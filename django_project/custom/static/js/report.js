let addedLayers = [];
let rasterBoundaryLayer = null;
const loadingSpinner1 = document.getElementById('loading-spinner-1');

MAPBOX = new mapboxgl.Map({
    container: 'map', // container ID
    style: mapboxStyle,
    center: [0, 0], // starting position [lng, lat]
    zoom: 2, // starting zoom
    preserveDrawingBuffer: true
});
MAPBOX.first_symbol = 'poi_label';

let rasterToAnalyse = null;

const fetchRasterBoundary = async () => {
    await fetch(rasterBoundary).then(response => response.arrayBuffer()).then(
        data => {
            rasterBoundaryLayer = data
        }
    )
}

fetch(geojsonBoundary).then(response => response.json()).then(
    async data => {
        MAPBOX.on('load', async () => {
            MAPBOX.addSource('boundary', {
                type: 'geojson',
                data: data
            });
            MAPBOX.addLayer({
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
            MAPBOX.coords = coords;
            MAPBOX.fitBounds(bbox, {padding: 20});
            await fetchRasterBoundary();
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

const loadGeoTiffLayer = async (url, styleUrl, layerId) => {
    await fetchSLD('/proxy_cca/' + styleUrl).then(async styleData => {
        await fetch(url).then(
            response => response.blob()
        ).then(async blob => {
            const tiff = await GeoTIFF.fromBlob(blob);
            const image = await tiff.getImage();
            const bands = await image.readRasters();
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
            addedLayers.push(layerId);
            MAPBOX.addSource('source' + layerId, {
                "type": "canvas",
                "canvas": canvas,
                "animate": false,
                "coordinates": coords
            });
            MAPBOX.addLayer({
                'id': 'layer' + layerId,
                "type": 'raster',
                'source': 'source' + layerId,
                "layout": {
                    "visibility": "visible",
                },
                "paint": {
                    "raster-resampling": "nearest"
                }
            });
            rasterToAnalyse = MAPBOX.getLayer('layer' + layerId);
        })
    });
}

const loadGeoJsonLayer = async (url, styleUrl, layerId) => {
    await fetchSLD('/proxy_cca/' + styleUrl).then(async styleData => {
        await fetch(url).then(response => response.json()).then(
            data => {
                const criteria = specs_set.call(
                    this,
                    data.features,
                    styleData.features_specs,
                );
                addedLayers.push(layerId);
                MAPBOX.addSource('source' + layerId, {
                    type: 'geojson',
                    data: data
                });
                MAPBOX.addLayer({
                    'id': 'layer' + layerId,
                    'type': 'line',
                    'source': 'source' + layerId,
                    'paint': {
                        "line-color": ['get', '__stroke'],
                        "line-width": ['get', '__stroke-width'],
                    }
                });
            });
    });
}

const clipSelectedLayer = async (boundary, layerId, drawToMap = true) => {
    const url = '/api/clip-layer-by-region/';
    await fetch(url, {
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
    }).then((response) => response.json()).then(async data => {
        const output = data.output;
        if (drawToMap) {
            if (output.includes('.json') > 0) {
                await loadGeoJsonLayer(output, data.style_url, layerId);
            } else if(output.includes('.tif') > 0) {
                await loadGeoTiffLayer(output, data.style_url, layerId);
            }
        }
    }).catch((error) => console.log(error))
}

(function () {
    const scenarioSelect = document.getElementById('scenarioSelect');
    const ccaToolBtn = document.getElementById('cca-tool-btn');
    let selectedScenario = null;
    let selectedLayers = null;

    scenarioSelect.onchange = async (e) => {
        ccaToolBtn.disabled = true;
        loadingSpinner1.style.display = "block";
        selectedScenario = e.target.options[e.target.selectedIndex];
        selectedLayers = JSON.parse(selectedScenario.dataset.layers);
        if (addedLayers.length > 0) {
            for (let i = 0; i < addedLayers.length; i++) {
                const addedLayer = addedLayers[i];
                MAPBOX.removeLayer('layer' + addedLayer);
                MAPBOX.removeSource('source' + addedLayer);
            }
            addedLayers = [];
        }
        if (selectedLayers.length > 0) {
            selectedLayers.reverse();
        }
        for (let i = 0; i < selectedLayers.length; i++) {
            await clipSelectedLayer(boundary, selectedLayers[i], true);
        }
        for (let j = 0; j < allLayerIds.length; j++) {
            if (!selectedLayers.includes(allLayerIds[j])) {
                await clipSelectedLayer(boundary, allLayerIds[j], false);
            }
        }
        loadingSpinner1.style.display = "none";
        ccaToolBtn.disabled = false;
    }

    ccaToolBtn.onclick = (e) => {
        e.preventDefault();
        window.location.href = selectedScenario.dataset.url + '&boundary=' + boundary + '&geoId=' + geoId;
    }
})()

// d340760a-5be9-3a93-b4f2-077f7ecd3d30 33
// d340760a-5be9-3a93-b4f2-077f7ecd3d30 32
// d340760a-5be9-3a93-b4f2-077f7ecd3d30 31
const loadTestLayers = async () => {
    // await clipSelectedLayer(boundary, 32, true)
}
