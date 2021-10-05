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

fetch("/uploaded/rasterized/9f1a148a-c683-3934-b06b-027c07bc5388.tif").then(
    response => response.arrayBuffer()
).then(onGeoTiffLoaded)

// fetch("/uploaded/rasterized/76244a4d-b641-398d-b6ad-0236cd0c6376.tif")
//   .then(function (response) {
//     return response.arrayBuffer();
//   })
//   .then(function (arrayBuffer) {
//     return fromArrayBuffer(arrayBuffer);
//   })
//   .then(function (tiff) {
//     return tiff.getImage();
//   })
//   .then(function (image) {
//     width = image.getWidth();
//     height = image.getHeight();
//     extent = image.getBoundingBox();
//     return image.readRGB();
//   })
//   .then(function (rgb) {
//     const canvas = document.createElement("canvas");
//     canvas.width = width;
//     canvas.height = height;
//     const context = canvas.getContext("2d");
//     const data = context.getImageData(0, 0, width, height);
//     const rgba = data.data;
//     let j = 0;
//     for (let i = 0; i < rgb.length; i += 3) {
//       rgba[j] = rgb[i];
//       rgba[j + 1] = rgb[i + 1];
//       rgba[j + 2] = rgb[i + 2];
//       rgba[j + 3] = 255;
//       j += 4;
//     }
//     context.putImageData(data, 0, 0);
//
//     map.addLayer(
//       new ImageLayer({
//         source: new Static({
//           url: canvas.toDataURL(),
//           projection: "EPSG:27700",
//           imageExtent: extent
//         })
//       })
//     );
//   });