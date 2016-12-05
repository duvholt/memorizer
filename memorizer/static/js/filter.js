var CoursesFilter = function(input, container, filter) {
    // Default child element filter
    filter = filter || 'li';
    this.searchInput = input;
    this.container = container;
    this.coursesList = container.querySelectorAll(filter);

    // Process course list for data
    this.courses = [];
    for(var i = 0; i < this.coursesList.length; i++) {
        var course = this.coursesList[i];
        this.courses.push({
            'element': course,
            'text': course.dataset.text
        });
    }

    // Listen for input change
    this.searchInput.addEventListener('input', this.search.bind(this));
    // Keyboard shortcuts
    document.addEventListener('keydown', this.shortcuts.bind(this));

    // Faking a search to set up selected
    this.search();
};

CoursesFilter.prototype.max = function() {
    if(this.filterList.length > 0) {
        return this.filterList.length - 1;
    }
    return null;
};

CoursesFilter.prototype.search = function(e) {
    this.selected = null;
    if(this.searchInput.value === '') {
        // Input empty, show all elements
        this.show();
        this.filterList = this.courses;
    }
    else {
        // Show only elements matching
        this.hide();
        this.filterList = this.filter(this.searchInput.value);
    }
    if(this.filterList.length > 0) {
        // When searching always set selected element to the first
        this.selected = 0;
        this.select();
        for (var i = 0; i < this.filterList.length; i++) {
            this.filterList[i].element.style.display = '';
            this.filterList[i].element.parentNode.appendChild(this.filterList[i].element);
        }
    }
};

CoursesFilter.prototype.show = function() {
    for(var i = 0; i < this.coursesList.length; i++) {
        this.coursesList[i].style.display = '';
    }
};

CoursesFilter.prototype.hide = function() {
    for(var i = 0; i < this.coursesList.length; i++) {
        this.coursesList[i].style.display = 'none';
    }
};

CoursesFilter.prototype.filter = function(word) {
    return this.courses.filter(function(value, i, array) {
        // case insensitive contains check
        value.score = value.text.toLowerCase().indexOf(word.toLowerCase());
        // -1: not found
        return value.score !== -1;
    }.bind(this)).sort(function(a, b) {
        // Lower index = better
        return a.score - b.score;
    });
};

CoursesFilter.prototype.select = function() {
    // Mark selected element as selected
    for (var i = this.courses.length - 1; i >= 0; i--) {
        var element = this.courses[i].element;
        element.classList.remove('selected');
    }
    element = this.filterList[this.selected].element;
    element.classList.add('selected');
};

CoursesFilter.prototype.shortcuts = function(e) {
    if(e.altKey || e.ctrlKey || e.shiftKey || e.metaKey) {
        // Ignore any events with modifiers to prevent overlapping with browser shortcuts
        return;
    }
    if(this.selected !== null) {
        var computedStyle = window.getComputedStyle(this.filterList[0].element);
        // width + border + margin
        var elementWidth = this.filterList[0].element.clientWidth +
        parseInt(computedStyle.borderRightWidth, 10) + parseInt(computedStyle.borderLeftWidth, 10) +
        parseInt(computedStyle.marginRight, 10) + parseInt(computedStyle.marginLeft, 10);
        var maxCols = Math.floor(this.container.clientWidth / elementWidth);
        var maxRows = Math.ceil(this.filterList.length / maxCols);
        // Current column
        var col = this.selected % maxCols;
        // Current row
        var row = Math.floor(this.selected / maxCols);
        switch(e.keyCode) {
            // Right
            case 37:
                if(col > 0) {
                    this.selected--;
                    this.select();
                }
                e.preventDefault();
                break;
            // Left
            case 39:
                if(col < (maxCols - 1) && this.selected < this.max()) {
                    this.selected++;
                    this.select();
                }
                e.preventDefault();
                break;
            // Up
            case 38:
                if(row > 0) {
                    this.selected -= maxCols;
                    this.select();
                }
                e.preventDefault();
                break;
            // Down
            case 40:
                if(row < (maxRows - 1) && (this.selected + maxCols - 1) < this.max()) {
                    this.selected += maxCols;
                    this.select();
                }
                e.preventDefault();
                break;
            // Select
            case 13:
            case 32:
                var element = this.filterList[this.selected].element;
                window.location.href = element.getElementsByTagName('a')[0].href;
                break;
            default:
                break;
        }
    }
};
