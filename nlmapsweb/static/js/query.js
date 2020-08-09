window.onload = function() {
    let mapView = new ol.View({
        center: ol.proj.fromLonLat([8.69079, 49.40768]),  // Heidelberg
        zoom: 12
    });

    let vectorSource = new ol.source.Vector({
        features: [],
        format: new ol.format.GeoJSON()
    });

    vectorSource.on('change', function() {
        let features = vectorSource.getFeatures();
        if (features.length > 0) {
            let center = ol.extent.getCenter(vectorSource.getExtent());
            mapView.setCenter(center);
        }
        let mapStatus = document.getElementById('map-status');
        mapStatus.innerHTML = 'Retrieved ' + features.length + ' results.';
        mapStatus.hidden = false;
    });

    let container = document.getElementById('popup');
    let content = document.getElementById('popup-content');
    let closer = document.getElementById('popup-closer');

    let overlay = new ol.Overlay({
        element: container,
        autoPan: {
            animation: {
                duration: 250
            }
        }
    });

    closer.onclick = function () {
        //overlay.setPosition(undefined);
        overlay.hidden = true;
        //closer.blur();
        return false;
    };

    let map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            }),
            new ol.layer.Vector({
                source: vectorSource
            })
        ],
        overlays: [overlay],
        view: mapView
    });

    map.on('singleclick', function (evt) {
        let feat = vectorSource.getClosestFeatureToCoordinate(evt.coordinate);
        content.innerHTML = feat.values_.popupContent;
        overlay.setPosition(feat.values_.geometry.flatCoordinates);
        overlay.hidden = false;
    });

    function mapQuery(mrl) {
        let mapStatus = document.getElementById('map-status');
        mapStatus.innerHTML = 'Retrieving result …';
        mapStatus.hidden = false;
        console.log(mrl);

        let geojsonURL = new URL('http://localhost:5000/geojson');
        geojsonURL.searchParams.set('mrl', mrl);
        vectorSource.setUrl(geojsonURL.toString());
        vectorSource.refresh();
    }

    function presentParseResult(parseResult) {
        let resultDiv = document.getElementById('parse-result');
        let content = '<p>Query: ' + htmlEscape(parseResult.nl) + '</p>\n'
            + '<p>MRL: ' + htmlEscape(parseResult.mrl) + '</p>\n';
        //content += '<h5>Key Value Pairs</p>\n';
        //for (let keyValPair in parseResult.alternatives) {
        //    content += '<p>' + htmlEscape(keyValPair[0])
        //        + ': ' + htmlEscape(keyValPair[1]) + ' | '
        //        + htmlEscape(parseResult.alternatives[keyValPair].toString());
        //}
        resultDiv.innerHTML = content;
        mapQuery(parseResult.mrl);
    }


    let queryForm = document.getElementById('query-form');
    queryForm.onsubmit = function() {
        event.preventDefault();
        event.stopPropagation();
        let parseStatus = document.getElementById('parse-status');
        parseStatus.innerHTML = 'Parsing query …';
        parseStatus.hidden = false;

        let formData = new FormData(this);

        let xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status == 200) {
                    let parseResult = JSON.parse(xhr.responseText);
                    presentParseResult(parseResult);
                    parseStatus.innerHTML = '';
                    parseStatus.hidden = true;
                } else {
                    parseStatus.innerHTML = 'Parsing failed.';
                    parseStatus.hidden = false;
                }
            }
        };

        xhr.open('POST', this.action);
        xhr.send(formData);
    };
};
