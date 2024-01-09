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
      name: 'OpenStreetMap',
      source: new ol.source.OSM(),
    }),
  ],
  view: new ol.View({
    center: ol.proj.fromLonLat([24.105078, 56.946285]),
    zoom: 13,
  }),
});

let vectorLayers = [];
let markerLayers = [];

function drawRoutes(data) {
  clearRoutes();

  let index = 0;
  for (const [route_name, route] of Object.entries(data)) {
    drawRoute(route_name, route, index++, Object.keys(data).length);
  }
}

function clearRoutes() {
  vectorLayers.forEach((layer) => {
    map.removeLayer(layer);
  });
  vectorLayers = [];

  markerLayers.forEach((layer) => {
    map.removeLayer(layer);
  });
  markerLayers = [];
}

function drawRoute(route_name, route, routeIndex, routeCount) {
  let lineFeatures = [];

  spectrumColor = getColor(routeIndex, routeCount);

  var markers = new VectorLayer({
    name: route_name + '_markers',
    source: new ol.source.Vector(),
    style: new ol.style.Style({
      image: new ol.style.Icon({
        anchor: [0.5, 1],
        src: 'static/resources/map-marker-svgrepo-com.svg',
        color: spectrumColor,
      }),
    }),
    zIndex: 1001,
  });

  markerLayers.push(markers);
  map.addLayer(markers);

  lineFeatures.push(drawLine(route, markers));

  var source = new VectorSource({
    features: lineFeatures,
    wrapX: false,
  });

  const style = new Style({
    stroke: new Stroke({
      color: spectrumColor,
      width: 5,
    }),
  });

  var vector_layer = new VectorLayer({
    name: route_name + '_lines',
    source: source,
    style: style,
  });

  vectorLayers.push(vector_layer);
  map.addLayer(vector_layer);
}

function drawLine(data, markers) {
  var points = [];

  data['markers'].forEach((point) => {
    var lonLat = fromLonLat([point.lon, point.lat]);

    var marker = new Feature(new Point(lonLat));
    markers.getSource().addFeature(marker);
  });

  data['lines'].forEach((point) => {
    var lonLat = fromLonLat([point.lon, point.lat]);

    points.push(lonLat);
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
  color = hslToHex((routeIndex / Math.max(1, routeCount - 1)) * 245, 100, 69);
  return color;
}
