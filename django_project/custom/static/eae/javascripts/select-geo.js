import api_get from "/static/eae/tool/api.js";

function topo_flag(features, flagurl, config) {
	const width = MOBILE ? 100 : 200;
	const padding = 1;

	const id = flagurl.substr(flagurl.length - 12);

	const svg = d3.select(document.createElementNS("http://www.w3.org/2000/svg", "svg"))
		    .attr('width', width)
		    .attr('height', width);

	const geopath = d3.geoPath()
		    .projection(d3.geoMercator());

	svg.append('defs')
		.append('pattern')
		.attr('id', `flag-${id}`)
		.attr('patternUnits', 'objectBoundingBox')
		.attr('x', 0)
		.attr('y', 0)
		.attr('width', 1)
		.attr('height', 1)

		.append('image')
		.attr('href', flagurl)
		.attr('x', config['x'] || 0)
		.attr('y', config['y'] || 0)
		.attr('width', config['width'])
		.attr('height', config['height']);

	const g = svg.append('g');

	Whatever.then(_ => {
		const path = g.selectAll(`path`)
			    .data(features)
			    .enter().append('path')
			    .attr('fill', `url(#flag-${id})`)
			    .attr('d', geopath);

		const box = path.node().getBBox();
		const s = (box.height > box.width) ? (box.height - box.width)/2 : 0;

		const factor = Math.min(
			width / (box.width + (padding * 2)),
			width / (box.height + (padding * 2))
		);

		g.attr('transform', `scale(${factor})translate(${(-box.x + padding + s)}, ${(-box.y + padding)})`);

		URL.revokeObjectURL(flagurl);
	});


	return svg.node();
};

async function geography(c) {
	console.log(c)
	const coll = await api_get(`/api/geography-list/?geo=` + c.id);

	const data = {};
	for (let x of coll) data[x.name] = x.name;

	const sl = new selectlist(`geographies-select-` + c.id, data, {
		'change': function(_) {
			const x = coll.find(x => x.name === this.value);
			if (x) location = location = `/tool/?geo=${x.id}`;
		}
	});

	if (coll.length === 0) {
		location = `/tool/?geo=${c.id}`;
		return;
	}

	let content = ce('div');
	content.append(
		ce('p', `We have several geographies for ${c.name}. Please do select one.`),
		sl.el
	);

	ea_modal.set({
		header: c.name,
		content: content,
		footer: null
	}).show();

	sl.input.focus();
};

export function init() {
	const playground = qs('#playground');

	MOBILE = window.innerWidth < 1152;

	function hextostring(hex) {
		var s = "";

		//             ________________ careful there
		//            /
		//           V
		for (let i = 2; i < hex.length; i += 2)
			s += String.fromCharCode(parseInt(hex.substr(i, 2), 16));

		return s;
	};

	api_get('/api/geography-list/')
		.then(countries_online => {
			for (let co of countries_online) {
				const d = ce('div', ce('h2', co.name, { class: 'country-name' }), { class: 'country-item', ripple: "" });
				d.onclick = _ => setTimeout(_ => geography(co), 350);

				if (co.icon) {
					console.log(co.icon)
				}

				const imgContainer = ce('div', '', { class: 'img-container'});
				d.prepend(imgContainer);
				imgContainer.append(ce('img', '', { 'src': co.icon, 'class': 'geography-img' }));

				playground.append(d);
			}

			ea_loading(false);
		})
		.catch(error => {
			ea_flash.push({
				type: 'error',
				title: "Fetch error",
				message: error
			});

			throw error;
		});
};
