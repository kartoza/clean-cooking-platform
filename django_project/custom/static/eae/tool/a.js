import * as cards from './cards.js';

import * as controls from './controls.js';

import * as controlssearch from './controls-search.js';

import * as views from './views.js';

import * as indexes from './indexes.js';

import api_get from "./api.js";

import {
	init as timeline_init,
	lines_draw as timeline_lines_draw,
	filter_valued_polygons as timeline_filter_valued_polygons,
} from './timeline.js';

import {
	fit as mapbox_fit,
	init as mapbox_init,
	change_theme as mapbox_change_theme,
	pointer as mapbox_pointer,
	zoomend as mapbox_zoomend,
	dblclick as mapbox_dblclick,
} from './mapbox.js';

import {
	plot_active as analysis_plot_active,
} from './analysis.js';

import DS from './ds.js';

import Overlord from './overlord.js';
import {openactive} from "./controls-search.js";


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
			else v = i.split(',').filter(e => o.params.inputs.indexOf(e.replace(/ *\([^)]*\) */g, "").replace(/ *\[[^)]*] */g, "")) > -1);
			if (v.length > 0) {
				for (let j=0; j<v.length;j++) {
					if (v[j].includes('(') || v[j].includes('[')) {
						let value = v[j].replace(/ *\([^)]*\) */g, "");
						value = value.replace(/ *\[[^)]*] */g, "");

						let domainMatches = v[j].match(/ *\([^)]*\) */g);
						let weightMatches = v[j].match(/ *\[[^)]*] */g);

						if (DOMAIN_DATA.length === 0 || DOMAIN_DATA.find(o => o.name !== value)) {
							let domain = '';
							if (domainMatches) {
									domain = domainMatches[0].replace('(', '').replace(')', '').split(':');
									domain = {
										'min': domain[0],
										'max': domain[1]
									}
							}
							if (domain) {
								DOMAIN_DATA.push({
									'name': value,
									'domain': domain
								})
							}
						}

						if (WEIGHT_DATA.length === 0 || WEIGHT_DATA.find(o => o.name !== value)) {
							let weight = '';
							if (weightMatches) {
								weight = weightMatches[0].replace('[', '').replace(']', '');
							}
							if (weight) {
								WEIGHT_DATA.push({
									'name': value,
									'weight': weight
								})
							}
						}

						v[j] = value;
					}
				}
			}
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
			for (let i=0; i < v.length; i++) {
				let domain_data = DOMAIN_DATA.find(o => o.name === v[i].replace(/ *\[[^)]*] */g, ""));
				if (domain_data) {
					if (domain_data.domain) {
						v[i] += `(${domain_data.domain.min}:${domain_data.domain.max})`
					}
				}
				let weight_data = WEIGHT_DATA.find(o => o.name === v[i].replace(/ *\([^)]*\) */g, ""));
				if (weight_data) {
					if (weight_data.weight) {
						v[i] += `[${weight_data.weight}]`
					}
				}
			}
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

function layout() {
	if (maybe(GEOGRAPHY, 'timeline'))
		qs('#visual').append(ce('div', null, { id: 'timeline' }));

	const n = qs('nav');
	const p = qs('#playground');
	const w = qs('#mobile-switcher');

	const m = qs('#maparea', p);
	const b = qs('#mapbox-container', m);
	const v = qs('#views', m);
	const t = qs('#timeline');

	const l = qs('#left-pane', p);
	const d = qs('#drawer', p);
	const c = qs('#controls', p);

	const r = qs('#right-pane', p);

	function set_heights() {
		const h = window.innerHeight - n.clientHeight - (MOBILE ? w.clientHeight : 0);

		p.style['height'] =
      l.style['height'] =
      c.style['height'] =
      m.style['height'] =
      b.style['height'] =
      d.style['height'] =
      r.style['height'] = h + "px";

		b.style['height'] = (h - (MOBILE ? v.clientHeight : 0)) + "px";

		if (t) b.style['height'] = m.style['height'] = h - t.clientHeight + "px";
	};

	if (MOBILE) m.style['width'] = screen.width + "px";

	const oc = tmpl('#bottom-right-container-output-template');
	const gc = tmpl('#bottom-right-container-graphs-template');

	if (GEOGRAPHY.timeline) {
		qs('#filtered-pane').append(oc);
		qs('#cards-pane').append(gc);
	} else {
		qs('#cards-pane').append(oc);
	}

	document.body.onresize = set_heights;
	set_heights();
};

