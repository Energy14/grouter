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

function drawLine(data, markers) {
  var points = [];

  data['lines'].forEach((point) => {
    var lonLat = fromLonLat([point.lon, point.lat]);

    points.push(lonLat);
  });

  data['markers'].forEach((point) => {
    var lonLat = fromLonLat([point.lon, point.lat]);

    var marker = new Feature(new Point(lonLat));
    markers.getSource().addFeature(marker);
  });

  var lineFeature = new Feature({
    geometry: new LineString(points),
  });

  return lineFeature;
}

function hslToHex(h, s, l) {
  l /= 100;
  const a = (s * Math.min(l, 1 - l)) / 100;
  const f = (n) => {
    const k = (n + h / 30) % 12;
    const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
    return Math.round(255 * color)
      .toString(16)
      .padStart(2, '0');
  };
  return `#${f(0)}${f(8)}${f(4)}`;
}

function getColor(routeIndex, routeCount) {
  color = hslToHex((routeIndex / (routeCount - 1)) * 245, 100, 69);
  return color;
}

function drawRoute(route, routeIndex, routeCount) {
  let lineFeatures = [];

  randColor = getColor(routeIndex, routeCount);

  var markers = new VectorLayer({
    source: new ol.source.Vector(),
    style: new ol.style.Style({
      image: new ol.style.Icon({
        anchor: [0.5, 1],
        src: 'resources/map-marker-svgrepo-com.svg',
        color: randColor,
      }),
    }),
    zIndex: 1001,
  });
  map.addLayer(markers);

  lineFeatures.push(drawLine(route, markers));

  var source = new VectorSource({
    features: lineFeatures,
    wrapX: false,
  });

  const style = new Style({
    stroke: new Stroke({
      color: randColor,
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
  let index = 0;
  for (const [_, route] of Object.entries(data)) {
    drawRoute(route, index++, Object.keys(data).length);
  }
}

let testData = {
  route1: {
    lines: [
      { lon: 24.1254218, lat: 56.996745 },
      { lon: 24.137366, lat: 56.983077 },
      { lon: 24.1523147, lat: 56.9561278 },
      { lon: 24.198709, lat: 56.970187 },
      { lon: 24.1606, lat: 56.9751356 },
    ],
    markers: [
      { lon: 24.1254218, lat: 56.996745 },
      { lon: 24.198709, lat: 56.970187 },
      { lon: 24.1606, lat: 56.9751356 },
    ],
  },
  route2: {
    lines: [
      { lon: 24.1500078, lat: 56.946285 },
      { lon: 24.105078, lat: 56.9462585 },
      { lon: 24.100078, lat: 56.951285 },
      { lon: 24.124218, lat: 56.9906745 },
    ],
    markers: [
      { lon: 24.1500078, lat: 56.946285 },
      { lon: 24.105078, lat: 56.9462585 },
      { lon: 24.124218, lat: 56.9906745 },
    ],
  },
  route3: {
    lines: [
      { lon: 24.125078, lat: 56.946285 },
      { lon: 24.120078, lat: 56.946285 },
      { lon: 24.1205078, lat: 56.951285 },
      { lon: 24.123147, lat: 56.9561278 },
      { lon: 24.128709, lat: 56.970187 },
      { lon: 24.1206, lat: 56.971356 },
      { lon: 24.127366, lat: 56.983077 },
    ],
    markers: [
      { lon: 24.125078, lat: 56.946285 },
      { lon: 24.1205078, lat: 56.951285 },
      { lon: 24.127366, lat: 56.983077 },
    ],
  },
};

drawRoutes(testData);
