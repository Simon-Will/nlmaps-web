// HTML Escaping for XSS prevention
// https://stackoverflow.com/questions/1219860/html-encoding-lost-when-attribute-read-from-input-field
function htmlEscape(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\//g, '&#x2F;');
}

function htmlToElem(html) {
    let temp = document.createElement('template');
    html = html.trim(); // Never return a space text node as a result
    temp.innerHTML = html;
    return temp.content.firstChild;
}

function contains(array, elm) {
    return array.indexOf(elm) >= 0;
}

function isString(obj) {
    return typeof obj === 'string' || obj instanceof String;
}

function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}

function ajaxBase(url, method, onsuccess, onerror = null, params = null,
                  formData = null, accept = 'application/json') {
    if (url.startsWith('/')) {
        url = window.location.origin + url;
    }

    if (params) {
        url = new URL(url);
        Object.keys(params).forEach(function(key) {
            url.searchParams.set(key, params[key]);
        });
        url = url.toString();
    }

    const xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                onsuccess(xhr);
            } else if (onerror) {
                onerror(xhr);
            }
        }
    };
    xhr.open(method, url);
    xhr.setRequestHeader('Accept', accept);
    if (method === 'POST' && formData !== null) {
        xhr.send(formData);
    } else {
        xhr.send();
    }
    return xhr;
}

function ajaxGet(url, onsuccess, onerror = null, params = null) {
    return ajaxBase(url, 'GET', onsuccess, onerror, params);
}

function ajaxPost(url, onsuccess, onerror = null, params = null,
                  formData = null) {
    return ajaxBase(url, 'POST', onsuccess, onerror, params, formData);
}

function flashMessage(parentElm, text = 'Updated!', cssClass = 'bg-success', milliseconds = 2000) {
    const container = document.createElement('div');
    container.classList.add('flashed-message');
    container.classList.add(cssClass);

    const message = document.createElement('span');
    message.classList.add('flashed-message-content');
    message.innerHTML = text;
    container.appendChild(message);

    const removeButton = document.createElement('button');
    removeButton.classList.add('flashed-message-remove-button');
    removeButton.innerHTML = '✖';
    removeButton.onclick = function() {
        container.remove();
        return false;
    };
    container.appendChild(removeButton);

    parentElm.appendChild(container);
    if (milliseconds) {
        window.setTimeout(function() {container.remove();}, milliseconds);
    }
}

function makeModal(contentElements = null) {
    const modal = document.createElement('div');
    modal.classList.add('modal');

    const modalContent = document.createElement('div');
    modalContent.classList.add('modal-content');

    if (contentElements) {
        for (let elm of contentElements) {
            modalContent.appendChild(elm);
        }
    }

    modal.appendChild(modalContent);
    modal.onclick = function(event) {
        if (event.target === modal) {
            modal.remove();
        }
    };

    return modal;
}

// These two clipboard functions are taken from
// https://stackoverflow.com/a/30810322 and modified moderately.
function fallbackCopyTextToClipboard(text, flash) {
    var textArea = document.createElement("textarea");
    textArea.value = text;

    // Avoid scrolling to bottom
    textArea.style.top = "0";
    textArea.style.left = "0";
    textArea.style.position = "fixed";

    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    let success = false;
    try {
        success = document.execCommand('copy');
        console.log('Fallback: Copied.');
    } catch (err) {
        success = false;
        console.error('Fallback: Unable to copy.', err);
    }

    document.body.removeChild(textArea);
    return success;
}

function copyTextToClipboard(text, flashParent = null) {

    function flashSuccess(success) {
        if (flashParent) {
            let message = '';
            if (text.length > 70) {
                message = success ? 'Copied.' : 'Failed to copy.';
            } else {
                message = success ? 'Copied “' + text + '”.'
                    : 'Failed to copy “' + text + '”.';
            }
            const cssClass = success ? 'bg-success' : 'bg-danger';
            flashMessage(flashParent, message, cssClass, 1000);
        }
    }

    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            flashSuccess(true);
        }, function(err) {
            console.error('Navigator.clipboard: Unable to copy.', err);
            flashSuccess(false);
        });
    } else {
        success = fallbackCopyTextToClipboard(text);
        flashSuccess(success);
    }
}

function makeTag(key, val, makeLink = false) {
    const content = document.createTextNode(key + '=' + val);
    let tagElm;
    if (makeLink) {
        tagElm = document.createElement('a');
        tagElm.href = 'https://wiki.openstreetmap.org/wiki/Tag:'
            + content.textContent;
        tagElm.appendChild(content);
    } else {
        tagElm = content;
    }
    return tagElm;
}

