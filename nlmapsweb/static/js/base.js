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

function contains(array, elm) {
    return array.indexOf(elm) >= 0;
}

function isString(obj) {
    return typeof obj === 'string' || obj instanceof String;
}

function flashMessage(parentElm, text = 'Updated!', cssClass = 'bg-success', milliseconds = 2000) {
    const updatedElm = document.createElement('p');
    updatedElm.innerHTML = text;
    updatedElm.classList.add(cssClass);
    parentElm.appendChild(updatedElm);
    window.setTimeout(function() {console.log('Time up'); updatedElm.remove();},
                      milliseconds);
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

function nwrFeaturesToTagString(nwrFeatures) {
    const parts = [];
    for (let feat of nwrFeatures) {
        if (contains(['or', 'and'], feat[0]) && Array.isArray(feat[1])) {
            let part = feat[0] + '(' + nwrFeaturesToTagString(feat.slice(1)) + ')';
            parts.push(part);
        } else if (feat.length === 2 && Array.isArray(feat[1])
                   && feat[1][0] === 'or') {
            let part = feat[0] + '=or(' + feat[1].slice(1).join(',') + ')';
            parts.push(part);
        } else if (feat.length === 2 && feat.every(isString)) {
            parts.push(feat[0] + '=' + feat[1]);
        } else {
            console.log('Unexpected nwrFeatures feat:', feat);
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

        // Deprecated
        this.element = element;
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

    if (features.query_type === 'in_query') {
        const table = document.createElement('table');
        const tableBody = document.createElement('tbody');
        table.appendChild(tableBody);

        tableBody.appendChild(
            makeTableRow('Question Class', 'Thing in Area')
        );
        tableBody.appendChild(
            makeTableRow('Target tags',
                         nwrFeaturesToTagString(features.target_nwr))
        );
        tableBody.appendChild(makeTableRow('Area', features.area));
        tableBody.appendChild(
            makeTableRow('QType', openParenAfterFunctor(features.qtype))
        );
        if (features.cardinal_direction) {
            tableBody.appendChild(
                makeTableRow('Cardinal Direction', features.cardinal_direction)
            );
        }
        elm = table;
    } else if (features.query_type === 'around_query') {
        const table = document.createElement('table');
        const tableBody = document.createElement('tbody');
        table.appendChild(tableBody);

        tableBody.appendChild(
            makeTableRow('Question Class', 'Thing around Reference Point')
        );
        tableBody.appendChild(
            makeTableRow('Target tags',
                         nwrFeaturesToTagString(features.target_nwr))
        );
        tableBody.appendChild(
            makeTableRow('Reference point',
                         nwrFeaturesToTagString(features.center_nwr))
        );
        if (features.area) {
            tableBody.appendChild(makeTableRow('Area', features.area));
        }
        tableBody.appendChild(
            makeTableRow('MaxDist', features.maxdist)
        );
        if (features.around_topx) {
            tableBody.appendChild(
                makeTableRow('Limit to at most', features.around_topx)
            );
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
    } else {
        elm = document.createTextNode(JSON.stringify(features));
    }

    elm.classList.add('features-info');
    return elm;
}
