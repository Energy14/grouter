const Feature = ol.Feature;
const VectorSource = ol.source.Vector;
const VectorLayer = ol.layer.Vector;
const Markers = ol.layer.Markers;
const Point = ol.geom.Point;
const LineString = ol.geom.LineString;
const Style = ol.style.Style;
const Stroke = ol.style.Stroke;
const fromLonLat = ol.proj.fromLonLat;
const Overlay = ol.Overlay;

const map = new ol.Map({
  target: 'map',
  layers: [
    new ol.layer.Tile({
      source: new ol.source.OSM(),
    }),
  ],
  view: new ol.View({
    center: ol.proj.fromLonLat([24.105078, 56.946285]),
    zoom: 16,
  }),
});

var markers = new VectorLayer({
  source: new ol.source.Vector(),
  style: new ol.style.Style({
    image: new ol.style.Icon({
      anchor: [0.5, 1],
      src: '../media/map-marker-svgrepo-com.svg',
    }),
  }),
  zIndex: 1001,
});
map.addLayer(markers);

const style = new Style({
  stroke: new Stroke({
    color: 'red',
    width: 5,
  }),
});

function drawLine(data) {
  var points = [];

  data.forEach((point) => {
    var lonLat = fromLonLat([point.lon, point.lat]);

    points.push(lonLat);

    var marker = new Feature(new Point(lonLat));
    markers.getSource().addFeature(marker);
  });

  console.log(points);

  var lineFeature = new Feature({
    geometry: new LineString(points),
  });

  return lineFeature;
}

function drawLines(data) {
  let lineFeatures = [];

  for (const [_, route] of Object.entries(data)) {
    lineFeatures.push(drawLine(route));
  }

  var source = new VectorSource({
    features: lineFeatures,
    wrapX: false,
  });

  var vector_layer = new VectorLayer({
    source: source,
    style: style,
  });

  map.addLayer(vector_layer);
}

let testData = {
  route1: [
    { lon: 24.105078, lat: 56.946285 },
    { lon: 24.100078, lat: 56.946285 },
    { lon: 24.100078, lat: 56.951285 },
  ],
};

drawLines(testData);
