// Dynamic loading of questions and answering
var Questions = function() {
    this.courseApi = new CourseAPI();
    this.examApi = new ExamAPI();
    this.questionApi = new QuestionAPI();

    // Current question information
    this.questions = [];
    this.ready = false;
    this.loadQuestions();

    // DOM elements
    this.questionElement = document.querySelector('.question');
    this.form = document.querySelector('form');
    this.nextButton = document.getElementById('next');
    this.prevButton = document.getElementById('prev');
    this.randomButton = document.getElementById('random');

    // Bind user events
    this.form.addEventListener('submit', this.answer.bind(this));
    this.nextButton.addEventListener('click', this.next.bind(this));
    this.prevButton.addEventListener('click', this.previous.bind(this));
    this.randomButton.addEventListener('click', this.random.bind(this));

    this.bindRadios();

    // History popstate
    window.onpopstate = this.popstate.bind(this);

    // Keyboard shortcuts
    document.addEventListener('keydown', this.shortcuts.bind(this));
};

Questions.prototype.parseURL = function() {
    // % is because of urlencoding characters like Ø into %C3%98
    var match = window.location.href.match(/\/([\w%]+)\/([\w%]+)\/(\d+)/);
    return {course: decodeURIComponent(match[1]), exam: decodeURIComponent(match[2]), question: decodeURIComponent(match[3])};
};

Questions.prototype.generateURL = function() {
    var urlInfo = this.parseURL();
    return '/' + encodeURIComponent(urlInfo.course) + '/' + encodeURIComponent(urlInfo.exam) + '/' + this.current;
};

Questions.prototype.loadQuestions = function() {
    this.urlInfo = this.parseURL();
    if(this.urlInfo !== null) {
        this.current = Number(this.urlInfo.question);
        this.courseApi.getByCode(this.urlInfo.course, this.course.bind(this));
    }
};

Questions.prototype.course = function(course) {
    this.courseData = course[0];
    if(this.urlInfo.exam == 'all') {
        // Get all exams
        this.examApi.examIds(this.courseData.id, function(exams) {
            this.questionApi.questions(exams, function(questions) {
                this.questions = questions;
                this.currentQuestion();
                this.ready = true;
            }.bind(this));
        }.bind(this));
    }
};

Questions.prototype.answer = function(e) {
    // If called by event let's stop it
    if(e !== undefined) {
        e.preventDefault();
    }
    var radio = document.querySelector('input[name="answer"]:checked');
    if(radio !== null) {
        var question = this.currentQuestion();
        var alternatives = {};
        // Creating a dictionary of id:correct
        for (var i = 0; i < question.alternatives.length; i++) {
            var alt = question.alternatives[i];
            alternatives[alt.id] = alt;
        }
        // A bit too messy for my taste. Consider rewriting
        var radios = document.querySelectorAll('input[name="answer"]');
        for(i = 0; i < radios.length; i++) {
            // Current alternative
            alt = alternatives[Number(radios[i].value)];
            var iconElement = document.createElement('i');
            // Setting font-awesome classname
            iconElement.className = 'fa fa-fw ' + (alt.correct ? 'fa-check' : 'fa-times');
            var label = radios[i].parentElement;
            // Selected alternative
            if(radio === radios[i]) {
                var radioDiv = label.parentElement;
                radioDiv.classList.add(alt.correct ? 'success' : 'error');
                radios[i].checked = false;
            }
            // Insert after. Why is this not a standard library method?
            label.insertBefore(iconElement, radios[i].nextSibling);

            // Go to next when clicking label
            label.addEventListener('click', this.next.bind(this));

            // Disable radios
            radios[i].disabled = true;
        }
    }
};


Questions.prototype.next = function(e) {
    // If called by event let's stop it
    if(e !== undefined) {
        e.preventDefault();
    }
    this.current++;
    if(this.current > this.questions.length) {
        this.current = 1;
    }
    this.updateURL(true);
    this.update();
};

Questions.prototype.previous = function(e) {
    // If called by event let's stop it
    if(e !== undefined) {
        e.preventDefault();
    }
    this.current--;
    if(this.current < 1) {
        this.current = this.questions.length;
    }
    this.updateURL(true);
    this.update();
};

Questions.prototype.random = function() {
    // Not implemented
};

Questions.prototype.currentQuestion = function() {
    return this.questions[this.current - 1];
};

Questions.prototype.bindRadios = function() {
    var radios = document.querySelectorAll('.radio label input');
    var currentValue = -1;
    for (var i = radios.length - 1; i >= 0; i--) {
        radios[i].addEventListener('click', function(e) {
            // Radio button was clicked twice
            if(e.target.value === currentValue) {
                // Stop bubbling of the event
                e.stopPropagation();
                this.answer();
            }
            else {
                currentValue = e.target.value;
            }
        }.bind(this));
    }
};

Questions.prototype.update = function() {
    this.updateQuestion();
    this.updateStats();
};

Questions.prototype.updateQuestion = function() {
    var question = this.currentQuestion();
    var container = document.querySelector('.question-container');
    container.innerHTML = scoop('question_template', {question: question, id: this.current});

    this.bindRadios();

    // Update title
    document.title = '#' + this.current + ' - ' + this.urlInfo.course; // missing exam info
};

Questions.prototype.updateStats = function() {

};

Questions.prototype.updateURL = function(push) {
    push = push === true;
    var stateObj = {current: this.current};
    if(push) {
        history.pushState(stateObj, "", this.generateURL());
    }
    else {
        history.replaceState(stateObj, "", this.generateURL());
    }
};

Questions.prototype.popstate = function(e) {
    this.current = e.state.current;
    this.update();
};

Questions.prototype.shortcuts = function(e) {
    // Alternatives
    try {
        var alternative = e.keyCode - 49;
        document.querySelectorAll('[name="answer"]:not(:disabled)')[alternative].checked = true;
    } catch (error) {
        // Not a valid alternative
    }

    // Submit answer to current question
    if (e.keyCode == 32 || e.keyCode == 81) {
        this.answer();
    }

    // Previous question
    if (e.keyCode == 37 || e.keyCode == 65) {
        this.previous();
    }

    // Next question
    if (e.keyCode == 39 || e.keyCode == 68) {
        this.next();
    }

    // Random question
    if (e.keyCode == 82) {
        this.random();
    }
};
