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

const clipSelectedLayerPromise = (boundary, layerId, drawToMap = true) => {
    return new Promise((resolve, reject) => {
        const url = '/api/clip-layer-by-region/';
        fetch(url, {
            method: 'POST',
            credentials: "same-origin",
            headers: {
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                boundary: boundary,
                layer_id: layerId
            })
        }).then((response) => response.json()).then(async data => {
            if (data['status'] === 'Pending') {
                setTimeout(async () => {
                    resolve(clipSelectedLayer(boundary, layerId, drawToMap));
                }, 1000)
            } else if (data['status'] === 'Success') {
                const output = data.output;
                if (drawToMap) {
                    if (output.includes('.json') > 0) {
                        await loadGeoJsonLayer(output, data.style_url, layerId);
                    } else if (output.includes('.tif') > 0) {
                        await loadGeoTiffLayer(output, data.style_url, layerId);
                    }
                }
                resolve("FINISH")
            } else {
                reject('Error clipping layer')
            }
        }).catch((error) => reject(error))
    })
}

const clipSelectedLayer = async (boundary, layerId, drawToMap = true) => {
    const url = '/api/clip-layer-by-region/';
    await fetch(url, {
        method: 'POST',
        credentials: "same-origin",
        headers: {
            'X-CSRFToken': csrfToken,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            boundary: boundary,
            layer_id: layerId
        })
    }).then((response) => response.json()).then(async data => {
        if (data['status'] === 'Pending') {
            setTimeout(async () => {
                await clipSelectedLayer(boundary, layerId, drawToMap);
            }, 1000)
        }
        else if (data['status'] === 'Success') {
            const output = data.output;
            if (drawToMap) {
                if (output.includes('.json') > 0) {
                    await loadGeoJsonLayer(output, data.style_url, layerId);
                } else if(output.includes('.tif') > 0) {
                    await loadGeoTiffLayer(output, data.style_url, layerId);
                }
            }
            console.log("FINISH")
        } else {
            console.error('Error clipping layer')
        }
    }).catch((error) => console.log(error))
}

(function () {
    const scenarioSelect = document.getElementById('scenarioSelect');
    const ccaToolBtn = document.getElementById('cca-tool-btn');
    const ccaReportBtn = document.getElementById('report-btn');
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
        const tasks = []
        for (let i = 0; i < selectedLayers.length; i++) {
            tasks.push(clipSelectedLayerPromise(boundary, selectedLayers[i], true));
        }
        for (let j = 0; j < allLayerIds.length; j++) {
            if (!selectedLayers.includes(allLayerIds[j])) {
                tasks.push(clipSelectedLayerPromise(boundary, allLayerIds[j], false));
            }
        }

        Promise.all(tasks).then(function(results){
            loadingSpinner1.style.display = "none";
            ccaToolBtn.disabled = false;
            ccaReportBtn.disabled = false;
        });
    }

    ccaToolBtn.onclick = (e) => {
        e.preventDefault();
        window.location.href = selectedScenario.dataset.url + '&boundary=' + boundary + '&geoId=' + geoId;
    }

    ccaReportBtn.onclick = (e) => {
        e.preventDefault();

        let url = '/generate-report-pdf/';
        let request = new XMLHttpRequest();
        let fd = new FormData();

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

        fd.append('geoId', geoId);
        fd.append('subRegion', subRegion);
        fd.append('mapImage', mapImage);

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
            }
        };

        request.send(fd);
    }
})()
