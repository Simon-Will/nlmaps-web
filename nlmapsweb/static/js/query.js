window.onload = function() {
    let mapView = new ol.View({
        center: ol.proj.fromLonLat([8.69079, 49.40768]),  // Heidelberg
        zoom: 12
    });

    let vectorSource = new ol.source.Vector({
        features: [],
        format: new ol.format.GeoJSON()
    });

    vectorSource.on('addfeature', function() {
        let features = vectorSource.getFeatures();
        if (features.length > 0) {
            let center = ol.extent.getCenter(vectorSource.getExtent());
            mapView.setCenter(center);
        }
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
        overlay.setPosition(undefined);
        //overlay.hidden = true;
        closer.blur();
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

    function presentAnswerResult(answerResult) {
        let mapStatus = document.getElementById('query-status');

        mapStatus.innerHTML = 'Retrieved '
            + answerResult.geojson.features.length + ' results.';
        mapStatus.hidden = false;

        if (answerResult.geojson.features.length > 0) {
            vectorSource.addFeatures(
                vectorSource.getFormat().readFeatures(
                    answerResult.geojson,
                    {featureProjection: 'EPSG:3857'}
                )
            );
        }

        let content = '';
        if (answerResult.success) {
            content += '<p>' + htmlEscape(answerResult.answer) + '</p>\n';
        } else {
            content += '<p>Error: ' + htmlEscape(answerResult.error) + '</p>\n';
        }
        let resultDiv = document.getElementById('query-result');
        resultDiv.innerHTML = content;
        resultDiv.hidden = false;
    }

    function mapQuery(mrl) {
        vectorSource.clear();

        let mapStatus = document.getElementById('query-status');
        mapStatus.innerHTML = 'Retrieving result …';
        mapStatus.hidden = false;

        let geojsonURL = new URL('http://localhost:5000/answer_mrl');
        geojsonURL.searchParams.set('mrl', mrl);
        let xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    let answerResult = JSON.parse(xhr.responseText);
                    presentAnswerResult(answerResult);
                } else {
                    mapStatus.innerHTML = 'Error while retrieving result';
                    mapStatus.hidden = false;
                }
            }
        };
        xhr.open('GET', geojsonURL.toString());
        xhr.send();
    }

    function resetResults() {
        let parseResultDiv = document.getElementById('parse-result');
        parseResultDiv.hidden = true;

        let parseResultContentDiv = document.getElementById(
            'parse-result-content');
        parseResultContentDiv.innerHTML = '';

        let mrlQueryForm = document.getElementById('mrl-query-form');
        mrlQueryForm.querySelector("input[name='mrl']").value = '';

        let answerResultDiv = document.getElementById('query-result');
        answerResultDiv.innerHTML = '';
        answerResultDiv.hidden = true;

        let refineMrlButton = document.getElementById('refine-mrl');
        refineMrlButton.hidden = false;

        let confirmMrlButton = document.getElementById('confirm-mrl');
        confirmMrlButton.hidden = false;

        vectorSource.clear();
    }

    function presentParseResult(parseResult) {
        let resultDiv = document.getElementById('parse-result');
        let resultContentDiv = document.getElementById('parse-result-content');
        let content = '';
        if (parseResult.success) {
            content += '<p>Query: ' + htmlEscape(parseResult.nl) + '</p>\n';
            content += '<p>MRL: ' + htmlEscape(parseResult.mrl) + '</p>\n';
            let mrlQueryForm = document.getElementById('mrl-query-form');
            mrlQueryForm.querySelector("input[name='mrl']").value = parseResult.mrl;
        } else {
            content += '<p>Error: ' + htmlEscape(parseResult.error) + '</p>\n';
            if (parseResult.lin) {
                content += '<p>Lin: ' + htmlEscape(parseResult.lin) + '</p>\n';
            }
        }
        resultContentDiv.innerHTML = content;
        resultDiv.hidden = false;
        mapQuery(parseResult.mrl);
    }


    let nlQueryForm = document.getElementById('nl-query-form');
    nlQueryForm.onsubmit = function() {
        resetResults();

        let parseStatus = document.getElementById('query-status');
        parseStatus.innerHTML = 'Parsing query …';
        parseStatus.hidden = false;

        let formData = new FormData(this);

        let xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                let parseResult = JSON.parse(xhr.responseText);
                if (xhr.status === 200) {
                    parseStatus.innerHTML = 'Parsed query.';
                    parseStatus.hidden = false;
                } else {
                    parseStatus.innerHTML = 'Parsing failed.';
                    parseStatus.hidden = false;
                }
                presentParseResult(parseResult);
            }
        };

        xhr.open('POST', this.action);
        xhr.send(formData);
        return false;
    };

    let mrlQueryForm = document.getElementById('mrl-query-form');
    mrlQueryForm.onsubmit = function() {
        let formData = new FormData(this);
        mapQuery(formData.get('mrl'));
        return false;
    };

    let parseResultJudgement = document.getElementById('parse-result-judgement');
    let refineMrlButton = document.getElementById('refine-mrl');
    let confirmMrlButton = document.getElementById('confirm-mrl');

    refineMrlButton.onclick = function(){
        parseResultJudgement.hidden = true;
        let mrlQueryForm = document.getElementById('mrl-query-form');
        mrlQueryForm.hidden = false;
        return false;
    };

    confirmMrlButton.onclick = function(){
        parseResultJudgement.hidden = true;
        return false;
    };
};
