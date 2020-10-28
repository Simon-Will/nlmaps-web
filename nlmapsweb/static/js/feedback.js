window.onload = function() {
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

    document.getElementById('parse-unparsed').onclick = function() {
        const formData = new FormData();
        formData.append('model', this.getAttribute('data-model'));
        formData.append('csrf_token', CSRF_TOKEN);
        let xhr = new XMLHttpRequest();

        const thisButton = this;
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    thisButton.parentElement.appendChild(
                        document.createTextNode('Parsed'));
                } else {
                    console.log(xhr.responseText);
                }
            }
        };

        xhr.open('POST', 'http://localhost:5000/batch_parse');
        xhr.send(formData);
    };
};
