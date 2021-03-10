window.addEventListener('load', function() {
    const tocBlock = new Block(document.getElementById('tutorial-toc-block'));

    document.querySelectorAll('.task .nl-prefixed').forEach(function(nl) {
        const example = nl.parentElement;
        const button = document.createElement('button');
        button.innerHTML = 'Copy NL';
        button.style.marginBottom = '1em';
        button.onclick = function() {
            const tempDiv = document.createElement('div');
            insertAfter(tempDiv, example);
            copyTextToClipboard(nl.textContent, tempDiv);
            window.setTimeout(function() {tempDiv.remove();}, 3000);
            return false;
        };
        example.appendChild(button);
    });

    const CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')
          .getAttribute('content');

    const tutorialFeedbackForm = document.getElementById('tutorial-feedback-form');
    if (tutorialFeedbackForm) {
        tutorialFeedbackForm.onsubmit = function() {
            const formData = new FormData(this);
            formData.append('csrf_token', CSRF_TOKEN);
            const thisForm = this;
            ajaxPost(
                this.action,
                function(xhr) {
                    thisForm.reset();
                    console.log('success');
                },
                function(xhr) {
                    console.log('error');
                },
                null,
                formData
            );
            return false;
        };
    }
});
