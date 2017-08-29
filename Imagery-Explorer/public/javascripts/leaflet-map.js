function toWKT(layer) {
    var lng, lat, coords = [];
    if (layer instanceof L.Polygon || layer instanceof L.Polyline) {
        var latlngs = layer.getLatLngs();
        for (var i = 0; i < latlngs.length; i++) {
            latlngs[i]
            coords.push(latlngs[i].lng + " " + latlngs[i].lat);
            if (i === 0) {
                lng = latlngs[i].lng;
                lat = latlngs[i].lat;
            }
        };
        if (layer instanceof L.Polygon) {
            return "POLYGON((" + coords.join(",") + "," + lng + " " + lat + "))";
        } else if (layer instanceof L.Polyline) {
            return "LINESTRING(" + coords.join(",") + ")";
        }
    } else if (layer instanceof L.Marker) {
        return "POINT(" + layer.getLatLng().lng + " " + layer.getLatLng().lat + ")";
    }
}

var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    osm = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttrib }),
    map = new L.Map('map', { center: new L.LatLng(52.07, 19.48), zoom: 5, minZoom: 5 }),
    drawnItems = L.featureGroup().addTo(map);

osm.addTo(map);

var drawControlFull = new L.Control.Draw({
    edit: {
        featureGroup: drawnItems,
        edit: false
    },
    draw: {
        rectangle: {
            shapeOptions: {
                color: '',
                opacity: 0.8
            }
        },
        polyline: false,
        polygon: false,
        circle: false,
        circlemarker: false,
        marker: false
    }
});

var drawControlEditOnly = new L.Control.Draw({
    edit: {
        featureGroup: drawnItems,
        edit: false
    },
    draw: false
});

map.addControl(drawControlFull);

map.on("draw:created", function (e) {
    var layer = e.layer;
    layer.addTo(drawnItems);
    drawControlFull.removeFrom(map);
    drawControlEditOnly.addTo(map)
    drawnItems.addLayer(layer);
    document.getElementById('extent_form').value = toWKT(layer);
});

map.on("draw:deleted", function (e) {
    drawControlEditOnly.removeFrom(map);
    drawControlFull.addTo(map);
});

map.on(L.Draw.Event.DELETED, function (e) {
    document.getElementById('extent_form').value = null;
});