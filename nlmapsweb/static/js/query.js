window.onload = function() {

    // Begin map stuff
    const mapView = new ol.View({
        center: ol.proj.fromLonLat([8.69079, 49.40768]),  // Heidelberg
        zoom: 12
    });

    const vectorSource = new ol.source.Vector({
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

    const container = document.getElementById('popup');
    const content = document.getElementById('popup-content');
    const closer = document.getElementById('popup-closer');

    const overlay = new ol.Overlay({
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

    const map = new ol.Map({
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

    // End map stuff

    // Begin block behavior

    function processAnswerResult(mrl, callback) {
        messagesBlock.addMessage('Retrieving result …');

        const geojsonURL = new URL('http://localhost:5000/answer_mrl');
        geojsonURL.searchParams.set('mrl', mrl);

        const xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    const answerResult = JSON.parse(xhr.responseText);
                    callback(answerResult);
                } else {
                    messagesBlock.addMessage('Retrieving result failed.', true);
                }
            }
        };
        xhr.open('GET', geojsonURL.toString());
        xhr.send();
    }

    class MessagesBlock extends Block {
        constructor(element) {
            super(element);

            this.bufSize = 5;
            this.messagesElm = element.querySelector('#messages');
        }

        reset() {
            this.messagesElm.innerHTML = '';
            this.element.hidden = true;
        }

        addMessage(content, error = false) {
            const li = document.createElement('li');
            li.appendChild(document.createTextNode(content));
            this.messagesElm.appendChild(li);

            if (error) {
                li.classList.add('message-error');
            } else {
                li.classList.add('message-info');
            }

            while (this.messagesElm.children.length > this.bufSize) {
                this.messagesElm.removeChild(this.messagesElm.firstChild);
            }

            this.element.hidden = false;
        }
    }

    class MrlInfoBlock extends Block {
        constructor(element) {
            super(element);
            this.nlElm = element.querySelector('#mrl-info-nl');
            this.linElm = element.querySelector('#mrl-info-lin');
            this.mrlElm = element.querySelector('#mrl-info-mrl');
            this.judgementElm = element.querySelector('#mrl-judgement');

            this.nl = null;
            this.lin = null;
            this.mrl = null;
            this.systemMrl = null;
        }

        reset() {
            this.nlElm.innerHTML = '';
            this.linElm.innerHTML = '';
            this.mrlElm.innerHTML = '';
            this.element.hidden = true;
            this.hideJudgement();
        }

        hideJudgement() {
            this.judgementElm.hidden = true;
            this.judgementElm.querySelector('#adjust-mrl').hidden = false;
            this.judgementElm.querySelector('#confirm-mrl').hidden = false;
        }

        showJudgement(onlyAdjust = false) {
            if (onlyAdjust) {
                this.judgementElm.hidden = false;
                this.judgementElm.querySelector('#adjust-mrl').hidden = false;
                this.judgementElm.querySelector('#confirm-mrl').hidden = true;
            } else {
                this.judgementElm.hidden = false;
                this.judgementElm.querySelector('#adjust-mrl').hidden = false;
                this.judgementElm.querySelector('#confirm-mrl').hidden = false;
            }
        }

        processParseResult(parseResult) {
            this.nl = parseResult.nl;

            if (parseResult.lin) {
                this.lin = parseResult.lin;
            } else {
                this.lin = '';
            }

            if (parseResult.mrl) {
                this.systemMrl = parseResult.mrl;
            } else {
                this.systemMrl = '';
            }

            this.nlElm.innerHTML = htmlEscape(this.nl);
            this.linElm.innerHTML = htmlEscape(this.lin);

            this.element.hidden = false;

            this.processMrl(parseResult.mrl);
        }

        processMrl(mrl) {
            mrlEditBlock.setMrl(mrl);

            if (mrl) {
                this.mrl = mrl;
                this.mrlElm.innerHTML = htmlEscape(mrl);
                this.showJudgement();

                answerBlock.processMrl(mrl);
            } else {
                this.mrl = null;
                this.mrlElm.innerHTML = '';
                this.showJudgement(true);

                messagesBlock.addMessage('Did not receive MRL.', true);
            }
        }
    }

    class MrlEditBlock extends Block {
        constructor(element) {
            super(element);
            this.form = this.element.querySelector('#mrl-query-form');
        }

        reset() {
            this.element.hidden = true;
            this.setMrl(null);
        }

        show() {
            this.element.hidden = false;
        }

        setMrl(mrl) {
            if (mrl) {
                this.form.querySelector("input[name='mrl']").value = mrl;
            } else {
                this.form.querySelector("input[name='mrl']").value = '';
            }
        }
    }

    class AnswerBlock extends Block {
        constructor(element) {
            super(element);
            this.mapElm = element.querySelector('#map');
        }

        reset() {
            vectorSource.clear();

            this.element.innerHTML = '';
            this.element.hidden = true;
        }

        processMrl(mrl) {
            this.reset();

            const thisAnswerBlock = this;
            processAnswerResult(mrl, function(answerResult) {
                messagesBlock.addMessage(
                    'Retrieved '
                        + answerResult.geojson.features.length
                        + ' results.'
                );

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
                    content = answerResult.answer;
                } else {
                    content = 'Error: ' + answerResult.error;
                }
                thisAnswerBlock.element.innerHTML = htmlEscape(content);
                thisAnswerBlock.element.hidden = false;
            });
        }
    }

    // End block behavior

    // Begin globals

    const CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')
          .getAttribute('content');

    const nlQueryBlock = new Block(document.getElementById('nl-query-block'));
    const messagesBlock = new MessagesBlock(document.getElementById('messages-block'));
    const mrlInfoBlock = new MrlInfoBlock(document.getElementById('mrl-info-block'));
    const mrlEditBlock = new MrlEditBlock(document.getElementById('mrl-edit-block'));
    const answerBlock = new AnswerBlock(document.getElementById('answer-block'));

    const nlQueryForm = document.getElementById('nl-query-form');
    const mrlQueryForm = document.getElementById('mrl-query-form');
    const confirmMrlButton = document.getElementById('confirm-mrl');
    const adjustMrlButton = document.getElementById('adjust-mrl');

    // End globals

    // Begin events

    nlQueryForm.onsubmit = function() {
        mrlInfoBlock.reset();
        messagesBlock.reset();
        answerBlock.reset();
        messagesBlock.addMessage('Parsing query …');

        const formData = new FormData(this);

        const xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                let parseResult = JSON.parse(xhr.responseText);
                if (xhr.status === 200) {
                    messagesBlock.addMessage('Parsed query.');
                } else {
                    if (parseResult.error) {
                        messagesBlock.addMessage(parseResult.error, true);
                    } else {
                        messagesBlock.addMessage('Parsing failed.', true);
                    }
                }
                mrlInfoBlock.processParseResult(parseResult);
            }
        };

        xhr.open('POST', this.action);
        xhr.send(formData);
        return false;
    };

    mrlQueryForm.onsubmit = function() {
        const formData = new FormData(this);
        mrlInfoBlock.processMrl(formData.get('mrl'));
        return false;
    };

    confirmMrlButton.onclick = function(){
        const formData = new FormData();
        formData.append('nl', mrlInfoBlock.nl);
        formData.append('systemMrl', mrlInfoBlock.systemMrl);
        formData.append('correctMrl', mrlInfoBlock.mrl);
        formData.append('csrf_token', CSRF_TOKEN);

        mrlInfoBlock.hideJudgement();
        mrlEditBlock.reset();

        let xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                let parseStatus = document.getElementById('query-status');
                if (xhr.status === 200) {
                    messagesBlock.addMessage('Feedback received. Thanks!');
                } else {
                    messagesBlock.addMessage('Feedback not received.', true);
                }
            }
        };

        xhr.open('POST', 'http://localhost:5000/feedback');
        xhr.send(formData);

        return false;
    };

    adjustMrlButton.onclick = function() {
        mrlEditBlock.show();
        return false;
    };

    // End events
};
