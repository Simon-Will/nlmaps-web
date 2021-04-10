window.addEventListener('load', function() {
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

    const styles = {
        'Point': new ol.style.Style({
            image: new ol.style.Circle({
                radius: 7,
                stroke: new ol.style.Stroke({color: 'red', width: 1.5}),
                fill: new ol.style.Fill({
                    color: 'rgba(255,0,0,0.4)',
                })
            })
        }),
    };

    const centerPointStyle = new ol.style.Style({
        image: new ol.style.Circle({
            radius: 9,
            stroke: new ol.style.Stroke({color:  'rgb(8,165,223)', width: 1.5}),
            fill: new ol.style.Fill({
                color: 'rgba(8,165,223,0.4)',
            })
        })
    });

    function getFeatureStyle(feature, resolution) {
        let style = styles[feature.getGeometry().getType()];
        if (!style) {
            style = ol.style.Style.createDefaultStyle(feature, resolution)[0];
        }
        return style;
    }

    const map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Tile({
                source: new ol.source.OSM()
            }),
            new ol.layer.Vector({
                source: vectorSource,
                style: getFeatureStyle
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

        RESULT_RETRIEVAL_XHR = ajaxGet(
            '/answer_mrl',
            function(xhr) {
                RESULT_RETRIEVAL_XHR = null;
                const answerResult = JSON.parse(xhr.responseText);
                callback(answerResult);
            },
            function(xhr) {
                RESULT_RETRIEVAL_XHR = null;
                messagesBlock.addMessage('Retrieving result failed.', true);
                const answerResult = JSON.parse(xhr.responseText);
                callback(answerResult);
            },
            {mrl: mrl}
        );
    }

    function diagnoseProblems(nl, mrl, callback) {
        messagesBlock.addMessage('Diagnosing potential MRL problems…');

        const formData = new FormData();
        formData.append('nl', nl);
        formData.append('mrl', mrl);
        formData.append('csrf_token', CSRF_TOKEN);

        ajaxPost(
            '/diagnose',
            function(xhr) {
                const diagnoseResult = JSON.parse(xhr.responseText);
                callback(diagnoseResult);
            },
            function(xhr) {
                messagesBlock.addMessage('Diagnosing failed.', true);
            },
            null,
            formData
        );

        return false;
    }

    function makeUseButton(tag) {
        const button = document.createElement('button');
        button.innerHTML = 'Use as …';
        button.onclick = function() {
            const p1 = document.createElement('p');
            p1.appendChild(
                document.createTextNode(
                    targetNwrSuperField.getNwrFeatures().toString()
                )
            );
            const p2 = document.createElement('p');
            p2.appendChild(
                document.createTextNode(
                    centerNwrSuperField.getNwrFeatures().toString()
                )
            );
            const p3 = document.createElement('p');
            p3.appendChild(
                document.createTextNode(
                    targetNwr2SuperField.getNwrFeatures().toString()
                )
            );
            const modal = makeModal([p1, p2, p3]);
            mrlEditBlock.body.appendChild(modal);
            return false;
        };
        return button;
    }

    function makeCopyButton(tag, helpElm) {
        const button = document.createElement('button');
        button.innerHTML = 'Copy Tag';
        button.onclick = function() {
            const tempDiv = document.createElement('div');
            insertAfter(tempDiv, helpElm);
            copyTextToClipboard(tag, tempDiv);
            window.setTimeout(function() {tempDiv.remove();}, 3000);
        };
        return button;
    }

    function makeMrlEditHelp(title, content = null) {
        let titleElm = null;
        if (title instanceof Element) {
            titleElm = title;
        } else {
            titleElm = document.createElement('span');
            titleElm.appendChild(document.createTextNode(title));
        }
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
        link.target = '_blank';
        name.appendChild(link);

        const description = document.createElement('li');
        description.style = 'font-style: italic;';
        description.appendChild(document.createTextNode(tagInfo.scopeNote.en));

        const count = document.createElement('li');
        count.appendChild(document.createTextNode('Count: ' + tagInfo.countAll));

        const copyButton = makeCopyButton(nameContent, help);

        text.appendChild(name);
        text.appendChild(description);
        text.appendChild(count);
        text.appendChild(copyButton);

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

        const tagFinderLink = document.createElement('a');
        tagFinderLink.innerHTML = 'TagFinder';
        tagFinderLink.href = 'https://tagfinder.herokuapp.com/';
        tagFinderLink.target = '_blank';
        const title = document.createElement('span');
        title.appendChild(tagFinderLink);
        title.appendChild(document.createTextNode(' help for “' + keyword + '”'));

        return makeMrlEditHelp(title, content);
    }

    function appendTagFinderHelp(keyword, parent) {
        ajaxGet(
            TAGFINDER_URL,
            function(xhr) {
                const foundTags = JSON.parse(xhr.responseText);
                if (foundTags) {
                    const editHelp = makeTagFinderHelp(keyword, foundTags);
                    parent.appendChild(editHelp);
                }
            },
            null,
            {query: keyword}
        );
    }

    function makeSingleCustomSuggestion(tagString, description) {
        const suggestion = document.createElement('ul');
        suggestion.classList.add('mrl-edit-help-custom-suggestion');

        const tagElm = document.createElement('li');

        const orStrings = tagString.split(' AND ');
        for (let i in orStrings) {
            const tagsAsStrings = orStrings[i].split(' OR ');
            for (let j in tagsAsStrings) {
                const tag = tagsAsStrings[j].split('=', 2);
                tagElm.appendChild(makeTag(tag[0], tag[1], true));
                if (j != tagsAsStrings.length - 1) {
                    tagElm.appendChild(document.createTextNode(' OR '));
                }
            }
            if (i != orStrings.length - 1) {
                tagElm.appendChild(document.createTextNode(' AND '));
            }
        }
        suggestion.appendChild(tagElm);

        const descriptionElm = document.createElement('li');
        descriptionElm.appendChild(document.createTextNode(description));
        descriptionElm.style = 'font-style: italic;';
        suggestion.appendChild(descriptionElm);

        return suggestion;
    }

    function makeCustomSuggestionsHelp(keyword, suggestions) {
        const content = document.createElement('div');
        content.classList.add('container-vertical-flex');

        for (let tagString in suggestions) {
            const description = suggestions[tagString];
            content.appendChild(
                makeSingleCustomSuggestion(tagString, description)
            );
        }

        const title = 'NLMaps Web help for “' + htmlEscape(keyword) + '”';
        const help = makeMrlEditHelp(title, content);
        help.classList.add('mrl-edit-help-custom-suggestions');

        return help;
    }

    function makeAnswerText(text) {
        const p = document.createElement('p');
        p.appendChild(document.createTextNode(text));
        return p;
    }

    function makeSingleAnswer(answer, numResults = null) {
        const answerElm = document.createElement('div');
        if (numResults === 0) {
            const msg = 'No objects satisfied your query.'
                  + ' Either there are no suitable objects in the data'
                  + ' or the MRL is wrong. Maybe you can help fix it?';
            answerElm.appendChild(makeAnswerText(msg));
        } else if (answer.type === 'map') {
            answerElm.appendChild(makeAnswerText('See Map for Answer.'));
        } else if (answer.type === 'text') {
            answerElm.appendChild(makeAnswerText(answer.text));
        } else if (answer.type === 'error') {
            answerElm.appendChild(makeAnswerText('Error: ' + answer.error));
        } else if (answer.type === 'dist') {
            const text = 'From ' + answer.center[1]
                  + ' to ' + answer.target[1]
                  + ': ' + answer.dist.toString()
                  + ' km';
            answerElm.appendChild(makeAnswerText(text));
        } else if (answer.type === 'list') {
            answer.list.forEach(function(text) {
                answerElm.appendChild(makeAnswerText(text));
            });
        } else {
            console.error('Unexpected answer type:', answer.type);
        }
        return answerElm;
    }

    function makeAnswerElm(answer, numResults = null) {
        const wrap = document.createElement('div');
        if (answer.type === 'sub') {
            answer.sub.forEach(function(a) {
                wrap.appendChild(makeSingleAnswer(a, numResults));
            });
        } else {
            wrap.appendChild(makeSingleAnswer(answer));
        }
        return wrap;
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
            document.querySelectorAll('#bad-tag-warning').forEach(elm => elm.remove());
            this.setVisibility('hidden');
            this.hideJudgement();
        }

        hideJudgement() {
            // judgementElm has "display: flex" which overrides hidden
            // So we need to manually set "display: none"
            this.judgementElm.hidden = true;
            this.judgementElm.style.display = 'none';
            this.judgementElm.querySelector('#adjust-mrl').hidden = false;
            this.judgementElm.querySelector('#confirm-mrl').hidden = false;
        }

        showJudgement(onlyAdjust = false) {
            // judgementElm should have "display: flex", but it was probably
            // removed during hideJudgment. Give it back.
            if (onlyAdjust) {
                this.judgementElm.hidden = false;
                this.judgementElm.style.display = 'flex';
                this.judgementElm.querySelector('#adjust-mrl').hidden = false;
                this.judgementElm.querySelector('#confirm-mrl').hidden = true;
            } else {
                this.judgementElm.hidden = false;
                this.judgementElm.style.display = 'flex';
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

                messagesBlock.addMessage(
                    'Did not receive MRL. Can you construct the correct MRL on your own?',
                    true
                );
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
                ajaxPost(
                    '/mrl_to_features',
                    function(xhr) {
                        const features = JSON.parse(xhr.responseText);
                        thisMrlInfoBlock.processFeatures(features);
                    },
                    function(xhr) {
                        messagesBlock.addMessage('Retrieving features failed.',
                                                 true);
                    },
                    null,
                    formData
                );
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
            this.mrlEditHelpContainer = this.body.querySelector('#mrl-edit-help-container');
        }

        reset() {
            this.setVisibility('hidden');
            this.setMrl(null);
            this.setFeatures(null);
            this.alternatives.innerHTML = '';
            this.mrlEditHelpContainer
                .querySelectorAll('.mrl-edit-help-tag-finder')
                .forEach(function(tagFinderHelp) {
                    tagFinderHelp.parentNode.remove();
                });
            this.mrlEditHelpContainer
                .querySelectorAll('.mrl-edit-help-custom-suggestions')
                .forEach(function(help) {
                    help.remove();
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
                    diagnoseResult.taginfo.forEach(function(tuple) {
                        const key = tuple[0][0];
                        const val = tuple[0][1];
                        const count = tuple[1];
                        const common = tuple[2];
                        const alts = tuple[3];

                        const taginfo = document.createElement('div');
                        taginfo.classList.add('taginfo');
                        taginfo.classList.add('container-vertical-flex');

                        const usageClass = getUsageClass(count);
                        const usageElm = document.createElement('span');
                        usageElm.appendChild(document.createTextNode('Count: '));
                        const numberElm = document.createElement('span');
                        numberElm.classList.add('tag-usage-' + usageClass.slug);
                        numberElm.appendChild(
                            document.createTextNode(count + ' (' + usageClass.name + ')'));
                        usageElm.appendChild(numberElm);

                        const tag = makeTag(key, val, true);
                        taginfo.appendChild(tag);
                        taginfo.appendChild(usageElm);

                        const tags = alts.map(keyval => makeTag(keyval[0], keyval[1], true));
                        if (tags.length > 0) {
                            const alternativesElm = document.createElement('span');
                            alternativesElm.appendChild(document.createTextNode('Alternatives: '));
                            for (let i = 0; i < tags.length - 1; ++i) {
                                alternativesElm.appendChild(tags[i]);
                                alternativesElm.appendChild(document.createTextNode(', '));
                            }
                            if (tags.length > 0) {
                                alternativesElm.appendChild(tags[tags.length - 1]);
                            }
                            taginfo.appendChild(alternativesElm);
                        }

                        thisMrlEditBlock.alternatives.appendChild(taginfo);

                        if (count <= 1000 && val != '*') {
                            const warning = document.createElement('p');
                            warning.id = 'bad-tag-warning';
                            warning.classList.add('tag-usage-' + usageClass.slug);
                            warning.appendChild(document.createTextNode('Tag '));
                            warning.appendChild(tag.cloneNode(true));
                            warning.appendChild(document.createTextNode(
                                ' is ' + usageClass.name.toLowerCase()
                                    + (count <= 100
                                       ? '. Please adjust the parse if you can.'
                                       : '. It might need adjustment.')
                            ));
                            const featuresElm = document.getElementById(
                                'mrl-info-features');
                            insertAfter(warning, featuresElm);
                        }
                    });

                    if (diagnoseResult.tf_idf_scores) {
                        for (let token in diagnoseResult.tf_idf_scores) {
                            const score = diagnoseResult.tf_idf_scores[token];
                            if (score > 0.3) {
                                appendTagFinderHelp(
                                    token, thisMrlEditBlock.mrlEditHelpContainer);
                            }
                        }
                    }

                    if (diagnoseResult.custom_suggestions) {
                        for (let token in diagnoseResult.custom_suggestions) {
                            const suggestions = diagnoseResult.custom_suggestions[token];
                            thisMrlEditBlock.mrlEditHelpContainer.appendChild(
                                makeCustomSuggestionsHelp(token, suggestions)
                            );
                        }
                    }
                });
            } else {
                //this.mrlForm.querySelector("input[name='mrl']").value = '';
                this.mrlForm.reset();
            }
        }

        setFeatures(features) {
            if (features) {
                const query_type_select = this.featuresForm.querySelector("select[name='query_type']");
                query_type_select.value = features.query_type;

                if (contains(['dist_between', 'dist_closest'], features.query_type)) {
                    if (features.for) {
                        this.featuresForm.querySelector("input[name='for_']").value
                            = features.for;
                    }
                    if (features.sub.length > 1) {
                        const sub2 = features.sub[1];

                        const targetNwr2Input = this.featuresForm.querySelector("input[name='target_nwr_2']");
                        targetNwr2Input.value = JSON.stringify(sub2.target_nwr);
                        targetNwr2SuperField.setNwrFeatures(sub2.target_nwr);

                        if (sub2.area) {
                            this.featuresForm.querySelector("input[name='area_2']").value
                                = sub2.area;
                        }
                        if (sub2.cardinal_direction) {
                            this.featuresForm.querySelector("select[name='cardinal_direction_2']").value
                                = sub2.cardinal_direction;
                        }

                    }
                    features = features.sub[0];
                }

                const targetNwrInput = this.featuresForm.querySelector("input[name='target_nwr']");
                targetNwrInput.value = JSON.stringify(features.target_nwr);
                targetNwrSuperField.setNwrFeatures(features.target_nwr);

                const qTypeInput = this.featuresForm.querySelector("select[name='qtype']");
                if (contains(['in_query', 'around_query'], query_type_select.value)) {
                    qTypeInput.value = JSON.stringify(features.qtype);
                } else {
                    qTypeInput.value = JSON.stringify(['latlong']);
                }

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
                    if (contains(['WALKING_DIST', 'DIST_INTOWN', 'DIST_OUTTOWN', 'DIST_DAYTRIP'],
                                 features.maxdist)) {
                        this.featuresForm.querySelector("select[name='maxdist']").value
                            = features.maxdist;
                        this.featuresForm.querySelector("input[name='custom_maxdist']").value = '';
                    } else {
                        this.featuresForm.querySelector("select[name='maxdist']").value
                            = 'CUSTOM';
                        this.featuresForm.querySelector("input[name='custom_maxdist']").value
                            = features.maxdist;
                    }
                }
                if (features.around_topx) {
                    this.featuresForm.querySelector("select[name='around_topx']").value
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

                let numResults = 0;
                if (answerResult.targets) {
                    numResults = answerResult.targets.features.length;
                    vectorSource.addFeatures(
                        vectorSource.getFormat().readFeatures(
                            answerResult.targets,
                            {featureProjection: 'EPSG:3857'}
                        )
                    );
                }

                if (answerResult.centers) {
                    const features = vectorSource.getFormat().readFeatures(
                        answerResult.centers,
                        {featureProjection: 'EPSG:3857'}
                    );
                    features.forEach(function(feature) {
                        feature.setStyle(centerPointStyle);
                    });
                    vectorSource.addFeatures(features);
                }

                messagesBlock.addMessage(
                    'Retrieved ' + numResults + ' results.'
                );

                let content = null;
                if (answerResult.success) {
                    content = makeAnswerElm(answerResult.answer, numResults);
                } else {
                    content = makeAnswerElm({type: 'error',
                                             error: answerResult.error});
                }
                thisAnswerBlock.body.appendChild(content);
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
    const rejectMrlButton = document.getElementById('reject-mrl');
    const switchAdjustFormButton = document.getElementById('switch-adjust-form');

    const targetNwrSuperField = new NwrSuperField('target_nwr');
    queryFeaturesForm.querySelector("input[name='target_nwr']")
        .insertAdjacentElement('beforebegin', targetNwrSuperField.root);

    const centerNwrSuperField = new NwrSuperField('center_nwr');
    queryFeaturesForm.querySelector("input[name='center_nwr']")
        .insertAdjacentElement('beforebegin', centerNwrSuperField.root);

    const targetNwr2SuperField = new NwrSuperField('target_nwr_2');
    queryFeaturesForm.querySelector("input[name='target_nwr_2']")
        .insertAdjacentElement('beforebegin', targetNwr2SuperField.root);

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

        PARSING_XHR = ajaxPost(
            this.action,
            function(xhr) {
                PARSING_XHR = null;
                let parseResult = JSON.parse(xhr.responseText);

                messagesBlock.addMessage('Parsed query.');

                mrlInfoBlock.processParseResult(parseResult);
            },
            function(xhr) {
                PARSING_XHR = null;
                let parseResult = JSON.parse(xhr.responseText);

                if (parseResult.error) {
                    messagesBlock.addMessage(parseResult.error, true);
                } else {
                    messagesBlock.addMessage('Parsing failed.', true);
                }

                if (parseResult.model && parseResult.nl) {
                    mrlInfoBlock.processParseResult(parseResult);
                }
            },
            null,
            formData
        );
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
        const targetNwr2 = targetNwr2SuperField.getNwrFeatures();
        if (targetNwr2.length > 0) {
            formData.set('target_nwr_2', JSON.stringify(targetNwr2));
        } else {
            formData.set('center_nwr',
                         JSON.stringify(centerNwrSuperField.getNwrFeatures()));
        }

        document.querySelectorAll('.flashed-message').forEach(elm => elm.remove());

        const thisForm = this;
        ajaxPost(
            '/features_to_mrl',
            function(xhr) {
                document.querySelectorAll('#bad-tag-warning').forEach(elm => elm.remove());
                answerBlock.reset();
                mrlEditBlock.reset();
                const mrl = xhr.responseText;
                mrlInfoBlock.processMrl(mrl, true);
            },
            function(xhr) {
                const response = JSON.parse(xhr.responseText);
                if (response.errors) {
                    response.errors.forEach(function(error) {
                        flashMessage(thisForm, error, 'bg-danger', null);
                    });
                }
                messagesBlock.addMessage('Retrieving mrl failed.', true);
            },
            null,
            formData
        );
        return false;
    };

    const maxDistSelector = queryFeaturesForm.querySelector("select[name='maxdist']");
    maxDistSelector.addEventListener('change', function(event) {
        if (maxDistSelector.value === 'CUSTOM') {
            queryFeaturesForm.querySelector("input[name='custom_maxdist']").hidden = false;
            queryFeaturesForm.querySelector("label[for='custom_maxdist']").hidden = false;
        } else {
            queryFeaturesForm.querySelector("input[name='custom_maxdist']").hidden = true;
            queryFeaturesForm.querySelector("label[for='custom_maxdist']").hidden = true;
        }
    });

    confirmMrlButton.onclick = function() {
        const formData = new FormData();
        formData.append('nl', mrlInfoBlock.nl);
        formData.append('systemMrl', mrlInfoBlock.systemMrl);
        formData.append('correctMrl', mrlInfoBlock.mrl);
        formData.append('model', mrlInfoBlock.model);
        formData.append('csrf_token', CSRF_TOKEN);

        mrlInfoBlock.hideJudgement();
        mrlEditBlock.reset();

        ajaxPost(
            '/feedback/create',
            function(xhr) {
                messagesBlock.addMessage('Feedback received. Thanks!');

                const feedback = JSON.parse(xhr.responseText);
                if (feedback.chapter_finished) {
                    // In case of tutorial fulfillment, redirect to next
                    // tutorial chapter.
                    const newUrl = window.location.origin
                          + '/tutorial?chapter='
                          + (feedback.chapter_finished + 1);
                    window.location.replace(newUrl);
                }
            },
            function(xhr) {
                const feedback = JSON.parse(xhr.responseText);
                if (feedback.error) {
                    messagesBlock.addMessage(feedback['error'], true);
                    if (feedback.tips) {
                        feedback.tips.forEach(function(tip) {
                            messagesBlock.addMessage('TIP: ' + tip, true);
                        });
                    }
                } else {
                    messagesBlock.addMessage('Feedback not received.', true);
                }
            },
            null,
            formData
        );
        return false;
    };

    rejectMrlButton.onclick = function() {
        const formData = new FormData();
        formData.append('nl', mrlInfoBlock.nl);
        formData.append('systemMrl', mrlInfoBlock.systemMrl);
        formData.append('correctMrl', '');
        formData.append('model', mrlInfoBlock.model);
        formData.append('csrf_token', CSRF_TOKEN);

        mrlInfoBlock.hideJudgement();
        mrlEditBlock.reset();

        ajaxPost(
            '/feedback/create',
            function(xhr) {
                messagesBlock.addMessage(
                    'Feedback received. Thanks! We’ll figure out the correct mrl for you.');
            },
            function(xhr) {
                const feedback = JSON.parse(xhr.responseText);
                if (feedback.error) {
                    messagesBlock.addMessage(feedback['error'], true);
                } else {
                    messagesBlock.addMessage('Feedback not received.', true);
                }
            },
            null,
            formData
        );
        return false;
    };

    adjustMrlButton.onclick = function() {
        mrlEditBlock.show();
        return false;
    };

    if (switchAdjustFormButton) {
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
            return false;
        };
    }

    queryFeaturesForm.querySelector("select[name='query_type']")
        .addEventListener('change', function() {
            function showSecondFeaturesFieldset(show) {
                const secondFeaturesFieldset = document.getElementById('second-features-fieldset');
                if (show) {
                    secondFeaturesFieldset.hidden = false;
                    secondFeaturesFieldset.style.display = '';
                    secondFeaturesFieldset.disabled = false;
                } else {
                    secondFeaturesFieldset.hidden = true;
                    secondFeaturesFieldset.style.display = 'none';
                    secondFeaturesFieldset.disabled = true;
                }
            }

            if (this.value === 'in_query') {
                queryFeaturesForm.querySelector("input[name='area']").readonly = false;

                centerNwrSuperField.root.hidden = true;
                queryFeaturesForm.querySelector("label[for='center_nwr']").hidden = true;
                queryFeaturesForm.querySelector("select[name='maxdist']").hidden = true;
                queryFeaturesForm.querySelector("label[for='maxdist']").hidden = true;
                queryFeaturesForm.querySelector("input[name='custom_maxdist']").hidden = true;
                queryFeaturesForm.querySelector("label[for='custom_maxdist']").hidden = true;
                queryFeaturesForm.querySelector("select[name='around_topx']").hidden = true;
                queryFeaturesForm.querySelector("label[for='around_topx']").hidden = true;

                queryFeaturesForm.querySelector("select[name='qtype']").hidden = false;
                queryFeaturesForm.querySelector("label[for='qtype']").hidden = false;
                showSecondFeaturesFieldset(false);
            } else if (this.value === 'around_query') {
                if (!queryFeaturesForm.querySelector("input[name='center_nwr']").value) {
                    queryFeaturesForm.querySelector("input[name='area']").readonly = true;
                }
                centerNwrSuperField.root.hidden = false;
                queryFeaturesForm.querySelector("label[for='center_nwr']").hidden = false;
                queryFeaturesForm.querySelector("select[name='maxdist']").hidden = false;
                queryFeaturesForm.querySelector("label[for='maxdist']").hidden = false;
                const customMaxdistHidden = queryFeaturesForm.querySelector("select[name='maxdist']").value !== 'CUSTOM';
                queryFeaturesForm.querySelector("input[name='custom_maxdist']").hidden = customMaxdistHidden;
                queryFeaturesForm.querySelector("label[for='custom_maxdist']").hidden = customMaxdistHidden;
                queryFeaturesForm.querySelector("select[name='around_topx']").hidden = false;
                queryFeaturesForm.querySelector("label[for='around_topx']").hidden = false;

                queryFeaturesForm.querySelector("select[name='qtype']").hidden = false;
                queryFeaturesForm.querySelector("label[for='qtype']").hidden = false;
                showSecondFeaturesFieldset(false);
            } else if (this.value === 'dist_closest') {
                if (!queryFeaturesForm.querySelector("input[name='center_nwr']").value) {
                    queryFeaturesForm.querySelector("input[name='area']").readonly = true;
                }
                centerNwrSuperField.root.hidden = false;
                queryFeaturesForm.querySelector("label[for='center_nwr']").hidden = false;
                queryFeaturesForm.querySelector("select[name='maxdist']").hidden = true;
                queryFeaturesForm.querySelector("label[for='maxdist']").hidden = true;
                queryFeaturesForm.querySelector("input[name='custom_maxdist']").hidden = true;
                queryFeaturesForm.querySelector("label[for='custom_maxdist']").hidden = true;
                queryFeaturesForm.querySelector("select[name='around_topx']").hidden = true;
                queryFeaturesForm.querySelector("label[for='around_topx']").hidden = true;

                queryFeaturesForm.querySelector("select[name='qtype']").hidden = true;
                queryFeaturesForm.querySelector("label[for='qtype']").hidden = true;
                showSecondFeaturesFieldset(false);
            } else if (this.value === 'dist_between') {
                queryFeaturesForm.querySelector("input[name='area']").readonly = false;

                centerNwrSuperField.root.hidden = true;
                queryFeaturesForm.querySelector("label[for='center_nwr']").hidden = true;
                queryFeaturesForm.querySelector("select[name='maxdist']").hidden = true;
                queryFeaturesForm.querySelector("label[for='maxdist']").hidden = true;
                queryFeaturesForm.querySelector("input[name='custom_maxdist']").hidden = true;
                queryFeaturesForm.querySelector("label[for='custom_maxdist']").hidden = true;
                queryFeaturesForm.querySelector("select[name='around_topx']").hidden = true;
                queryFeaturesForm.querySelector("label[for='around_topx']").hidden = true;

                queryFeaturesForm.querySelector("select[name='qtype']").hidden = true;
                queryFeaturesForm.querySelector("label[for='qtype']").hidden = true;
                showSecondFeaturesFieldset(true);
            }
        });

    const termsNotice = document.getElementById('terms-notice');
    if (termsNotice) {
        const username = document.querySelector('meta[name="username"]');
        if (window.localStorage.hideTermsNotice || username) {
            // User has an account or has explicitly hidden the notice.
            termsNotice.hidden = true;
        }
        document.getElementById('hide-terms-notice').onclick = function() {
            window.localStorage.hideTermsNotice = true;
            termsNotice.hidden = true;
            return false;
        };
    }
    // End events
});