function getUsageClass(count) {
    if (count) {
        if (count > 10000) {
            return {slug: 'abundant', name: 'Abundant'};
        } else if (count > 1000) {
            return {slug: 'common', name: 'Common'};
        } else if (count > 100) {
            return {slug: 'rare', name: 'Rare'};
        } else if (count > 0){
            return {slug: 'virtually-unused', name: 'Virtually Unused'};
        }
    }
    return {slug: 'unused', name: 'Unused'};
}

function canonicalizeNwrFeatures(nwrFeatures) {
    // Convert [['religion', ['or', 'christian', 'muslim']]]
    // into [['or', ['religion', 'christian'], ['religion', 'muslim']]]
    const parts = [];
    for (let feat of nwrFeatures) {
        if (contains(['or', 'and'], feat[0]) && Array.isArray(feat[1])) {
            const part = [feat[0]].concat(canonicalizeNwrFeatures(feat.slice(1)));
            parts.push(part);
        } else if (feat.length === 2 && Array.isArray(feat[1])
                   && feat[1][0] === 'or') {
            const or_part = ['or'];
            for (let value of feat[1].slice(1)) {
                or_part.push([feat[0], value]);
            }
            parts.push(or_part);
        } else if (feat.length === 2 && feat.every(isString)) {
            parts.push([feat[0], feat[1]]);
        } else {
            console.log('[canonicalizeNwr] Unexpected nwrFeatures feat:', feat);
            parts.push(JSON.stringify(feat));
        }
    }
    return parts;
}

function nwrFeaturesToTagString(nwrFeatures) {
    const parts = [];
    for (let feat of nwrFeatures) {
        if (contains(['or', 'and'], feat[0]) && Array.isArray(feat[1])) {
            const part = feat[0] + '(' + nwrFeaturesToTagString(feat.slice(1)) + ')';
            parts.push(part);
        } else if (feat.length === 2 && Array.isArray(feat[1])
                   && feat[1][0] === 'or') {
            const part = feat[0] + '=or(' + feat[1].slice(1).join(',') + ')';
            parts.push(part);
        } else if (feat.length === 2 && feat.every(isString)) {
            parts.push(feat[0] + '=' + feat[1]);
        } else {
            console.log('[nwrFeaturesToTagString] Unexpected nwrFeatures feat:', feat);
            parts.push(JSON.stringify(feat));
        }
    }
    return parts.join(',');
}

function openParenAfterFunctor(nestedArray) {
    const parts = [];
    for (let elm of nestedArray) {
        if (isString(elm)) {
            parts.push(elm);
        } else if (Array.isArray(elm)) {
            parts.push(elm[0] + '(' + openParenAfterFunctor(elm.slice(1)) + ')');
        } else {
            console.log('Unexpected array element:', elm);
            parts.push(JSON.stringify(elm));
        }
    }
    return parts.join(',');
}

class Block {
    constructor(element) {
        this.whole = element;
        this.header = element.querySelector('.block-header');
        this.body = element.querySelector('.block-body');

        if (this.header) {
            this.title = this.header.querySelector('.block-title');

            this.visibility = this.detectVisibility();
            this.setVisibility(this.visibility);
        }
    }

    detectVisibility() {
        if (this.whole.hidden === true) {
            return 'hidden';
        } else if (this.body.hidden === true) {
            return 'collapsed';
        } else {
            return 'expanded';
        }
    }

    setVisibility(state) {
        switch(state) {
        case 'hidden':
            this.whole.hidden = true;
            this.visibility = 'hidden';
            break;
        case 'expanded':
            this.whole.hidden = false;
            this.expand();
            break;
        case 'collapsed':
            this.whole.hidden = false;
            this.collapse();
        }
    }

    collapse() {
        this.body.hidden = true;
        this.visibility = 'collapsed';
        this.header.classList.add('block-collapsed');
        this.header.classList.remove('block-expanded');

        const block = this;
        this.header.onclick = function() {
            block.expand();
        };
    }

    expand() {
        this.body.hidden = false;
        this.visibility = 'expanded';
        this.header.classList.add('block-expanded');
        this.header.classList.remove('block-collapsed');

        const block = this;
        this.header.onclick = function() {
            block.collapse();
        };
    }

    hide() {
        this.element.hidden = true;
        this.whole.hidden = true;
    }

    show() {
        this.element.hidden = false;
        this.whole.hidden = false;
    }
}


