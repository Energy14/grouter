map = new OpenLayers.Map('mapdiv');
map.addLayer(new OpenLayers.Layer.OSM());

var lonLat = new OpenLayers.LonLat(24.105078, 56.946285).transform(
  new OpenLayers.Projection('EPSG:4326'), // transform from WGS 1984
  map.getProjectionObject() // to Spherical Mercator Projection
);

var zoom = 16;

var markers = new OpenLayers.Layer.Markers('Markers');
map.addLayer(markers);

markers.addMarker(new OpenLayers.Marker(lonLat));

map.setCenter(lonLat, zoom);
