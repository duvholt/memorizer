var API = function() {
    this.url = null;
};

API.prototype.get = function(filters, callback) {
    Ajax({url: this.url, data: filters}, {
        success: function(data) {
            callback(data);
        },
        error: function(data) {
            Alert('Klarte ikke hente data. Prøv å laste siden på nytt.', 'error');
        }
    });
};

var CourseAPI = function() {
    API.call(this);
    this.url = '/api/courses/';
};

CourseAPI.prototype = Object.create(API.prototype);

CourseAPI.prototype.getByCode = function(code, callback) {
    this.get({code: code}, callback);
};

var ExamAPI = function() {
    API.call(this);
    this.url = '/api/exams/';
};

ExamAPI.prototype = Object.create(API.prototype);

ExamAPI.prototype.examIds = function(course_id, callback) {
    this.get({course_id: course_id}, function(exams) {
        var ids = [];
        for(var i = 0; i < exams.length; i++) {
            ids.push(exams[i].id);
        }
        callback(ids);
    }.bind(this));
};

var QuestionAPI = function() {
    API.call(this);
    this.url = '/api/questions/';
};

QuestionAPI.prototype = Object.create(API.prototype);

QuestionAPI.prototype.questions = function(exams, callback) {
    this.get({exam_id: exams}, callback);
};