function mobile() {
	controlssearch.select_tab(qs('#controls-tab-all'), "all");

	for (let el of qsa('.controls-subbranch')) {
		elem_collapse(qs('.controls-container', el), el);
	}

	const switcher = qs('#mobile-switcher');

	const svgcontrols = ce('div', tmpl('#svg-controls'), { bind: 'controls', ripple: "" });
	const map = ce('div', tmpl('#svg-map'), { bind: 'map', ripple: "" });
	const inputs = ce('div', tmpl('#svg-list'), { bind: 'inputs', ripple: "" });
	const outputs = ce('div', tmpl('#svg-pie'), { bind: 'outputs', ripple: "" });

	const tabs = [svgcontrols, map, inputs, outputs];

	function mobile_switch(v) {
		switch (v) {
		case 'controls':{
			for (let e of ['#left-pane'])
				qs(e).style.display = '';

			for (let e of ['#right-pane', '#views'])
				qs(e).style.display = 'none';

			break;
		}

		case 'right': {
			for (let e of ['#left-pane'])
				qs(e).style.display = 'none';

			for (let e of ['#right-pane'])
				qs(e).style.display = '';

			break;
		}

		case 'outputs':
		case 'inputs': {
			for (let e of ['#left-pane'])
				qs(e).style.display = 'none';

			for (let e of ['#right-pane'])
				qs(e).style.display = '';

			U.view = v;

			views.right_pane();
			views.buttons();
			break;
		}

		case 'map':
		default: {
			for (let e of ['#right-pane', '#left-pane', '#views'])
				qs(e).style.display = 'none';

			for (let e of ['#views'])
				qs(e).style.display = '';

			break;
		}
		}
	};

	for (let e of tabs) {
		e.onclick = function(_) {
			for (let t of tabs) t.classList.remove('active');

			mobile_switch(this.getAttribute('bind'));
			e.classList.add('active');
		};

		switcher.append(e);
	}

	map.click();
};

function sidebarCollapseClicked() {
	let sidebarCollapse = document.getElementById('controls');
	let btn = document.getElementById('sidebarCollapseContainer');

	if (sidebarCollapse.style.marginLeft === "-550px") {
		sidebarCollapse.style.display = 'flex';
		setTimeout(() => {
    	sidebarCollapse.style.marginLeft = '0px';
			btn.style.left = '500px';
		}, 50)
  } else {
    sidebarCollapse.style.marginLeft = '-' + 550 + 'px';
		btn.style.left = '15px';
		setTimeout(() => {
    	sidebarCollapse.style.display = 'none';
		}, 300)
  }
	setTimeout(() => {
		MAPBOX.resize();
	}, 300)
}

