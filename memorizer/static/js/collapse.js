var Collapse = (function() {
    var isCollapsed = function(element) {
        return element.classList.contains('collapsed');
    };

    var toggle = function(e) {
        e.preventDefault();
        var element = e.currentTarget;
        var container = document.querySelector(element.dataset.target);
        if(isCollapsed(container)) {
            open(container);
        }
        else {
            close(container);
        }
    };

    var open = function(element) {
        element.classList.remove('collapsed');
    };

    var close = function(element) {
        element.classList.add('collapsed');
    };

    return {
        init: function() {
            var collapses = document.querySelectorAll('.collapse');
            for (var i = collapses.length - 1; i >= 0; i--) {
                collapses[i].addEventListener('click', toggle, false);
            }
        }
    };
})();

Collapse.init();
