let rasterBoundaryLayer = null;
const loadingSpinner1 = document.getElementById('loading-spinner-1');
const loadingSpinner0 = document.getElementById('loading-spinner-0');
const progressBar = document.getElementById('progress-bar');
const presetDesc = document.getElementById('preset-desc');
let clippingProgress = 0;
let doneLayer = 0;

MAPBOX = new mapboxgl.Map({
    container: 'map', // container ID
    style: mapboxStyle,
    center: [0, 0], // starting position [lng, lat]
    zoom: 2, // starting zoom
    preserveDrawingBuffer: true
});
MAPBOX.first_symbol = 'poi_label';

const fetchRasterBoundary = async () => {
    await fetch(rasterBoundary).then(response => response.arrayBuffer()).then(
        data => {
            rasterBoundaryLayer = data
        }
    )
}

if (boundary) {
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
                BBOX = bbox;
                await fetchRasterBoundary();
            });
        }
    )
} else {
    const bbox = bboxString.split(',');
    let bbox_1 = proj4("EPSG:3857", "EPSG:4326").forward([parseFloat(bbox[0]), parseFloat(bbox[1])]);
    let bbox_2 = proj4("EPSG:3857", "EPSG:4326").forward([parseFloat(bbox[2]), parseFloat(bbox[3])]);
    if (bbox_1[0] < 1) {
        bbox_1 = [parseFloat(bbox[0]), parseFloat(bbox[1])];
        bbox_2 = [parseFloat(bbox[2]), parseFloat(bbox[3])];
    }
    BBOX = [
        [bbox_1[0], bbox_1[1]], // southwestern corner of the bounds
        [bbox_2[0], bbox_2[1]] // northeastern corner of the bounds
    ]
    const l = bbox[0];
    const r = bbox[2];
    const d = bbox[1];
    const u = bbox[3];
    coords = [[l, u], [r, u], [r, d], [l, d]];
    MAPBOX.coords = coords;
    MAPBOX.fitBounds([
        [bbox_1[0], bbox_1[1]], // southwestern corner of the bounds
        [bbox_2[0], bbox_2[1]] // northeastern corner of the bounds
    ]);
}

const clipSelectedLayerPromise = (boundary, layerId, drawToMap = true, currentTry = 0) => {
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
                    if (currentTry === 25) {
                        reject('Error clipping layer ' + layerId)
                    }
                    resolve(clipSelectedLayerPromise(boundary, layerId, drawToMap, currentTry+=1));
                }, 1000)
            } else if (data['status'] === 'Success') {
                doneLayer += 1;
                progressBar.style.width = `${doneLayer/allLayerIds.length * 90}%`;

                resolve("FINISH")
            } else {
                doneLayer += 1;
                progressBar.style.width = `${doneLayer/allLayerIds.length * 90}%`;

                reject('Error clipping layer ' + layerId)
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
            console.log("FINISH")
        } else {
            console.error('Error clipping layer')
        }
    }).catch((error) => console.log(error))
}

(function () {
    const scenarioSelect = document.getElementById('scenarioSelect');
    const ccaToolBtn = document.getElementById('cca-tool-btn');
    const ccaReportBtn = document.getElementById('summary-button');
    let selectedScenario = null;
    let selectedLayers = null;
    let analysisType = null;
    presetDesc.innerHTML = '';

    setTimeout(() => {
        scenarioSelect.selectedIndex = 0;
        presetDesc.innerHTML = '';
    }, 400)

    scenarioSelect.onchange = async (e) => {
        // Clear canvas
        let eaiCanvas = document.getElementById('eai-output');
        eaiCanvas.getContext('2d').clearRect(0, 0, eaiCanvas.width, eaiCanvas.height);

        let aniCanvas = document.getElementById('ani-output');
        aniCanvas.getContext('2d').clearRect(0, 0, aniCanvas.width, aniCanvas.height);

        let demandCanvas = document.getElementById('demand-output');
        demandCanvas.getContext('2d').clearRect(0, 0, demandCanvas.width, demandCanvas.height);

        let supplyCanvas = document.getElementById('supply-output');
        supplyCanvas.getContext('2d').clearRect(0, 0, supplyCanvas.width, supplyCanvas.height);

        doneLayer = 0;
        progressBar.style.width = `0%`;

        window.demandData = null;
        window.supplyData = null;
        window.aniData = null;

        ccaToolBtn.disabled = true;
        ccaReportBtn.disabled = true;
        loadingSpinner1.style.display = "block";
        loadingSpinner0.style.display = "block";
        selectedScenario = e.target.options[e.target.selectedIndex];
        analysisType = selectedScenario.dataset.analysisType.split(',');
        ANALYSIS_TYPE = analysisType;

        selectedLayers = JSON.parse(selectedScenario.dataset.layers);
        let datasetUrl = selectedScenario.dataset.url;
        presetDesc.innerHTML = selectedScenario.dataset.desc;
        let inputString = new URL(datasetUrl).searchParams.get('inputs').replace(/ *\([^)]*\) */g, "");
        let inputs = inputString.split(',')

        if (selectedLayers.length > 0) {
            selectedLayers.reverse();
        }
        const tasks = []

        if (boundary) {
            for (let i = 0; i < selectedLayers.length; i++) {
                tasks.push(clipSelectedLayerPromise(boundary, selectedLayers[i], false));
            }
            for (let j = 0; j < allLayerIds.length; j++) {
                if (!selectedLayers.includes(allLayerIds[j])) {
                    tasks.push(clipSelectedLayerPromise(boundary, allLayerIds[j], false));
                }
            }
        }

        Promise.allSettled(tasks).
            then(function (results) {
                results.forEach((result) => console.log(result))
                loadingSpinner1.style.display = "none";
                ccaToolBtn.disabled = false;
                window.getDatasets(inputString, scenarioSelect.value, analysisType);
            });
    }

    ccaToolBtn.onclick = (e) => {
        e.preventDefault();window.location.href = selectedScenario.dataset.url + '&boundary=' + boundary + '&geoId=' + geoId + '&useCase=' + useCaseId + '&subRegion=' + subRegionUrl + '&preset=' + scenarioSelect.value;
    }
})()
