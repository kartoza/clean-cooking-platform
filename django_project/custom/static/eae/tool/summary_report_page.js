import api_get from "./api.js";
import DS from "./ds.js";
import Overlord from "./overlord.js";
import run, {
	plot_active as analysis_plot_active,
	raster_to_tiff
} from "./analysis.js";
import analyse from './summary.js';
import * as plot from "./plot.js";
import {
	change_theme as mapbox_change_theme,
	fit as mapbox_fit
} from "./mapbox";
import {downloadReport} from "./download_report";
const ea_nanny_steps = [];
const raster_data = {};
let addedLayers = [];

function nanny_init() {
	window.ea_nanny = new nanny(ea_nanny_steps);

	if (![null, "inputs"].includes(U.view)) return;
	if (U.inputs.length > 0) return;

	const w = localStorage.getItem('needs-nanny');
	if (!w || !w.match(/false/)) ea_nanny.start();
}

const UProxyHandler = {
	get: function(o,p) {
		const i = o.url.searchParams.get(p);

		let v;
		switch (p) {
		case "params": {
			v = o.params;
			break;
		}

		case "inputs": {
			if (!i || i === "") v = [];
			else v = i.split(',').filter(e => o.params.inputs.indexOf(e) > -1);
			break;
		}

		default: {
			v = (i === "" ? null : i);
			break;
		}
		}

		return v;
	},

	set: function(o,t,v) {
		switch (t) {
		case "output":
		case "view": {
			if (!o.params[t].includes(v)) v = o.params[t][0];
			o.url.searchParams.set(t,v);
			break;
		}

		case "timeline": {
			o.url.searchParams.set(t, v || GEOGRAPHY.timeline_dates.slice(-1)[0]);
			break;
		}

		case "subgeo":
		case "subgeoname":
		case "pack": {
			o.url.searchParams.set(t,v);
			break;
		}

		case "inputs": {
			o.url.searchParams.set(t, [...new Set(v)]);
			break;
		}

		case "params": {
			for (let p in v) {
				if (!o.params[p].includes(v[p])) continue;
				o.url.searchParams.set(p, v[p]);
			}
			break;
		}

		default: {
			throw TypeError(`U: I'm not allowed to set '${t}'`);
		}
		}

		history.replaceState(null, null, o.url);

		return true;
	}
};

function init_template() {
	const oc = tmpl('#bottom-right-container-output-template');
	qs('#cards-pane').append(oc);
}

export async function init() {

	const map = ce('div', tmpl('#svg-map'), { bind: 'map', ripple: "" });
	const outputs = ce('div', tmpl('#svg-pie'), { bind: 'outputs', ripple: "" });

	const url = new URL(location);
	const geoId = url.searchParams.get('geoId');
	const boundary = url.searchParams.get('boundary');
	let params = 'default';

	GEOGRAPHY = await api_get(`/api/geography/?geo=${geoId}`);

	U = new Proxy({ url: url, params: ea_params[params] }, UProxyHandler);
	O = new Overlord();

	const inputs = U.inputs;
	nanny_init();
	let boundary_url = `/api/boundaries-dataset/?geography=${geoId}`;
	if (boundary) {
		boundary_url += `&boundary=${boundary}`
	}
	const datasetBoundaries = await api_get(boundary_url)
	let ds = new DS(datasetBoundaries, false);
	if (!boundary) {
		await ds.load('vectors');
		MAPBOX.coords = convertBounds(ds.vectors.bounds);
	}
};

