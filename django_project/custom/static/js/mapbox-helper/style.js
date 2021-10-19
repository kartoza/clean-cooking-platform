function specs_set(fs, specs) {
    const criteria = [];
    for (let i = 0; i < fs.length; i += 1) {
        if (specs) {
            const c = {params: []};
            let p = false;

            for (let s of specs) {
                let m;

                const r = new RegExp(s.match);
                const v = fs[i].properties[s.key];

                if (!v) continue;

                const vs = v + "";

                if (vs === s.match || (m = vs.match(r))) {
                    c[s.key] = vs ? vs : m[1];

                    if (c.params.indexOf(s.key) < 0) c.params.push(s.key);

                    if (has(s, 'radius')) {
                        fs[i].properties['__radius'] = c['radius'] = s['radius'];
                    }

                    if (has(s, 'stroke')) {
                        fs[i].properties['__stroke'] = c['stroke'] = s['stroke'];
                    }

                    if (has(s, 'stroke-width')) {
                        fs[i].properties['__stroke-width'] = c['stroke-width'] = s['stroke-width'];
                    }

                    p = true;
                }
            }

            if (p && criteria.indexOf(JSON.stringify(c)) < 0)
                criteria.push(JSON.stringify(c));
        }
    }

    return criteria;
};


const parseStyle = async (sldStr) => {
    if (sldStr.includes('<UserLayer>')) {
        sldStr = sldStr.replace('<UserLayer>', '<sld:NamedLayer>');
        sldStr = sldStr.replace('</UserLayer>', '</sld:NamedLayer>');
    }
    let styleObject = await parser.readStyle(sldStr).then(styleObject => styleObject)
    let styleConfiguration = {};
    if (JSON.stringify(styleObject).includes('"kind":"Raster"')) {
        try {
            styleConfiguration = {
                intervals: [],
                color_stops: [],
                init: {
                    min: 0, max: 0
                },
                domain: {
                    min: 0, max: 0
                }
            }
            styleObject.rules[0].symbolizers[0].colorMap.colorMapEntries.forEach(function (item, index) {
                styleConfiguration.intervals.push(item.quantity);
                styleConfiguration.color_stops.push(item.color);
                if (item.quantity > styleConfiguration.init.max) {
                    styleConfiguration.init.max = item.quantity;
                    styleConfiguration.domain.max = item.quantity;
                }
                if (item.quantity < styleConfiguration.init.min) {
                    styleConfiguration.init.min = item.quantity;
                    styleConfiguration.domain.min = item.quantity;
                }
            })
        } catch (e) {
            console.log(e)
        }
    } else {
        if (JSON.stringify(styleObject).includes(('"kind":"Mark"'))) {
            styleConfiguration = {
                "fill": styleObject.rules[0].symbolizers[0].color,
                "width": styleObject.rules[0].symbolizers[0].radius,
                "opacity": 1,
                "shape_type": "points"
            }
        } else {
            let vectorConf = await mapboxParser.writeStyle(styleObject).then(mObj => mObj);
            let vectorConfObj = JSON.parse(vectorConf);
            vectorConfObj['shape_type'] = 'lines';
            styleConfiguration = {
                "attributes": [],
                "attributes_map": [],
                "features_specs": []
            };
            for (const layer of vectorConfObj.layers) {
                let filters = layer.filter;
                if (!styleConfiguration.attributes.includes(filters[1])) {
                    styleConfiguration.attributes.push(filters[1]);
                    styleConfiguration.attributes_map.push({
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
                styleConfiguration.features_specs.push(styleSpec)
            }
        }
    }
    return styleConfiguration;
}