export async function init() {
	const url = new URL(location);
	const id = url.searchParams.get('geo') || DEFAULT_GEO_ID;

	DOMAIN_DATA = [];
	WEIGHT_DATA = [];

	SIDEBAR = {
		sort_subbranches: [],
		sort_branches: []
	}

	GEOGRAPHY = await api_get(`/api/geography/?geo=${id}`);
	GEOGRAPHY.timeline = maybe(GEOGRAPHY, 'configuration', 'timeline');
	GEOGRAPHY.timeline_dates = maybe(GEOGRAPHY, 'configuration', 'timeline_dates');

	let params = 'default';

	if (GEOGRAPHY.timeline)
		params = 'timeline';

	MOBILE = screen.width < 1152;
	layout();

	U = new Proxy({ url: url, params: ea_params[params] }, UProxyHandler);
	O = new Overlord();

	MAPBOX = mapbox_init(O, U);

	try {
		await dsinit(GEOGRAPHY.id, U.inputs, U.pack, bounds => {
			MAPBOX.coords = mapbox_fit(bounds);
			mapbox_change_theme(ea_settings.mapbox_theme);

			let sidebarCollapse = qs('#sidebarCollapse', this);
			sidebarCollapse.onclick = sidebarCollapseClicked;

		});
	} catch (err) {
		console.log(err)
	}

	O.index = U.output;

	cards.init();
	controls.init();
	controlssearch.init();

	if (MOBILE) mobile();

	views.init();
	indexes.init();

	if (GEOGRAPHY.timeline) timeline_init();

	if (!MOBILE && !GEOGRAPHY.timeline) nanny_init();

	setTimeout(() => {
		controlssearch.openactive(U.inputs);
	}, 100)

	ea_loading(false);
};

/*
 * dsinit
 *
 * 1. fetch the datasets list from the API
 * 2. generate DS objects
 * 3. initialise mutants and collections
 *
 * @param "id" uuid
 * @param "inputs" string[] with DS.id's
 * @param "pack" string ("all" ...)
 * @param "callback" function to run with the boundaries
 *
 * returns DS[]
 */

async function dsinit(id, inputs, pack, callback) {
	let select = ["*", "category:categories(*)", "df:_datasets_files(*,file:files(*))"];

	let bounds;

	let boundary_url = `/api/boundaries-dataset/?geography=${id}`;
	if (boundary) {
		boundary_url += `&boundary=${boundary}`
	}
	const datasetBoundaries = await api_get(boundary_url)
	let ds = new DS(datasetBoundaries, false);
	// await ds.load('csv');
	await ds.load('vectors');
	await ds.load('raster');
	if (!(bounds = ds.vectors.bounds)) throw `'boundaries' dataset has no vectors.bounds`;
	const c = ds.config;
	if (c.column_name) {
		GEOGRAPHY.boundaries = {};

		for (let r of ds.csv.data)
			GEOGRAPHY.boundaries[r[c.column]] = r[c.column_name];
	}

	pack = maybe(pack, 'length') ? pack : 'all';

	let datasets_url = `/api/datasets/?geography=${id}`;
	if (boundary) {
		datasets_url += `&boundary=${boundary}`
	}
	await api_get(datasets_url)
		.then(async r => {
			return Promise.all(r.map(async e => {
				const branch_name = e.category.controls.path[0];
				const subbranch_name = e.category.controls.path[1];
				if (!SIDEBAR.sort_branches.includes(branch_name)) {
					SIDEBAR.sort_branches.push(branch_name)
				}
				if (!SIDEBAR.sort_subbranches.includes(subbranch_name)) {
					SIDEBAR.sort_subbranches.push(subbranch_name)
				}
				for (const item of e.df) {
					if (item.func === 'vectors' && item.file.geonode_layer && !boundary) {
						e.category.vectors = {
							specs: null,
							shape_type: 'lines',
							opacity: 1
						}
						continue
					}
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
							update_style(item.file.id, raster_configuration);
						} else {
							if (JSON.stringify(styleObject).includes(('"kind":"Mark"'))) { // points
								let pointConfiguration = {
								  "fill": styleObject.rules[0].symbolizers[0].color,
								  "width": styleObject.rules[0].symbolizers[0].radius,
								  "opacity": 1,
								  "shape_type": "points"
								}
								item.file.configuration = pointConfiguration;
								e.category.vectors = pointConfiguration;
							} else { // lines
								let vectorConf = await mapboxParser.writeStyle(styleObject).then(mObj => mObj)
								let vectorConfObj = JSON.parse(vectorConf);
								vectorConfObj['shape_type'] = 'lines';
								if (!e.category.vectors) {
									e.category.vectors = {
										specs: null,
										shape_type: vectorConfObj['shape_type'],
										opacity: 1
									}
								}
								e.category.vectors.specs = vectorConfObj.layers;
								item.file.configuration = e.category.vectors;
								if (!e.configuration) {
									let customVectorConfiguration = {
										"attributes": [],
										"attributes_map": [],
										"features_specs": [],
										"key": "fid"
									};
									for (const layer of vectorConfObj.layers) {
										if (layer.type === 'fill') {
											e.category.vectors.shape_type = 'polygons-fixed'
										}
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
									if (e.category.vectors.shape_type.match('polygons')) {
										if (vectorConfObj.layers.length > 0) {
											e.category.vectors.paint = vectorConfObj.layers[0].paint;
											e.category.vectors.stroke = vectorConfObj.layers[0].paint['fill-outline-color'];
											e.category.vectors.opacity = 1;
											e.category.vectors.fill = vectorConfObj.layers[0].paint['fill-color'];
										}
									} else {
										if (customVectorConfiguration.features_specs.length > 0)
											e.category.vectors.stroke = customVectorConfiguration.features_specs[0]['stroke']
									}
									e.configuration = customVectorConfiguration;
								}
							}
							update_style(item.file.id, {
								'vectors': e.category.vectors,
								'configuration': e.configuration
							});
						}
					}
				}
				return new DS(e, inputs.includes(e.category.name))
			}))
		});
	U.params.inputs = [...new Set(DS.array.map(e => e.id))];

	// We need all the datasets to be initialised _before_ setting
	// mutant/collection attributes (order is never guaranteed)
	//
	DS.array.filter(d => d.mutant).forEach(d => d.mutant_init());
	DS.array.filter(d => d.items).forEach(d => d.items_init());

	if (U.inputs.length > 0) {
		U.inputs.forEach(data => {
			let ds = DS.array.find(o => o.id === data);
			let domain_data = DOMAIN_DATA.find(o => o.name === data);
			if (domain_data) {
				ds._domain = domain_data.domain;
			}
			let weight_data = WEIGHT_DATA.find(o => o.name === data);
			if (weight_data && weight_data.weight) {
				ds.weight = parseInt(weight_data.weight);
				ds.controls.weight_group.change({'min': 1, 'max': ds.weight });
			}
		})
	}

	callback(bounds);
};

