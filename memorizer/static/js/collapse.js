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
        element.style.height = 0;
        element.classList.remove('collapsed');

        element.classList.add('collapsing');
        element.style.height = element.scrollHeight + 'px';
        setTimeout(function() {
            element.classList.remove('collapsing');
            element.style.height = '';
        }, 400);
    };

    var close = function(element) {
        element.style.height = element.scrollHeight + 'px';
        // Forcing updating of height, I think?
        element.offsetHeight;

        element.classList.add('collapsing');
        element.style.height = '0px';
        setTimeout(function() {
            element.classList.remove('collapsing');
            element.classList.add('collapsed');
        }, 400);
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
