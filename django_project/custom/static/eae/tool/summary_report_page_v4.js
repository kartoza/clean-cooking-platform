import api_get from "./api.js";
import DS from "./ds.js";
import Overlord from "./overlord.js";
import run, {plot_active as analysis_plot_active} from "./analysis.js";
import analyse from './summary.js';
import * as plot from "./plot.js";
const ea_nanny_steps = [];

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

};

async function run_analysis (output) {
	const raster = run(output);
	const data = await analyse(raster);
	plot.outputcanvas(raster, qs(`canvas#${output}-output`));
	return data;
};

export async function getDatasets(inputs) {

	let datasets_url = `/api/datasets/?geography=${geoId}`;
	if (boundary) {
		datasets_url += `&boundary=${boundary}`
	}
	if (inputs) {
		datasets_url += `&inputs=${inputs}`;
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
						let sldStr = await fetch(item.file.style).then(response => response.text()).then(str => str);

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
										if (!customVectorConfiguration.attributes.includes(filters[1])) {
											customVectorConfiguration.attributes.push(filters[1]);
											customVectorConfiguration.attributes_map.push({
												'target': filters[1],
												'dataset': filters[1]
											})
										}
										const styleSpec = {
											"key": filters[1],
											"match": filters[2],
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
			await DST.get(inputList[i])._active(true, true);
		} catch (e) {
			console.log(e);
		}
	}
	// await run_analysis("eai");
	window.supplyData = await run_analysis("supply");
	window.demandData = await run_analysis("demand");
	// await run_analysis("ani");

	document.getElementById('loading-spinner-0').style.display = 'none';
	document.getElementById('report-btn').disabled = false;
}

document.getElementById('report-btn').onclick = async (e) => {
	e.preventDefault();

	let buttonText = document.getElementById('report-btn-text');
	let button = document.getElementById('report-btn');
	button.disabled = true;
	buttonText.innerHTML = 'Generating...'

	let url = '/generate-report-pdf/';
	let request = new XMLHttpRequest();
	let fd = new FormData();

	MAPBOX.fitBounds(BBOX, {padding: 20, duration: 0});
	await new Promise(r => setTimeout(r, 500));

	let mapCanvas = document.getElementsByClassName('mapboxgl-canvas')[0];

	let width = 800;
	let height = 600;
	const canvas = document.getElementById('output');
	const ctx = canvas.getContext("2d");

	canvas.width = width;
	canvas.height = height;
	ctx.drawImage(mapCanvas,
		(mapCanvas.width / 2) - (width / 2),0,
		width, height,
		0,0,
		width, height
	);
	let mapImage = canvas.toDataURL('image/png', 1.0);

	let demandImage = document.getElementById('demand-output').toDataURL('image/png', 1.0);
	let supplyImage = document.getElementById('supply-output').toDataURL('image/png', 1.0);

	fd.append('geoId', geoId);
	fd.append('subRegion', subRegion);
	fd.append('mapImage', mapImage);
	fd.append('demandImage', demandImage);
	fd.append('supplyImage', supplyImage);
	fd.append('useCaseId', useCaseId);
	fd.append('scenarioId', document.getElementById('scenarioSelect').value);

	try {
		fd.append('supplyDataHighPercentage', (window.supplyData['population-density']['distribution'][4] * 100).toFixed(2))
		fd.append('totalPopulation', Math.round(window.supplyData['population-density']['total']))
	} catch (e) {}

	try {
		fd.append('demandDataHighPercentage', (window.demandData['population-density']['distribution'][4] * 100).toFixed(2))
	} catch (e) {}

	request.open('POST', url, true);
	request.setRequestHeader('X-CSRFToken', csrfToken);
	request.responseType = 'blob';

	request.onload = function () {
		// Only handle status code 200
		if (request.status === 200) {
			// Try to find out the filename from the content disposition `filename` value
			let disposition = request.getResponseHeader('content-disposition');
			let matches = /"([^"]*)"/.exec(disposition);
			let filename = (matches != null && matches[1] ? matches[1] : 'Report.pdf');

			// The actual download
			let blob = new Blob([request.response], {type: 'application/pdf'});
			let link = document.createElement('a');
			link.href = window.URL.createObjectURL(blob);
			link.download = filename;

			document.body.appendChild(link);

			link.click();

			document.body.removeChild(link);

			button.disabled = false;
			buttonText.innerHTML = 'Clean Cooking Access Report'
		}
	};

	request.send(fd);
}