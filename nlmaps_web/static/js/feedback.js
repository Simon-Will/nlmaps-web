window.addEventListener('load', function() {
    const CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')
          .getAttribute('content');

    function makeSpan(string, start, end, cssClass) {
        const span = document.createElement('span');
        span.appendChild(document.createTextNode(string.substring(start, end)));
        span.classList.add(cssClass);
        return span;
    }

    function flipEditType(editType) {
        switch(editType) {
        case 'insert': return 'delete';
        case 'delete': return 'insert';
        default: return editType;
        }
    }

    document.querySelectorAll('.feedback-piece').forEach(function(elm) {
        const opcodes = JSON.parse(elm.getAttribute('data-opcodes'));
        if (opcodes) {
            const feedbackSysElm = elm.querySelector('.feedback-sys');
            const feedbackSys = feedbackSysElm.innerHTML;
            const feedbackCorrElm = elm.querySelector('.feedback-corr');
            const feedbackCorr = feedbackCorrElm.innerHTML;
            feedbackSysElm.innerHTML = '';
            feedbackCorrElm.innerHTML = '';

            opcodes.forEach(function([editType, fromSysStart, fromSysEnd,
                                      fromCorrStart, fromCorrEnd]){
                feedbackSysElm.appendChild(
                    makeSpan(feedbackSys, fromSysStart, fromSysEnd,
                             'highlight-' + editType)
                );
                feedbackCorrElm.appendChild(
                    makeSpan(feedbackCorr, fromCorrStart, fromCorrEnd,
                             'highlight-' + flipEditType(editType))
                );
            });
        }
    });

    function add_tags(tags) {
        document.querySelectorAll('.feedback-tags-form select')
            .forEach(function(selectElm) {
                tags.forEach(function(tag) {
                    const option = document.createElement('option');
                    option.appendChild(document.createTextNode(tag));
                    option.setAttribute('value', tag);
                    selectElm.appendChild(option);
                });
            });
    }

    function selectTagsInForm(tags, form) {
        tags.forEach(function(tag) {
            form.querySelector('option[value="' + tag + '"]')
                .selected = 'selected';
        });
    }

    document.querySelectorAll('.feedback-tags-form').forEach(function(form) {
        form.onsubmit = function() {
            const formData = new FormData(this);

            thisForm = this;
            let xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    if (xhr.status === 200) {
                        const response = JSON.parse(xhr.responseText);
                        console.log(response);
                        if (response.newTags) {
                            add_tags(response.newTags);
                            selectTagsInForm(response.newTags, thisForm);
                        }
                        thisForm.querySelector('input[name="new_tags"]').value = '';
                        console.log('Updated');
                        flashMessage(thisForm, 'Tagged!');
                    } else {
                        flashMessage(thisForm, 'Tagging failed!', 'bg-warning');
                    }
                }
            };
            xhr.open('POST', this.action);
            xhr.send(formData);
            return false;
        };
    });

    const parseUnparsedButton = document.getElementById('parse-unparsed');
    if (parseUnparsedButton) {
        parseUnparsedButton.onclick = function() {
            const formData = new FormData();
            formData.append('model', this.getAttribute('data-model'));
            formData.append('csrf_token', CSRF_TOKEN);

            const thisButton = this;
            ajaxPost(
                '/batch_parse',
                function(xhr) {
                    thisButton.parentElement.appendChild(
                        document.createTextNode('Parsed'));
                },
                function(xhr) {
                    console.log(xhr.responseText);
                },
                null,
                formData
            );
        };
    }

    document.querySelectorAll('.add-child-button').forEach(function(button) {
        button.onclick = function() {
            const id = button.getAttribute('data-piece-id');
            button.previousElementSibling.hidden = false;
            button.hidden = true;
        };
    });
    document.querySelectorAll('.add-child-form').forEach(function(form) {
        form.onsubmit = function() {
            const formData = new FormData(this);
            ajaxPost(
                this.action,
                function(xhr) {
                    const fb = JSON.parse(xhr.responseText);

                    const feedbackPieceDiv = document.createElement('div');
                    feedbackPieceDiv.classList.add('feedback-piece');
                    feedbackPieceDiv.classList.add('feedback-type-unknown');

                    const idPar = document.createElement('p');
                    idPar.classList.add('feedback-id');
                    const idParLink = document.createElement('a');
                    idParLink.setAttribute('href', '/feedback/' + fb.id);
                    idParLink.innerHTML = fb.id;
                    idPar.appendChild(idParLink);
                    feedbackPieceDiv.appendChild(idPar);

                    const nlPar = document.createElement('p');
                    nlPar.classList.add('feedback-nl');
                    nlPar.innerHTML = fb.nl;
                    feedbackPieceDiv.appendChild(nlPar);

                    const sysPar = document.createElement('p');
                    sysPar.classList.add('feedback-sys');
                    sysPar.classList.add('mrl');
                    sysPar.innerHTML = 'None';
                    feedbackPieceDiv.appendChild(sysPar);

                    const corrPar = document.createElement('p');
                    corrPar.classList.add('feedback-corr');
                    corrPar.classList.add('mrl');
                    corrPar.innerHTML = fb.correct_mrl;
                    feedbackPieceDiv.appendChild(corrPar);

                    const feedbackList = form.closest('.block-body')
                          .querySelector('.feedback-list');
                    feedbackList.appendChild(feedbackPieceDiv);
                    if (feedbackList.children.length >= 3) {
                        form.parentElement.hidden = true;
                    }
                },
                function(xhr) {
                    flashMessage('Adding feedback failed', 'bg-danger');
                },
                null,
                formData
            );
            return false;
        };
    });

    document.querySelectorAll('.replace-button').forEach(function(button) {
        const feedbackId = button.getAttribute('data-feedback-id');
        button.onclick = function() {
            ajaxGet(
                '/replace_feedback/' + feedbackId,
                function(xhr) {
                    const fb = JSON.parse(xhr.responseText);
                    const message = 'Saved feedback with ID ' + fb.id
                        + ', NL "' + fb.nl
                        + '" and MRL "' + fb.correct_mrl + '"';
                    flashMessage(button.closest('.feedback-piece'), message,
                                 'bg-success', null);
                },
                function(xhr) {
                    const fb = JSON.parse(xhr.responseText);
                    let message = 'Unknown error';
                    if (fb.error) {
                        message = fb.error;
                    }
                    flashMessage(button.closest('.feedback-piece'), message,
                                 'bg-danger', null);
                },
            );
            return false;
        };
    });
});
