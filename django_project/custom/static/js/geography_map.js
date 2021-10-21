const geotiffLayer = new ol.layer.Image();
const tileLayer = new ol.layer.Tile();
const geotiffLayerAdded = false;

const map = new ol.Map({
  target: 'map',
  layers: [
    new ol.layer.Tile({
      source: new ol.source.OSM()
    }),
    tileLayer,
    geotiffLayer
  ],
  view: new ol.View({
    center: [0, 0],
    zoom: 2
  })
});


const zoomToBoundingBox = (bboxString = '80.0584517,26.3479682,88.2015273,30.4731565') => {
  const bbox = bboxString.split(',');
  let col = new ol.Collection();
  let bboxLayer = new ol.layer.Vector({
    source: new ol.source.Vector({
      features: col
    })
  })
  col.push(new ol.Feature({
    geometry: new ol.geom.Point(ol.proj.fromLonLat([bbox[0], bbox[1]]))
  }));
  col.push(new ol.Feature({
    geometry: new ol.geom.Point(ol.proj.fromLonLat([bbox[2], bbox[3]]))
  }));
  map.getView().fit(bboxLayer.getSource().getExtent());
}

let width, height, extent;

const statusBtn = document.getElementById('btn-status');
const loadingSpinner1 = document.getElementById('loading-spinner-1');

const onGeoTiffLoaded = (data) => {
  const tiff = GeoTIFF.parse(data);
  const image = tiff.getImage();
  const rawBox = image.getBoundingBox();
  const box = [rawBox[0],rawBox[1] - (rawBox[3] - rawBox[1]), rawBox[2], rawBox[1]];
  const bands = image.readRasters();
  const band = bands[0];
  let the_canvas = document.createElement('canvas');
  const minValue = -1;
  const maxValue = 255;
  const plot = new plotty.plot({
    canvas: the_canvas,
    data: band, width: image.getWidth(), height: image.getHeight(),
    domain: [minValue, maxValue],
    colorScale: 'earth',
    clampLow: true,
    clampHigh: true
  });
  plot.render();
  const imgSource = new ol.source.ImageStatic({
    url: the_canvas.toDataURL("image/png"),
    imageExtent: box,
    projection: 'EPSG:4326'
  })
  geotiffLayer.setSource(imgSource);
}

const showGeoTiffLayer = (url) => {
  fetch(url).then(
    response => response.arrayBuffer()
  ).then(onGeoTiffLoaded)
}

const addedLayer = {};
const showGeoJSONLayer = (url, checkLayerLoaded = true, layerId = 'boundary') => {
  const geojsonSource = new ol.source.Vector({
      url: url,
      format: new ol.format.GeoJSON(),
  });
  const vectorLayer = new ol.layer.Vector({
    source: geojsonSource,
  });
  if (layerId in addedLayer) {
    map.removeLayer(addedLayer[layerId]);
  }
  addedLayer[layerId] = vectorLayer;
  map.addLayer(vectorLayer);
  if (checkLayerLoaded) {
    const intervalID = setInterval(() => {
      try {
        if (vectorLayer.getSource().getFeatures().length > 0) {
          map.getView().fit(vectorLayer.getSource().getExtent());
          loadingSpinner1.style.display = "none";
          clearInterval(intervalID);
        }
      } catch (e) {}
    });
  }
}

showTileLayer = (layerName) => {
  tileLayer.setSource(new ol.source.TileWMS({
    url: `/proxy_cca/${geoserverUrl}/wms`,
    params: {'LAYERS': layerName, 'TILED': true},
    serverType: 'geoserver',
    transition: 0
  }));
  loadingSpinner1.style.display = "none";
  statusBtn.querySelector('.text').innerHTML = 'Please Choose a Sub Region';
}
