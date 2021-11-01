let subregion_source = null;

MAPBOX = new mapboxgl.Map({
    container: 'map', // container ID
    style: mapboxStyle,
    center: [0, 0], // starting position [lng, lat]
    zoom: 2, // starting zoom
    preserveDrawingBuffer: true,
});


const zoomToBoundingBox = (bboxString = '80.0584517,26.3479682,88.2015273,30.4731565') => {
  const bbox = bboxString.split(',');
  const bbox_1 = proj4("EPSG:3857", "EPSG:4326").forward([parseFloat(bbox[0]), parseFloat(bbox[1])]);
  const bbox_2 =  proj4("EPSG:3857", "EPSG:4326").forward([parseFloat(bbox[2]), parseFloat(bbox[3])]);
  MAPBOX.fitBounds([
    [bbox_1[0], bbox_1[1]], // southwestern corner of the bounds
    [bbox_2[0], bbox_2[1]] // northeastern corner of the bounds
  ]);
}

let width, height, extent;

const addedLayer = {};
const showGeoJSONLayer = (url, checkLayerLoaded = true, layerId = 'boundary') => {
  fetch(url).then(response => response.json()).then(
      async data => {
        if (subregion_source) {
            MAPBOX.removeLayer('subregion-layer');
            MAPBOX.removeSource('subregion-source');
        }
        subregion_source = MAPBOX.addSource('subregion-source', {
          type: 'geojson',
          data: data
        });
        MAPBOX.addLayer({
          'id': 'subregion-layer',
          'type': 'fill',
          'source': 'subregion-source',
          'paint': {
            'fill-color': '#0280BF',
            'fill-opacity': 0.8
          }
        });
        bbox = turf.extent(data);
        const l = bbox[0];
        const r = bbox[2];
        const d = bbox[1];
        const u = bbox[3];
        console.log(bbox);
        coords = [[l, u], [r, u], [r, d], [l, d]];
        MAPBOX.coords = coords;
        MAPBOX.fitBounds(bbox, {padding: 20});
      }
  )
}

showTileLayer = (layerName) => {
  MAPBOX.on('load', function() {
    MAPBOX.addSource('boundary-source', {
      'type': 'raster',
      'tiles': [
        `/proxy_cca/${geoserverUrl}/wms?bbox={bbox-epsg-3857}&format=image/png&
        service=WMS&TILED=true&version=1.1.1&request=GetMap&srs=EPSG:3857&
        transparent=true&width=256&height=256&LAYERS=${layerName}`,
      ],
      'tileSize': 256
    });
    MAPBOX.addLayer(
        {
          'id': 'boundary-layer',
          'type': 'raster',
          'source': 'boundary-source',
          'paint': {}
        }
    );
    loadingSpinner1.style.display = "none";
  });
}
