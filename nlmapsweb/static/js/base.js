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

class Block {
    constructor(element) {
        this.element = element;
    }

    hide() {
        this.element.hidden = true;
    }

    show() {
        this.element.hidden = false;
    }
}
