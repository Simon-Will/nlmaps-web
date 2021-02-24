function removeAdjacentSeparator(elm) {
    let sep = elm.previousElementSibling;
    if (sep === null) {
        sep = elm.nextElementSibling;
    }
    if (sep.classList.contains('nwr-super-field-separator')) {
        sep.remove();
    }
}

class NwrSuperField {
    constructor(id, name = '', inputSize = 40) {
        this.id = id;
        this.name = name || id;
        this.inputSize = inputSize;

        this.root = document.createElement('div');
        this.root.id = id;
        this.root.classList.add('nwr-super-field');

        this.fillRoot();
    }

    fillRoot() {
        this.root.appendChild(this.makeGroup(0));

        const andButton = document.createElement('button');
        andButton.type = 'button';
        andButton.innerHTML = 'And';
        andButton.classList.add('add-nwr-super-field-group');
        const thisNwrSuperField = this;
        andButton.onclick = function() {
            let groupIdx = 0;
            const prevGroup = this.previousElementSibling;
            if (prevGroup) {
                groupIdx = 1 + Number(prevGroup.getAttribute('data-group-idx'));
            }
            this.insertAdjacentElement('beforebegin', thisNwrSuperField.makeSeparator('and'));
            this.insertAdjacentElement('beforebegin', thisNwrSuperField.makeGroup(groupIdx));
            return false;
        };
        this.root.appendChild(andButton);
    }

    reset() {
        this.root.innerHTML = '';
        this.fillRoot();
    }

    makeGroup(groupIdx) {
        const elm = document.createElement('div');
        elm.classList.add('nwr-super-field-group');
        elm.setAttribute('data-group-idx', groupIdx);

        elm.appendChild(this.makeField(groupIdx, 0));

        const orButton = document.createElement('button');
        orButton.type = 'button';
        orButton.innerHTML = 'Or';
        orButton.classList.add('add-nwr-super-field-field');
        const thisNwrSuperField = this;
        orButton.onclick = function() {
            this.insertAdjacentElement('beforebegin', thisNwrSuperField.makeSeparator('or'));
            const prevTagIdx = Number(this.previousElementSibling.getAttribute('data-tag-idx'));
            this.insertAdjacentElement('beforebegin', thisNwrSuperField.makeField(groupIdx, prevTagIdx + 1));
            return false;
        };
        elm.appendChild(orButton);

        return elm;
    }

    makeField(groupIdx, tagIdx) {
        const elm = document.createElement('div');
        elm.classList.add('nwr-super-field-field');

        const input = document.createElement('input');
        input.setAttribute('name', `${this.name}-${groupIdx}-${tagIdx}`);
        input.setAttribute('data-tag-idx', tagIdx);
        input.setAttribute('type', 'text');
        input.setAttribute('size', this.inputSize);
        input.setAttribute('pattern', '[^=]+=[^=]+');
        input.setAttribute('title', 'key=value');
        input.setAttribute('placeholder', 'key=value');
        elm.appendChild(input);

        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.classList.add('remove-nwr-super-field-field');
        removeButton.innerHTML = '✖';
        removeButton.onclick = function() {
            if (elm.parentElement.querySelectorAll('.nwr-super-field-field').length <=1) {
                // This is the last element that is left. Remove the whole group.
                const parent = elm.parentElement;
                removeAdjacentSeparator(parent);
                parent.remove();
            } else {
                removeAdjacentSeparator(elm);
                elm.remove();
            }
        };
        elm.appendChild(removeButton);

        return elm;
    }

    makeSeparator(text) {
        const sep = document.createElement('span');
        sep.classList.add('nwr-super-field-separator');
        sep.appendChild(document.createTextNode(text));
        return sep;
    }

    addTag(groupIdx, tag) {
        const group = this.root.querySelector(`.nwr-super-field-group[data-group-idx="${groupIdx}"]`);
        let lastInput = Array.from(group.querySelectorAll('input')).pop();
        if (lastInput.value) {
            Array.from(
                group.querySelectorAll('button.add-nwr-super-field-field')
            ).pop().click();
            lastInput = Array.from(group.querySelectorAll('input')).pop();
        }
        lastInput.value = tag;
    }

    setNwrFeatures(nwrFeatures) {
        this.reset();
        nwrFeatures = canonicalizeNwrFeatures(nwrFeatures);
        const addGroupButton = this.root.querySelector(
            'button.add-nwr-super-field-group');
        let groupIdx = 0;
        let needNewGroup = false;
        for (let feat of nwrFeatures) {
            if (needNewGroup) {
                groupIdx += 1;
                addGroupButton.click();
            }

            if (feat[0] === 'or' && Array.isArray(feat[1])) {
                for (let tag of feat.slice(1)) {
                    this.addTag(groupIdx, tag[0] + '=' + tag[1]);
                }
                needNewGroup = true;
            } else if (feat[0] === 'and' && Array.isArray(feat[1])) {
                flashMessage(this.root, `Skipping ${feat}. “and” is not supported.`,
                             'bg-error', 15000);
                needNewGroup = false;
            } else if (feat.length === 2 && feat.every(isString)) {
                this.addTag(groupIdx, feat[0] + '=' + feat[1]);
                needNewGroup = true;
            } else {
                flashMessage(this.root, `Skipping ${feat}. Unknown error.`,
                             'bg-error', 15000);
                needNewGroup = false;
            }
        }
    }

    getNwrFeatures() {
        const nwr = [];
        for (let group of this.root.querySelectorAll('.nwr-super-field-group')) {
            const groupNwr = [];
            for (let input of group.querySelectorAll('input')) {
                const val = input.value;
                if (val && val.includes('=')) {
                    const tag = val.split('=', 2);
                    groupNwr.push(tag);
                }
            }
            if (groupNwr.length === 1) {
                nwr.push(groupNwr[0]);
            } else if (groupNwr.length > 1) {
                groupNwr.unshift('or');
                nwr.push(groupNwr);
            }
        }
        return nwr;
    }
}
