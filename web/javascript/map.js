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
    zoom: 13,
  }),
});

var markers = new VectorLayer({
  source: new ol.source.Vector(),
  style: new ol.style.Style({
    image: new ol.style.Icon({
      anchor: [0.5, 1],
      src: 'recourses/map-marker-svgrepo-com.svg',
    }),
  }),
  zIndex: 1001,
});
map.addLayer(markers);

function drawLine(data) {
  var points = [];

  data.forEach((point) => {
    var lonLat = fromLonLat([point.lon, point.lat]);

    points.push(lonLat);

    var marker = new Feature(new Point(lonLat));
    markers.getSource().addFeature(marker);
  });

  var lineFeature = new Feature({
    geometry: new LineString(points),
  });

  return lineFeature;
}

function getRandomInRange(range) {
  return Math.floor(Math.random() * range);
}

function getRandomColor() {
  color = '';
  brightnessSum = 0;
  for (var i = 0; i < 3; i++) {
    brightness = getRandomInRange(16);
    brightnessSum += brightness;
    color += brightness.toString(16);
  }
  if (brightnessSum < 32) {
    color[getRandomInRange(3) + 1] = 'a';
  }
  if (brightnessSum > 42) {
    color[getRandomInRange(3) + 1] = '5';
  }
  console.log(color);
  return '#' + color;
}

function drawRoute(route) {
  let lineFeatures = [];

  lineFeatures.push(drawLine(route));

  var source = new VectorSource({
    features: lineFeatures,
    wrapX: false,
  });

  const style = new Style({
    stroke: new Stroke({
      color: getRandomColor(),
      width: 5,
    }),
  });

  var vector_layer = new VectorLayer({
    source: source,
    style: style,
  });

  map.addLayer(vector_layer);
}

function drawRoutes(data) {
  for (const [_, route] of Object.entries(data)) {
    drawRoute(route);
  }
}

let testData = {
  route1: [
    { lon: 24.105078, lat: 56.946285 },
    { lon: 24.100078, lat: 56.946285 },
    { lon: 24.100078, lat: 56.951285 },
  ],
  route2: [
    { lon: 24.124218, lat: 56.996745 },
    { lon: 24.137366, lat: 56.983077 },
    { lon: 24.123147, lat: 56.961278 },
    { lon: 24.198709, lat: 56.970187 },
    { lon: 24.1606, lat: 56.971356 },
  ],
};

drawRoutes(testData);
