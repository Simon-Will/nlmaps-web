window.onload = function() {
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
            console.log(opcodes);
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
}
