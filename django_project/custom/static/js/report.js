
const map = new mapboxgl.Map({
    container: 'map', // container ID
    style: mapboxStyle,
    center: [0, 0], // starting position [lng, lat]
    zoom: 2 // starting zoom
});

fetch(geojsonBoundary).then(response => response.json()).then(
    data => {
        map.on('load', () => {
            map.addSource('boundary', {
                type: 'geojson',
                data: data
            });
            map.addLayer({
                'id': 'boundary-layer',
                'type': 'line',
                'source': 'boundary',
                'paint': {
                    'line-width': 2,
                    'line-color': 'red'
                }
            });
            bbox = turf.extent(data);
            const l = bbox[0];
            const r = bbox[2];
            const d = bbox[1];
            const u = bbox[3];
            coords = [[l, u], [r, u], [r, d], [l, d]];
            map.fitBounds(bbox, {padding: 20});
        });
    }
)

const fetchSLD = (url) => {
    return new Promise((resolve, reject) => {
        fetch(url).then(response => response.text()).then(
            async data => {
                const styleObj = await parseStyle(data);
                resolve(styleObj)
            }
        )
    })
}

const loadGeoTiffLayer = (url, styleUrl, layerId) => {
    fetchSLD('/proxy_cca/' + styleUrl).then(styleData => {
        fetch(url).then(
            response => response.arrayBuffer()
        ).then(data => {
            const tiff = GeoTIFF.parse(data);
            const image = tiff.getImage();
            const bands = image.readRasters();
            const band = bands[0];
            const width = image.getWidth();
            const height = image.getHeight();
            const nodata = parseFloat(image.fileDirectory.GDAL_NODATA);
            const canvas = drawcanvas({
                canvas: ce('canvas'),
                data: band,
                width: width,
                height: height,
                nodata: nodata,
                colorscale: ea_colorscale({
                    stops: styleData.color_stops,
                    domain: styleData.domain,
                    intervals: styleData.intervals
                })
            });
            map.addSource('boundary' + layerId, {
                "type": "canvas",
                "canvas": canvas,
                "animate": false,
                "coordinates": coords
            });
            map.addLayer({
                'id': 'layer' + layerId,
                "type": 'raster',
                'source': 'boundary' + layerId,
                "layout": {
                    "visibility": "visible",
                },
                "paint": {
                    "raster-resampling": "nearest"
                }
            });
        })
    });
}

const loadGeoJsonLayer = (url, styleUrl, layerId) => {
    fetchSLD('/proxy_cca/' + styleUrl).then(styleData => {
        fetch(url).then(response => response.json()).then(
            data => {
                const criteria = specs_set.call(
                    this,
                    data.features,
                    styleData.features_specs,
                );
                map.addSource('boundary' + layerId, {
                    type: 'geojson',
                    data: data
                });
                map.addLayer({
                    'id': 'layer' + layerId,
                    'type': 'line',
                    'source': 'boundary' + layerId,
                    'paint': {
                        "line-color": ['get', '__stroke'],
                        "line-width": ['get', '__stroke-width'],
                    }
                });
            });
    });
}

const clipSelectedLayer = (boundary, layerId) => {
    const url = '/api/clip-layer-by-region/';
    fetch(url, {
        method: 'POST',
        credentials: "same-origin",
        headers: {
            'X-CSRFToken': getCookie("csrftoken"),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            boundary: boundary,
            layer_id: layerId
        })
    }).then((response) => response.json()).then(data => {
        const output = data.output;
        if (output.includes('.json') > 0) {
            loadGeoJsonLayer(output, data.style_url, layerId);
        } else if(output.includes('.tif') > 0) {
            loadGeoTiffLayer(output, data.style_url, layerId);
        }
    }).catch((error) => console.log(error))
}

(function () {
    const scenarioSelect = document.getElementById('scenarioSelect');
    const ccaToolBtn = document.getElementById('cca-tool-btn');
    let selectedScenario = null;
    let selectedLayers = null;

    scenarioSelect.onchange = (e) => {
        ccaToolBtn.disabled = false;
        selectedScenario = e.target.options[e.target.selectedIndex];
        selectedLayers = JSON.parse(selectedScenario.dataset.layers);
        for (let i = 0; i < selectedLayers.length; i++) {
            clipSelectedLayer(boundary, selectedLayers[i]);
        }
    }

    ccaToolBtn.onclick = (e) => {
        e.preventDefault();
        window.location.href = selectedScenario.dataset.url + '&boundary=' + boundary;
    }
})()