function makeTableRow(key, value) {
    const row = document.createElement('tr');
    const keyCell = document.createElement('td');
    const valueCell = document.createElement('td');
    keyCell.appendChild(document.createTextNode(key));
    valueCell.appendChild(document.createTextNode(value));
    row.appendChild(keyCell);
    row.appendChild(valueCell);
    return row;
}


function makeFeaturesElm(features) {
    let elm = null;
    const table = document.createElement('table');
    const tableBody = document.createElement('tbody');
    table.appendChild(tableBody);

    if (features.query_type === 'in_query') {
        tableBody.appendChild(
            makeTableRow('Question Class', 'Thing in Area')
        );
        tableBody.appendChild(
            makeTableRow('Target Tags',
                         nwrFeaturesToTagString(features.target_nwr))
        );
        if (features.area) {
            tableBody.appendChild(makeTableRow('Area', features.area));
        }
        tableBody.appendChild(
            makeTableRow('QType', openParenAfterFunctor(features.qtype))
        );
        if (features.cardinal_direction) {
            tableBody.appendChild(
                makeTableRow('Cardinal Direction', features.cardinal_direction)
            );
        }
        elm = table;
    } else if (contains(['around_query', 'dist_closest'], features.query_type)) {
        let questionClass = 'Thing around Reference Point';
        if (features.query_type === 'dist_closest') {
            questionClass = 'Distance to Closest Thing';
            features = features.sub[0];
        }
        tableBody.appendChild(makeTableRow('Question Class', questionClass));

        tableBody.appendChild(
            makeTableRow('Target Tags',
                         nwrFeaturesToTagString(features.target_nwr))
        );
        tableBody.appendChild(
            makeTableRow('Reference Point',
                         nwrFeaturesToTagString(features.center_nwr))
        );
        if (features.area) {
            tableBody.appendChild(makeTableRow('Area', features.area));
        }
        tableBody.appendChild(
            makeTableRow('Maximum Distance', features.maxdist)
        );
        if (features.around_topx) {
            if (features.around_topx === '1') {
                tableBody.appendChild(
                    makeTableRow('Limit to', 'Closest')
                );
            } else {
                tableBody.appendChild(
                    makeTableRow('Limit to at Most', features.around_topx)
                );
            }
        }
        tableBody.appendChild(
            makeTableRow('QType', openParenAfterFunctor(features.qtype))
        );
        if (features.cardinal_direction) {
            tableBody.appendChild(
                makeTableRow('Cardinal Direction', features.cardinal_direction)
            );
        }
        elm = table;
    } else if (features.query_type === 'dist_between') {
        tableBody.appendChild(
            makeTableRow('Question Class', 'Distance Between Two Things')
        );

        const features1 = features.sub[0];
        tableBody.appendChild(
            makeTableRow('Target Tags 1',
                         nwrFeaturesToTagString(features1.target_nwr))
        );
        if (features1.area) {
            tableBody.appendChild(makeTableRow('Area 1', features1.area));
        }
        if (features1.cardinal_direction) {
            tableBody.appendChild(
                makeTableRow('Cardinal Direction 1', features1.cardinal_direction)
            );
        }

        const features2 = features.sub[1];
        tableBody.appendChild(
            makeTableRow('Target Tags 2',
                         nwrFeaturesToTagString(features2.target_nwr))
        );
        if (features2.area) {
            tableBody.appendChild(makeTableRow('Area 2', features2.area));
        }
        if (features2.cardinal_direction) {
            tableBody.appendChild(
                makeTableRow('Cardinal Direction 2', features2.cardinal_direction)
            );
        }

        elm = table;
    } else {
        elm = document.createElement('div');
        elm.appendChild(document.createTextNode(JSON.stringify(features)));
    }

    elm.classList.add('features-info');
    return elm;
}

function checkFeedbackStates() {
    ajaxGet('/feedback/check', function(xhr) {
        const check_data = JSON.parse(xhr.responseText);
        const flashDiv = document.getElementById('flash-container');
        if (check_data.learned.length !== 0) {
            let content = 'Model learned to correctly parse feedbacks';
            for (const info of check_data.learned) {
                content += ' #' + info.id;
            }
            content += '.';
            flashMessage(flashDiv, content, 'bg-success', null);
        }
        if (check_data.unlearned.length !== 0) {
            let content = 'Model unlearned to correctly parse feedbacks';
            for (const info of check_data.unlearned) {
                content += ' #' + info.id;
            }
            content += '.';
            flashMessage(flashDiv, content, 'bg-warning', null);
        }
    });
}

window.addEventListener('load', checkFeedbackStates);

window.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        document.querySelectorAll('.modal').forEach(function(elm) {
            elm.remove();
        });
    }
});
