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
  map.getView().fit(imgSource.getExtent());
}

const showGeoTiffLayer = (url) => {
  fetch(url).then(
    response => response.arrayBuffer()
  ).then(onGeoTiffLoaded)
}

showGeoTiffLayer("/uploaded/rasterized/9f1a148a-c683-3934-b06b-027c07bc5388.tif")