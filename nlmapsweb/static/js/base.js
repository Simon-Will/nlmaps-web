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


class Block {
    constructor(element) {
        this.element = element;
    }

    hide() {
        this.hidden = true;
    }

    show() {
        this.hidden = false;
    }
}
