const geotiffLayer = new ol.layer.Image();

const map = new ol.Map({
  target: 'map',
  layers: [
    new ol.layer.Tile({
      source: new ol.source.OSM()
    }),
    geotiffLayer
  ],
  view: new ol.View({
    center: [0, 0],
    zoom: 2
  })
});

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

const showGeoJSONLayer = (url) => {
  const geojsonSource = new ol.source.Vector({
      url: url,
      format: new ol.format.GeoJSON(),
  });
  const vectorLayer = new ol.layer.Vector({
    source: geojsonSource,
  });
  map.addLayer(vectorLayer);
  const intervalID = setInterval(() => {
    try {
      if (typeof vectorLayer.getFeatures() !== 'undefined') {
        map.getView().fit(vectorLayer.getSource().getExtent());
        loadingSpinner1.style.display = "none";
        statusBtn.querySelector('.text').innerHTML = 'Please Choose a Sub Region';
        clearInterval(intervalID);
      }
    } catch (e) {}
  });
}
