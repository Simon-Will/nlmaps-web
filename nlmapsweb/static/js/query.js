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
                    console.log(diagnoseResult.tf_idf_scores);
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

    function makeMrlEditHelp(title, content = null) {
        const titleElm = document.createElement('span');
        titleElm.appendChild(document.createTextNode(title));
        titleElm.classList.add('mrl-edit-help-title');

        if (content === null) {
            content = document.createElement('div');
        }

        const mrlEditHelp = document.createElement('div');
        mrlEditHelp.classList.add('mrl-edit-help');
        mrlEditHelp.appendChild(titleElm);
        mrlEditHelp.appendChild(content);

        return mrlEditHelp;
    }

    function makeSingleTagHelp(tagInfo) {
        const help = document.createElement('div');
        help.classList.add('mrl-edit-help-tag-finder-tag-container');

        const text = document.createElement('ul');
        text.classList.add('mrl-edit-help-tag-finder-tag-text');

        const name = document.createElement('li');
        let nameContent = tagInfo.prefLabel;
        if (tagInfo.isKey) {
            nameContent += '=*';
        }
        const link = document.createElement('a');
        link.appendChild(document.createTextNode(nameContent));
        link.href = tagInfo.subject;
        name.appendChild(link);

        const description = document.createElement('li');
        description.style = 'font-style: italic;';
        description.appendChild(document.createTextNode(tagInfo.scopeNote.en));

        const count = document.createElement('li');
        count.appendChild(document.createTextNode('Count: ' + tagInfo.countAll));

        text.appendChild(name);
        text.appendChild(description);
        text.appendChild(count);

        help.appendChild(text);

        if (tagInfo.depiction) {
            const imgDiv = document.createElement('div');
            imgDiv.classList.add('mrl-edit-help-tag-finder-tag-img');
            const img = document.createElement('img');
            img.setAttribute('src', tagInfo.depiction);
            img.setAttribute('alt', 'Depiction of ' + nameContent);
            imgDiv.appendChild(img);
            help.appendChild(imgDiv);
        }

        return help;
    }

    function makeTagFinderHelp(keyword, foundTags) {
        const content = document.createElement('div');
        content.classList.add('mrl-edit-help-tag-finder');
        for (let tag of foundTags.slice(0, 3)) {
            content.appendChild(makeSingleTagHelp(tag));
        }
        const title = 'Tag candidates for “' + keyword + '”';
        return makeMrlEditHelp(title, content);
    }

    function appendTagFinderHelp(keyword, parent) {
        const url = new URL(TAGFINDER_URL);
        url.searchParams.set('query', keyword);

        const xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    const foundTags = JSON.parse(xhr.responseText);
                    if (foundTags) {
                        const editHelp = makeTagFinderHelp(keyword, foundTags);
                        parent.appendChild(editHelp);
                    }
                }
            }
        };
        xhr.open('GET', url.toString());
        xhr.send();
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
            this.modelElm = this.body.querySelector('#mrl-info-model');
            this.nlElm = this.body.querySelector('#mrl-info-nl');
            this.linElm = this.body.querySelector('#mrl-info-lin');
            this.mrlElm = this.body.querySelector('#mrl-info-mrl');
            this.featuresElm = this.body.querySelector('#mrl-info-features');
            this.judgementElm = this.body.querySelector('#mrl-judgement');

            this.model = null;
            this.nl = null;
            this.lin = null;
            this.mrl = null;
            this.systemMrl = null;
            this.features = null;
            this.systemFeatures = null;
        }

        reset() {
            this.modelElm.innerHTML = '';
            this.nlElm.innerHTML = '';
            this.linElm.innerHTML = '';
            this.mrlElm.innerHTML = '';
            this.featuresElm.innerHTML = '';
            this.element.hidden = true;
            this.hideJudgement();
        }

        hideJudgement() {
            // TODO: For some reason, the judgementElm is still visible after
            // this step.
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
            this.model = parseResult.model;
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

            this.modelElm.innerHTML = htmlEscape(this.model);
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
            mrlEditBlock.setFeatures(features);

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

                const thisMrlInfoBlock = this;
                const xhr = new XMLHttpRequest();
                xhr.onreadystatechange = function() {
                    if (xhr.readyState === XMLHttpRequest.DONE) {
                        if (xhr.status === 200) {
                            const features = JSON.parse(xhr.responseText);
                            thisMrlInfoBlock.processFeatures(features);
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
            this.mrlForm = this.body.querySelector('#mrl-query-form');
            this.featuresForm = this.body.querySelector('#query-features-form');
            this.alternatives = this.body
                .querySelector('#mrl-edit-help-alternatives');
            this.area = this.body
                .querySelector('#mrl-edit-help-area');
            this.mrlEditHelpContainer = this.body.querySelector('#mrl-edit-help-container');
        }

        reset() {
            this.setVisibility('hidden');
            this.setMrl(null);
            this.setFeatures(null);
            this.alternatives.innerHTML = '';
            this.area.innerHTML = '';
            this.mrlEditHelpContainer
                .querySelectorAll('.mrl-edit-help-tag-finder')
                .forEach(function(tagFinderHelp) {
                    tagFinderHelp.parentNode.remove();
                });
        }

        show() {
            this.setVisibility('expanded');
        }

        setMrl(mrl) {
            if (mrl) {
                this.mrlForm.querySelector("input[name='mrl']").value = mrl;

                const thisMrlEditBlock = this;
                diagnoseProblems(mrlInfoBlock.nl, mrl, function(diagnoseResult) {
                    diagnoseResult.alternatives.forEach(function(tuple) {
                        const key = tuple[0][0];
                        const val = tuple[0][1];
                        const common = tuple[1];
                        const alts = tuple[2];

                        const li = document.createElement('li');
                        const common_text = common ? '[Common] ' : '[Uncommon or non-existent] ';
                        li.appendChild(document.createTextNode(common_text));
                        li.appendChild(makeTag(key, val));
                        li.appendChild(document.createTextNode(': '));
                        const tags = alts.map(keyval => makeTag(keyval[0], keyval[1], true));
                        for (let i = 0; i < tags.length - 1; ++i) {
                            li.appendChild(tags[i]);
                            li.appendChild(document.createTextNode(', '));
                        }
                        if (tags.length > 0) {
                            li.appendChild(tags[tags.length - 1]);
                        }

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

                    if (diagnoseResult.tf_idf_scores) {
                        for (let token in diagnoseResult.tf_idf_scores) {
                            const score = diagnoseResult.tf_idf_scores[token];
                            console.log(token, score);
                            if (score > 0.3) {
                                appendTagFinderHelp(
                                    token, thisMrlEditBlock.mrlEditHelpContainer);
                            }
                        }
                    }
                });
            } else {
                //this.mrlForm.querySelector("input[name='mrl']").value = '';
                this.mrlForm.reset();
            }
        }

        setFeatures(features) {
            if (features && contains(['around_query', 'in_query'], features.query_type)) {
                const query_type_select = this.featuresForm.querySelector("select[name='query_type']");
                query_type_select.value = features.query_type;

                const targetNwrInput = this.featuresForm.querySelector("input[name='target_nwr']");
                targetNwrInput.value = JSON.stringify(features.target_nwr);
                targetNwrSuperField.setNwrFeatures(features.target_nwr);

                this.featuresForm.querySelector("select[name='qtype']").value
                    = JSON.stringify(features.qtype);
                this.featuresForm.querySelector("select[name='cardinal_direction']").value
                    = features.cardinal_direction;

                if (features.center_nwr) {
                    this.featuresForm.querySelector("input[name='center_nwr']").value
                        = JSON.stringify(features.center_nwr);
                    centerNwrSuperField.setNwrFeatures(features.center_nwr);
                }
                if (features.area) {
                    this.featuresForm.querySelector("input[name='area']").value
                        = features.area;
                }
                if (features.maxdist) {
                    this.featuresForm.querySelector("input[name='maxdist']").value
                        = features.maxdist;
                }
                if (features.around_topx) {
                    this.featuresForm.querySelector("input[name='around_topx']").value
                        = features.around_topx;
                }

                query_type_select.dispatchEvent(new Event('change'));
            } else {
                this.featuresForm.reset();
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
    const TAGFINDER_URL = 'https://tagfinder.herokuapp.com/api/search';

    const infoBlock = new Block(document.getElementById('info-block'));
    const nlQueryBlock = new Block(document.getElementById('nl-query-block'));
    const messagesBlock = new MessagesBlock(document.getElementById('messages-block'));
    const mrlInfoBlock = new MrlInfoBlock(document.getElementById('mrl-info-block'));
    const mrlEditBlock = new MrlEditBlock(document.getElementById('mrl-edit-block'));
    const answerBlock = new AnswerBlock(document.getElementById('answer-block'));

    const nlQueryForm = document.getElementById('nl-query-form');
    const mrlQueryForm = document.getElementById('mrl-query-form');
    const queryFeaturesForm = document.getElementById('query-features-form');
    const confirmMrlButton = document.getElementById('confirm-mrl');
    const adjustMrlButton = document.getElementById('adjust-mrl');
    const switchAdjustFormButton = document.getElementById('switch-adjust-form');

    const targetNwrSuperField = new NwrSuperField('target_nwr');
    queryFeaturesForm.querySelector("input[name='target_nwr']")
        .insertAdjacentElement('beforebegin', targetNwrSuperField.root);

    const centerNwrSuperField = new NwrSuperField('center_nwr');
    queryFeaturesForm.querySelector("input[name='center_nwr']")
        .insertAdjacentElement('beforebegin', centerNwrSuperField.root);

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
        const mrl = formData.get('mrl');
        answerBlock.reset();
        mrlEditBlock.reset();

        mrlInfoBlock.processMrl(mrl, true);
        return false;
    };

    queryFeaturesForm.onsubmit = function() {
        const formData = new FormData(this);
        const keys = Array.from(formData.keys());
        for (let key of keys) {
            if (key.startsWith('target_nwr') || key.startsWith('center_nwr')) {
                formData.delete(key);
            }
        }
        formData.set('target_nwr',
                     JSON.stringify(targetNwrSuperField.getNwrFeatures()));
        formData.set('center_nwr',
                     JSON.stringify(centerNwrSuperField.getNwrFeatures()));

        answerBlock.reset();
        mrlEditBlock.reset();

        const xhr = new XMLHttpRequest();
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    const mrl = xhr.responseText;
                    mrlInfoBlock.processMrl(mrl, true);
                } else {
                    let msg = '';
                    try {
                        msg =  'Retrieving mrl failed: ' + xhr.responseText;
                    } catch (SyntaxError) {
                        msg = 'Retrieving mrl failed.';
                    }
                    messagesBlock.addMessage(msg, true);
                }
            }
        };
        xhr.open('POST', 'http://localhost:5000/features_to_mrl');
        xhr.send(formData);

        return false;
    };

    confirmMrlButton.onclick = function(){
        const formData = new FormData();
        formData.append('nl', mrlInfoBlock.nl);
        formData.append('systemMrl', mrlInfoBlock.systemMrl);
        formData.append('correctMrl', mrlInfoBlock.mrl);
        formData.append('model', mrlInfoBlock.model);
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

        xhr.open('POST', 'http://localhost:5000/feedback/create');
        xhr.send(formData);

        return false;
    };

    adjustMrlButton.onclick = function() {
        mrlEditBlock.show();
        return false;
    };

    switchAdjustFormButton.onclick = function() {
        if (mrlQueryForm.hidden) {
            this.innerHTML = 'Switch to features form';
            queryFeaturesForm.hidden = true;
            mrlQueryForm.hidden = false;
        } else {
            this.innerHTML = 'Switch to MRL form';
            queryFeaturesForm.hidden = false;
            mrlQueryForm.hidden = true;
        }
    };

    queryFeaturesForm.querySelector("select[name='query_type']")
        .addEventListener('change', function() {
            if (this.value === 'in_query') {
                queryFeaturesForm.querySelector("input[name='area']").readonly = false;

                centerNwrSuperField.root.hidden = true;
                queryFeaturesForm.querySelector("label[for='center_nwr']").hidden = true;
                queryFeaturesForm.querySelector("input[name='maxdist']").hidden = true;
                queryFeaturesForm.querySelector("label[for='maxdist']").hidden = true;
                queryFeaturesForm.querySelector("input[name='around_topx']").hidden = true;
                queryFeaturesForm.querySelector("label[for='around_topx']").hidden = true;
            } else if (this.value === 'around_query') {
                if (!queryFeaturesForm.querySelector("input[name='center_nwr']").value) {
                    queryFeaturesForm.querySelector("input[name='area']").readonly = true;
                }
                centerNwrSuperField.root.hidden = false;
                queryFeaturesForm.querySelector("label[for='center_nwr']").hidden = false;
                queryFeaturesForm.querySelector("input[name='maxdist']").hidden = false;
                queryFeaturesForm.querySelector("label[for='maxdist']").hidden = false;
                queryFeaturesForm.querySelector("input[name='around_topx']").hidden = false;
                queryFeaturesForm.querySelector("label[for='around_topx']").hidden = false;
            }
        });
    // End events
};