function update_style(dataset_id, style_data) {
	fetch('/api/style-api/', {
    	method: 'POST',
		headers: {
			'X-CSRFToken': csrfToken,
			'Accept': 'application/json',
			'Content-Type': 'application/json'
		},
    	body: JSON.stringify({
			'datasetId': dataset_id,
			'styleData': style_data
		})
	}).then(data => {
		console.log(data)
	});
}

function load_view() {
	const timeline = qs('#timeline');

	const {view, output, inputs} = U;

	function special_layers() {
		if (!MAPBOX.getSource('output-source')) {
			MAPBOX.addSource('output-source', {
				"type": 'canvas',
				"canvas": 'output',
				"animate": false,
				"coordinates": MAPBOX.coords
			});
		}

		if (!MAPBOX.getLayer('output-layer')) {
			MAPBOX.addLayer({
				"id": 'output-layer',
				"source": 'output-source',
				"type": 'raster',
				"layout": {
					"visibility": "none",
				},
				"paint": {
					"raster-resampling": "nearest",
				}
			}, MAPBOX.first_symbol);
		}

		if (!GEOGRAPHY.timeline) return;

		if (!MAPBOX.getSource('filtered-source')) {
			MAPBOX.addSource('filtered-source', {
				"type": 'geojson',
				"data": DST.get('boundaries').vectors.features
			});
		}

		if (!MAPBOX.getLayer('filtered-layer')) {
			MAPBOX.addLayer({
				"id": 'filtered-layer',
				"source": 'filtered-source',
				"type": 'fill',
				"layout": {
					"visibility": "none",
				},
				"paint": {
					"fill-color": "#0571B0",
					"fill-outline-color": "black",
					"fill-opacity": [ "case", [ "boolean", [ "get", "__hidden" ], false ], 0, 1 ]
				},
			}, MAPBOX.first_symbol);

			mapbox_dblclick('filtered-layer');
			mapbox_zoomend('filtered-layer');
		}
	};

	special_layers();

	switch (view) {
	case "outputs": {
		indexes.list();

		analysis_plot_active(output, true)
			.then(_ => {
				if (timeline) timeline.style.display = 'none';

				if (MAPBOX.getLayer('filtered-layer'))
					MAPBOX.setLayoutProperty('filtered-layer', 'visibility', 'none');

				MAPBOX.setLayoutProperty('output-layer', 'visibility', 'visible');
			});
		break;
	}

	case "inputs": {
		if (MAPBOX.getLayer('output-layer'))
			MAPBOX.setLayoutProperty('output-layer', 'visibility', 'none');

		cards.update(inputs);
		delay(1).then(O.sort); // TODO: remove/revisit this hack

		analysis_plot_active(output, false);

		break;
	}

	case "filtered": {
		if (timeline) timeline.style.display = 'none';

		MAPBOX.setLayoutProperty('filtered-layer', 'visibility', 'visible');
		MAPBOX.setLayoutProperty('output-layer', 'visibility', 'none');

		analysis_plot_active(output, true);

		timeline_filter_valued_polygons();
		break;
	}

	case "timeline": {
		if (timeline) timeline.style.display = '';

		MAPBOX.setLayoutProperty('filtered-layer', 'visibility', 'none');
		MAPBOX.setLayoutProperty('output-layer', 'visibility', 'none');

		cards.update(inputs);
		delay(1).then(O.sort); // TODO: remove/revisit this hack

		break;
	}

	default: {
		throw `Argument Error: Overlord: Could not set/find the view '${view}'.`;
	}
	}

	views.buttons();
	views.right_pane();
};

