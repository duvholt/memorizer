// Simple alert displayer

var Alert = (function() {
    var container = document.querySelector('.alerts');
    var Alert = function(message, level) {
        var timeout = 5 * 1000;
        var element = document.createElement('li');
        element.textContent = message;
        element.classList.add('alert', level);
        container.appendChild(element);
        // Dismiss after 5s
        setTimeout(function() {
            container.removeChild(element);
        }, timeout);
    };

    return Alert;
})();
