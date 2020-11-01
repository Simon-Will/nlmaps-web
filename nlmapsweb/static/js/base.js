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
