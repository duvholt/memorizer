var CoursesFilter = function(input, courses) {
    this.searchInput = input;
    this.coursesList = courses;

    // Process course list for data
    this.courses = [];
    for(var i = this.coursesList.length - 1; i >= 0; i--) {
        var course = this.coursesList[i];
        this.courses.push({
            'element': course,
            'text': course.dataset.text
        });
    }

    // Listen for input change
    this.searchInput.addEventListener('input', function(e) {
        if(this.searchInput.value === '') {
            // Input empty, show all elements
            this.show();
        }
        else {
            // Show only elements matching
            this.hide();
            var list = this.filter(this.searchInput.value);
            for (var i = 0; i < list.length; i++) {
                list[i].element.style.display = '';
                list[i].element.parentNode.appendChild(list[i].element);
            }
        }
    }.bind(this));
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
