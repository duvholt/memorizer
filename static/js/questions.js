// Dynamic loading of questions and answering
var Questions = function() {
    this.courseApi = new CourseAPI();
    this.examApi = new ExamAPI();
    this.questionApi = new QuestionAPI();
    this.answerApi = new AnswerAPI();
    this.statsApi = null;

    // Current question information
    this.questions = [];
    this.loadQuestions();
};

// Ran when questions have been loaded
Questions.prototype.loaded = function() {
    // DOM elements
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
        var api = new API('/api/questions/' + this.urlInfo.course + '/' + this.urlInfo.exam + '/');
        api.send({}, function(questions) {
            // Shuffling alternatives
            for (var i = 0; i < questions.length; i++) {
                var question = questions[i];
                if(question.alternatives !== undefined) {
                    this.shuffle(question.alternatives);
                }
            }
            this.questions = questions;
            this.loaded();
        }.bind(this));
        if(this.urlInfo.exam !== 'all') {
            this.statsApi = new StatsAPI(this.urlInfo.course, this.urlInfo.exam);
        }
        else {
            this.statsApi = new StatsAPI(this.urlInfo.course);
        }
    }
};

Questions.prototype.answer = function(e) {
    // If called by event let's stop it
    if(e !== undefined) {
        e.preventDefault();
    }
    var selectedRadios = document.querySelectorAll('input[name="answer"]:checked');
    if(selectedRadios !== null) {
        var question = this.currentQuestion();
        if(question.multiple) {
            var alternatives = {};
            // Creating a dictionary of id:correct
            for (var i = 0; i < question.alternatives.length; i++) {
                var alt = question.alternatives[i];
                alternatives[alt.id] = alt;
            }
        }
        // A bit too messy for my taste. Consider rewriting
        var radios = document.querySelectorAll('input[name="answer"]');
        for(i = 0; i < radios.length; i++) {
            var value = radios[i].value;
            var correct, success;
            if(question.multiple) {
                // Current alternative
                correct = alternatives[Number(value)].correct;
            }
            else {
                correct = question.correct == (value == "true");
            }
            var iconElement = document.createElement('i');
            // Setting font-awesome classname
            iconElement.className = 'fa fa-fw ' + (correct ? 'fa-check' : 'fa-times');
            var label = radios[i].parentElement;
            // Selected alternative
            for (var j = 0; j < selectedRadios.length; j++) {
                var selectedRadio = selectedRadios[j];
                if(selectedRadio === radios[i]) {
                    var radioDiv = label.parentElement;
                    radioDiv.classList.add(correct ? 'success' : 'error');
                    radios[i].checked = false;
                    break;
                }
            }
            // Insert after. Why is this not a standard library method?
            label.insertBefore(iconElement, radios[i].nextSibling);

            // Go to next when clicking label
            label.addEventListener('click', this.next.bind(this));

            // Disable radios
            radios[i].disabled = true;
        }
        values = [];
        for (i = 0; i < selectedRadios.length; i++) {
            values.push(Number(selectedRadios[i].value));
        }
        // Send ajax request
        this.answerApi.submit(this.currentQuestion().id, values, function() {
            this.updateStats();
        }.bind(this));
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
    this.updateQuestion();
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
    this.updateQuestion();
};

Questions.prototype.random = function() {
    // TODO: Remove already answered questions
    var rand = Math.round(Math.random() * (this.questions.length - 1));
    this.current = rand;
    this.updateURL(true);
    this.updateQuestion();
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

Questions.prototype.updateQuestion = function() {
    var question = this.currentQuestion();
    var container = document.querySelector('.question-container');
    var boolAlternatives = [{value: "true", label: "Ja"}, {value: "false", label: "Nei"}];
    container.innerHTML = scoop('question_template', {question: question, id: this.current, boolAlts: boolAlternatives});

    this.bindRadios();

    // Update title
    document.title = '#' + this.current + ' - ' + this.urlInfo.course; // missing exam info
};

Questions.prototype.updateStats = function() {
    this.statsApi.get(function(data) {
        var stats = document.querySelector('.stats');
        stats.innerHTML = scoop('stats_template', {stats: data});
    }.bind(this));
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
    this.updateQuestion();
};

Questions.prototype.shortcuts = function(e) {
    if(e.altKey || e.ctrlKey || e.shiftKey) {
        // Ignore any events with modifiers to prevent overlapping with browser shortcuts
        return;
    }
    // Alternatives
    try {
        var alternative = e.keyCode - 49;
        var input = document.querySelectorAll('[name="answer"]:not(:disabled)')[alternative];
        input.checked = !input.checked;
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

Questions.prototype.shuffle = function(list) {
    // Fisher-Yates shuffle
    for(var i = list.length  - 1; i > 0; i--) {
        var j = Math.round(Math.random() * i);
        var tmp = list[i];
        list[i] = list[j];
        list[j] = tmp;
    }
}
