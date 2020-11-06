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
            let extent = vectorSource.getExtent();
            if (features.length === 1) {
                mapView.setCenter(ol.extent.getCenter(extent));
                mapView.setZoom(12);
            } else {
                // Widen the extent a little so that none of the features sit on
                // the edge.
                const xdiff = extent[2] - extent[0];
                const ydiff = extent[3] - extent[1];
                extent[0] -= 0.05 * xdiff;
                extent[1] -= 0.05 * ydiff;
                extent[2] += 0.05 * xdiff;
                extent[3] += 0.05 * ydiff;
                mapView.fit(extent);
            }
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

    let RESULT_RETRIEVAL_XHR = null;
    function processAnswerResult(mrl, callback) {
        if (RESULT_RETRIEVAL_XHR) {
            RESULT_RETRIEVAL_XHR.abort();
            RESULT_RETRIEVAL_XHR = null;
            messagesBlock.addMessage('Aborting result retrieval.', true);
        }

        messagesBlock.addMessage('Retrieving result …');

        const geojsonURL = new URL('http://localhost:5000/answer_mrl');
        geojsonURL.searchParams.set('mrl', mrl);

        const xhr = new XMLHttpRequest();
        RESULT_RETRIEVAL_XHR = xhr;
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                RESULT_RETRIEVAL_XHR = null;
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

    function diagnoseProblems(nl, mrl, callback) {
        messagesBlock.addMessage('Diagnosing potential MRL problems…');

        const formData = new FormData();
        formData.append('nl', nl);
        formData.append('mrl', mrl);
        formData.append('csrf_token', CSRF_TOKEN);

        const xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    const diagnoseResult = JSON.parse(xhr.responseText);
                    callback(diagnoseResult);
                } else {
                    messagesBlock.addMessage('Diagnosing failed.', true);
                }
            }
        };
        xhr.open('POST', 'http://localhost:5000/diagnose');
        xhr.send(formData);
        return false;
    }

    class MessagesBlock extends Block {
        constructor(element) {
            super(element);

            this.bufSize = 5;
            this.messagesElm = this.body.querySelector('#messages');
        }

        reset() {
            this.messagesElm.innerHTML = '';
            this.setVisibility('hidden');
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

            this.setVisibility('expanded');
        }
    }

    class MrlInfoBlock extends Block {
        constructor(element) {
            super(element);
            this.nlElm = this.body.querySelector('#mrl-info-nl');
            this.linElm = this.body.querySelector('#mrl-info-lin');
            this.mrlElm = this.body.querySelector('#mrl-info-mrl');
            this.featuresElm = this.body.querySelector('#mrl-info-features');
            this.judgementElm = this.body.querySelector('#mrl-judgement');

            this.nl = null;
            this.lin = null;
            this.mrl = null;
            this.systemMrl = null;
            this.features = null;
            this.systemFeatures = null;
        }

        reset() {
            this.nlElm.innerHTML = '';
            this.linElm.innerHTML = '';
            this.mrlElm.innerHTML = '';
            this.featuresElm.innerHTML = '';
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

            if (parseResult.features) {
                this.systemFeatures = parseResult.features;
            } else {
                this.systemFeatures = null;
            }

            this.nlElm.innerHTML = htmlEscape(this.nl);
            this.linElm.innerHTML = htmlEscape(this.lin);

            this.setVisibility('expanded');

            this.processMrl(parseResult.mrl);
            this.processFeatures(parseResult.features);
        }

        processMrl(mrl, processFeatures = false) {
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
            if (processFeatures) {
                this.retrieveAndProcessFeatures(mrl);
            }
        }

        processFeatures(features) {
           // TODO: mrlEditBlock.setFeatures(features);

            if (features) {
                this.features = features;
                this.featuresElm.innerHTML = '';
                this.featuresElm.appendChild(makeFeaturesElm(features));
            } else {
                this.features = null;
                this.featuresElm.innerHTML = '';

                messagesBlock.addMessage('Did not receive features.', true);
            }
        }

        retrieveAndProcessFeatures(mrl) {
            if (mrl) {
                const formData = new FormData();
                formData.append('mrl', mrl);
                formData.append('csrf_token', CSRF_TOKEN);

                const thisBlock = this;
                const xhr = new XMLHttpRequest();
                xhr.onreadystatechange = function() {
                    if (xhr.readyState === XMLHttpRequest.DONE) {
                        if (xhr.status === 200) {
                            const features = JSON.parse(xhr.responseText);
                            thisBlock.processFeatures(features);
                        } else {
                            messagesBlock.addMessage('Retrieving features failed.',
                                                     true);
                        }
                    }
                };
                xhr.open('POST', 'http://localhost:5000/mrl_to_features');
                xhr.send(formData);
            }
        }
    }

    class MrlEditBlock extends Block {
        constructor(element) {
            super(element);
            this.form = this.body.querySelector('#mrl-query-form');
            this.alternatives = this.body
                .querySelector('#mrl-edit-help-alternatives');
            this.area = this.body
                .querySelector('#mrl-edit-help-area');
        }

        reset() {
            this.setVisibility('hidden');
            this.setMrl(null);
            this.alternatives.innerHTML = '';
            this.area.innerHTML = '';
        }

        show() {
            this.setVisibility('expanded');
        }

        setMrl(mrl) {
            if (mrl) {
                this.form.querySelector("input[name='mrl']").value = mrl;

                const thisMrlEditBlock = this;
                diagnoseProblems(mrlInfoBlock.nl, mrl, function(diagnoseResult) {
                    diagnoseResult.alternatives.forEach(function(tuple) {
                        const key = tuple[0][0];
                        const val = tuple[0][1];
                        const common = tuple[1];
                        const alts = tuple[2];

                        const li = document.createElement('li');
                        const common_text = common ? '[Common] ' : '[Uncommon] ';
                        li.appendChild(document.createTextNode(common_text));
                        li.appendChild(makeTag(key, val));
                        li.appendChild(document.createTextNode(': '));
                        const tags = alts.map(keyval => makeTag(keyval[0], keyval[1], true));
                        for (let i = 0; i < tags.length - 1; ++i) {
                            li.appendChild(tags[i]);
                            li.appendChild(document.createTextNode(', '));
                        }
                        // TODO: Fix: arg1 not an object
                        li.appendChild(tags[tags.length - 1]);

                        thisMrlEditBlock.alternatives.appendChild(li);
                    });

                    if (diagnoseResult.area) {
                        if (diagnoseResult.area.count) {
                            thisMrlEditBlock.area.innerHTML = 'Found '
                                + diagnoseResult.area.count.toString()
                                + ' results for area “' + diagnoseResult.area.name
                                + '”.';
                        } else {
                            thisMrlEditBlock.area.innerHTML = 'Found no results for area “'
                                + diagnoseResult.area.name + '”.';
                        }
                    } else {
                        thisMrlEditBlock.area.innerHTML = 'Problem with area query.';
                    }
                });
            } else {
                this.form.querySelector("input[name='mrl']").value = '';
            }
        }
    }

    class AnswerBlock extends Block {
        constructor(element) {
            super(element);
            this.mapElm = this.body.querySelector('#map');
        }

        reset() {
            vectorSource.clear();

            this.body.innerHTML = '';
            this.setVisibility('hidden');
        }

        processMrl(mrl) {
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
                thisAnswerBlock.body.innerHTML = htmlEscape(content);
                thisAnswerBlock.setVisibility('expanded');
            });
        }
    }

    // End block behavior

    // Begin globals

    const CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')
          .getAttribute('content');

    const infoBlock = new Block(document.getElementById('info-block'));
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

    let PARSING_XHR = null;
    nlQueryForm.onsubmit = function() {
        if (PARSING_XHR) {
            PARSING_XHR.abort();
            PARSING_XHR = null;
            messagesBlock.addMessage('Aborting parsing.', true);
        }
        if (RESULT_RETRIEVAL_XHR) {
            RESULT_RETRIEVAL_XHR.abort();
            RESULT_RETRIEVAL_XHR = null;
            messagesBlock.addMessage('Aborting result retrieval.', true);
        }

        mrlInfoBlock.reset();
        mrlEditBlock.reset();
        messagesBlock.reset();
        answerBlock.reset();
        messagesBlock.addMessage('Parsing query …');

        const formData = new FormData(this);

        const xhr = new XMLHttpRequest();
        PARSING_XHR = xhr;
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                PARSING_XHR = null;
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
        const mrl = formData.get('mrl')
        answerBlock.reset();
        mrlEditBlock.reset();

        mrlInfoBlock.processMrl(mrl, true);
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
