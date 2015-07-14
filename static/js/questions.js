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

    // Keyboard shortcuts
    document.addEventListener('keydown', this.shortcuts.bind(this));
};

Questions.prototype.parseUrl = function() {
    // % is because of urlencoding characters like Ø into %C3%98
    var match = window.location.href.match(/\/([\w%]+)\/([\w%]+)\/(\d+)/);
    return {course: decodeURIComponent(match[1]), exam: decodeURIComponent(match[2]), question: decodeURIComponent(match[3])};
};

Questions.prototype.loadQuestions = function() {
    this.urlInfo = this.parseUrl();
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
        // Finding correct alternatives
        console.log(question);
        for (var i = 0; i < question.alternatives.length; i++) {
            var alt = question.alternatives[i];
            if(alt.id === Number(radio.value)) {
                // Found it
                console.log(alt.correct);
                break;
            }
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
    this.updateQuestion();
};

Questions.prototype.random = function() {
    // Not implemented
};

Questions.prototype.currentQuestion = function() {
    return this.questions[this.current - 1];
};

Questions.prototype.updateQuestion = function() {
    var question = this.currentQuestion();
    var container = document.querySelector('.question-container');
    container.innerHTML = scoop('question_template', {question: question, id: this.current});
};

Questions.prototype.updateStats = function() {

};

Questions.prototype.updateURL = function() {
    // Update url
};

Questions.prototype.shortcuts = function(e) {
    // Alternatives
    try {
        var alternative = e.keyCode - 49;
        document.querySelectorAll('[name="answer"]')[alternative].checked = true;
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
