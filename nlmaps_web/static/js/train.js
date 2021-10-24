window.onload = function() {
    const trainSpinner = document.getElementById('train-spinner');
    const trainingFinishedSymbol = document.getElementById('train-finished');
    const message = document.getElementById('train-message');

    let lastState = null;

    function checkTrainingStatus() {
        ajaxGet(
            '/train_status',
            function(xhr) {
                const data = JSON.parse(xhr.responseText);
                if (data.still_training) {
                    message.innerHTML = 'Currently training.';
                    trainSpinner.style.display = 'block';
                    trainingFinishedSymbol.hidden = true;
                } else {
                    message.innerHTML = 'Not currently training.';
                    trainSpinner.style.display = 'none';
                    trainingFinishedSymbol.hidden = false;
                    if (lastState === true) {
                        checkFeedbackStates();
                    }
                }
                lastState = data.still_training;
            },
            function(xhr) {
                message.innerHTML = 'Error when checking training status.';
                trainSpinner.style.display = 'none';
                trainingFinishedSymbol.hidden = true;
                lastState = false;
            }
        );
    }

    const timer = setInterval(checkTrainingStatus, 5000);
    checkTrainingStatus();
};