export async function getDatasets(inputs, scenarioId, analysisType = []) {

	let datasets_url = `/api/datasets/?geography=${geoId}`;
	if (boundary) {
		datasets_url += `&boundary=${boundary}`
	}
	if (inputs) {
		if (!inputs.includes('population-density')) {
			let inputList = inputs.split(',');
			inputList.unshift('population-density');
			inputs = inputList.join(',');
		}
		datasets_url += `&inputs=${inputs}`;
	}

	DST.forEach((value, key) => {
		if (key !== 'boundaries') {
			DST.delete(key);
		}
	})

	if (addedLayers.length > 0) {
		for (let i = 0; i < addedLayers.length; i++) {
			const addedLayer = addedLayers[i];
			try {
				MAPBOX.removeLayer(addedLayer);
				MAPBOX.removeSource(addedLayer);
			} catch (e) {
				console.log(e)
			}
		}
		addedLayers = [];
	}

	await api_get(datasets_url)
		.then(async r => {
			return Promise.all(r.map(async e => {
				for (const item of e.df) {
					if (item.file.style) {
						let raster_configuration = {
							"init": {
								"max": 0,
								"min": 0
							},
							"scale": "intervals",
							"domain": {
								"max": 0,
								"min": 0
							},
							"factor": 1,
							"intervals": [],
							"precision": 0,
							"color_stops": []
						};

						let sldUrl = `/api/style-api/?datasetId=${item.file.id}&styleUrl=${item.file.style}`;
						let isSldData = true;
						let sldStr = '';
						let mapboxStyleData = null;
						await fetch(sldUrl).then(response => {
							const contentType = response.headers.get("content-type");
							if (contentType && contentType.indexOf("application/json") !== -1) {
								return response.json().then(data => {
									// process your JSON data further
									isSldData = false;
									mapboxStyleData = data;
									return data;
								});
							} else {
								return response.text().then(text => {
									// this is text, do something with it
									isSldData = true;
									sldStr = text;
									return text;
								});
							}
						});

						if (mapboxStyleData) {
							try {
								if (mapboxStyleData.hasOwnProperty('color_stops')) {
									e.category.domain = mapboxStyleData.domain;
									e.category.colorstops = mapboxStyleData.color_stops;
									e.category.analysis.intervals = mapboxStyleData.intervals;
									e.category.raster = mapboxStyleData;
									item.file.configuration = mapboxStyleData;
								} else {
									if (mapboxStyleData.hasOwnProperty('vectors')) {
										item.file.configuration = mapboxStyleData.vectors;
										e.category.vectors = mapboxStyleData.vectors;
										e.configuration = mapboxStyleData.configuration;
									}

								}
							} catch (e) {
								console.error(e)
							}
							continue;
						}

						if (sldStr.includes('<UserLayer>')) {
							sldStr = sldStr.replace('<UserLayer>', '<sld:NamedLayer>');
							sldStr = sldStr.replace('</UserLayer>', '</sld:NamedLayer>');
						}

						let styleObject = await parser.readStyle(sldStr).then(styleObject => styleObject)
						if (JSON.stringify(styleObject).includes('"kind":"Raster"')) {
							try {
								styleObject.rules[0].symbolizers[0].colorMap.colorMapEntries.forEach(function (item, index) {
									raster_configuration.intervals.push(item.quantity);
									raster_configuration.color_stops.push(item.color);
									if (item.quantity > raster_configuration.init.max) {
										raster_configuration.init.max = item.quantity;
										raster_configuration.domain.max = item.quantity;
									}
									if (item.quantity < raster_configuration.init.min) {
										raster_configuration.init.min = item.quantity;
										raster_configuration.domain.min = item.quantity;
									}
									if (index === styleObject.rules[0].symbolizers[0].colorMap.colorMapEntries.length - 1) {
										if (item.label) {
											let legends = item.label.split('-');
											if (legends.length > 1) {
												let legend = legends[1].trim();
												if (parseFloat(legend) > raster_configuration.domain.max) {
													raster_configuration.domain.max = parseFloat(legend);
													raster_configuration.init.max = parseFloat(legend);
												}
											}
										}
									}
								})
							} catch (e) {
								console.log(e)
							}
							e.category.domain = raster_configuration.domain;
							e.category.colorstops = raster_configuration.color_stops;
							e.category.analysis.intervals = raster_configuration.intervals;
							e.category.raster = raster_configuration;
							item.file.configuration = raster_configuration;
						} else {
							if (JSON.stringify(styleObject).includes(('"kind":"Mark"'))) {
								let pointConfiguration = {
								  "fill": styleObject.rules[0].symbolizers[0].color,
								  "width": styleObject.rules[0].symbolizers[0].radius,
								  "opacity": 1,
								  "shape_type": "points"
								}
								item.file.configuration = pointConfiguration;
								e.category.vectors = pointConfiguration;
							} else {
								let vectorConf = await mapboxParser.writeStyle(styleObject).then(mObj => mObj)
								let vectorConfObj = JSON.parse(vectorConf);
								vectorConfObj['shape_type'] = 'lines';
								item.file.configuration = vectorConfObj
								if (!e.category.vectors) {
									e.category.vectors = {
										specs: null,
										shape_type: vectorConfObj['shape_type'],
										opacity: 1
									}
								}
								e.category.vectors.specs = vectorConfObj.layers;
								if (!e.configuration) {
									let customVectorConfiguration = {
										"attributes": [],
										"attributes_map": [],
										"features_specs": []
									};
									for (const layer of vectorConfObj.layers) {
										let filters = layer.filter;
										let styleSpec = {};
										if (filters) {
											if (!customVectorConfiguration.attributes.includes(filters[1])) {
												customVectorConfiguration.attributes.push(filters[1]);
												customVectorConfiguration.attributes_map.push({
													'target': filters[1],
													'dataset': filters[1]
												})
											}
											let key = filters[1];
											if (key.length > 1) {
												key = key[1];
											}

											if (layer.type === 'fill') {
												styleSpec = {
													"key": key,
													"match": filters[1],
												}
											} else {
												styleSpec = {
													"key": filters[1],
													"match": filters[2],
												}
											}
											if (filters.length > 2) {
												styleSpec["match_2"] = filters[2]
											}
										}
										if ('line-color' in layer.paint) {
											styleSpec['stroke'] = layer.paint['line-color']
										}
										if ('line-width' in layer.paint) {
											styleSpec['stroke-width'] = layer.paint['line-width']
										}
										if ('fill-color' in layer.paint) {
											styleSpec['fill'] = layer.paint['fill-color']
										}
										if ('fill-outline-color' in layer.paint) {
											styleSpec['stroke'] = layer.paint['fill-outline-color']
										}
										customVectorConfiguration.features_specs.push(styleSpec)
									}
									e.configuration = customVectorConfiguration;
								}
							}
						}
					}
				}
				return new DS(e, inputs.includes(e.category.name))
			}))
		});
	// U.params.inputs = [...new Set(DS.array.map(e => e.id))];
	init_template();
	const inputList = inputs.split(',').reverse();
	for (const [key, value] of DST.entries()) {
	 	await DST.get(key)._active(false, false);
	}
	await DST.get('boundaries')._active(true, false);
	for (let i = 0; i < inputList.length; i++) {
		try {
			if (typeof MAPBOX.getSource(inputList[i]) === 'undefined') {
				await DST.get(inputList[i]).active(true, true);
				addedLayers.push(inputList[i]);
			}
		} catch (e) {
			debugger;
			console.log(e);
		}
	}

	// Wait for seconds
	setTimeout(() => {
		document.getElementById('loading-spinner-0').style.display = 'none';
		document.getElementById('summary-button').disabled = false;
		progressBar.style.width = '100%';
	}, 500)
}

window.getDatasets = getDatasets;

document.getElementById('summary-button').onclick = async (e) => {
	e.preventDefault();

	const scenarioSelect = document.getElementById('scenarioSelect');

	PRESET_ID = scenarioSelect.value;
	USE_CASE_ID = useCaseId;
	PRESET_NAME = scenarioSelect.options[scenarioSelect.selectedIndex].text;

	await downloadReport(800, 600);
}

export function convertBounds(bounds) {

	const l = bounds[0];
	const r = bounds[2];
	const d = bounds[1];
	const u = bounds[3];

	return [[l,u], [r,u], [r,d], [l,d]];
}