function map_click(e) {
	const {view, inputs, output} = U;

	const i = maybe(inputs, 0);

	let t;

	function feature_info(et, e) {
		let at = [];

		if (this.category.name === 'boundaries' ||
				this.category.name.match(/^(timeline-)?indicator/)) {
			at.push(["_boundaries_name", GEOGRAPHY.configuration.boundaries_name || "Geography Name"]);
			et.properties["_boundaries_name"] = GEOGRAPHY.boundaries[et.properties[this.vectors.key]];
		}

		if (this.config.column && this.category.name !== 'boundaries') {
			at.push(["_" + this.config.column, this.name]);
			et.properties["_" + this.config.column] = this.csv.table[et.properties[this.vectors.key]];
		}

		if (this.config.attributes_map) {
			at = at.concat(this.config.attributes_map.map(e => [e.dataset, e.target]));
		}

		let td = table_data(at, et.properties);

		table_add_lnglat(td, [e.lngLat.lng, e.lngLat.lat]);

		mapbox_pointer(
			td,
			e.originalEvent.pageX,
			e.originalEvent.pageY
		);
	};

	function vectors_click(callback) {
		const et = MAPBOX.queryRenderedFeatures(e.point)[0];
		if (!et) return;

		if (et.source === i) {
			if (typeof callback === 'function') callback(et);

			if (INFOMODE)
				feature_info.call(t, et, e);
		}
	};

	function raster_click() {
		if (!INFOMODE) return;

		const b = DST.get('boundaries');

		const rc = ea_coordinates_in_raster(
			[e.lngLat.lng, e.lngLat.lat],
			MAPBOX.coords,
			{
				data: t.raster.data,
				width: t.raster.width,
				height: t.raster.height,
				nodata: b.raster.nodata
			}
		);

		if (typeof maybe(rc, 'value') === 'number' &&
        rc.value !== t.raster.nodata) {
			const v = rc.value;

			const vv = (v%1 === 0) ? v : v.toFixed(2);

			const td = table_data([
				["value", t.name]
			], {
				"value": `${vv} <code>${t.category.unit || ''}</code>`
			});

			table_add_lnglat(td, [e.lngLat.lng, e.lngLat.lat]);

			mapbox_pointer(
				td,
				e.originalEvent.pageX,
				e.originalEvent.pageY
			);
		}
		else {
			console.log("No value (or nodata value) on raster.", rc);
		}
	};

	function analysis_click() {
		const b = DST.get('boundaries');

		const o = ea_coordinates_in_raster(
			[e.lngLat.lng, e.lngLat.lat],
			MAPBOX.coords,
			{
				data: t.raster.data,
				width: b.raster.width,
				height: b.raster.height,
				nodata: -1
			}
		);

		if (typeof maybe(o, 'value') === 'number') {
			let f = d3.scaleQuantize().domain([0,1]).range(["Low", "Low-Medium", "Medium", "Medium-High", "High"]);

			const dict = [
				["aname", t.name],
				["_empty", null]
			];

			const props = {
				"aname": f(o.value),
				"_empty": ""
			};

			DS.array
				.filter(d => d.on)
				.forEach(d => {
					if (d.datatype === 'raster') {
						dict.push([d.id, d.name]);
						let value = d.raster.data[o.index];
						props[d.id] = value.toFixed(2) + " " + d.category.unit;
					}

					else if (d.config.column && d.category.name !== 'boundaries') {
						dict.push(["_" + d.config.column, d.name]);
						props["_" + d.config.column] = d.csv.table[d.raster.data[o.index]] + " " + d.category.unit;
					}

					else if (d.raster) {
						dict.push([d.id, d.name]);
						let defaultUnit = 'meters';
						let value = d.raster.data[o.index];
						if(d.category.unit) {
							defaultUnit = d.category.unit;
						}
						if (defaultUnit === 'meters') {
							value = value / 1000;
							defaultUnit = 'km';
						}
						value = value.toFixed(2)
						props[d.id] = value + " " + defaultUnit + " (proximity to)";
					}
				});

			let td = table_data(dict, props);

			table_add_lnglat(td, [e.lngLat.lng, e.lngLat.lat]);

			mapbox_pointer(
				td,
				e.originalEvent.pageX,
				e.originalEvent.pageY
			);
		}

		else {
			console.log("No value on raster.", o);
		}
	};

	if (view === "outputs") {
		if (!INFOMODE) return;

		t = {
			raster: {
				data: MAPBOX.getSource('output-source').raster
			},
			category: {},
			name: ea_indexes[output]['name']
		};

		analysis_click();
	}

	else if (view === "inputs") {
		t  = DST.get(i);

		if (!t) return;

		if (t.vectors) vectors_click();

		else if (t.raster.data) raster_click();
	}

	else if (view === "timeline") {
		t  = DST.get(i);

		if (!t) return;

		if (t.vectors) vectors_click(p => {
			if (p.properties['District']) U.subgeoname = p.properties['District'];
			timeline_lines_draw();
		});

		else if (t.raster.data) raster_click();
	}
};

function nanny_init() {
	window.ea_nanny = new nanny(ea_nanny_steps);

	if (![null, "inputs"].includes(U.view)) return;
	if (U.inputs.length > 0) return;

	const w = localStorage.getItem('needs-nanny');
	if (!w || !w.match(/false/)) ea_nanny.start();
};

function nanny_force() {
	U.params = {
		inputs: [],
		output: 'eai',
		view: 'inputs'
	};

	DS.array.filter(d => d.on).forEach(d => d.active(false, false));

	O.view = 'inputs';
	// controlssearch.select_tab(qs('#controls-tab-census'), "census");
	ea_modal.hide();

	O.view = U.view;

	ea_nanny.start();
};

// TODO: used in an onclick attribute
window.ea_nanny_force_start = nanny_force;

// TODO: the following are used by overlord. delete them.
window.load_view = load_view;
window.map_click = map_click;
