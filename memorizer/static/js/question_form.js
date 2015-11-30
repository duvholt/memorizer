var QuestionForm = (function() {
    var alternatives, correct, select;
    var multiple = '1';
    var bool = '2';

    var updateQuestionType = function(e) {
        if(select.value === multiple) {
            correct.parentNode.style.display = 'none';
        }
        else if(select.value === bool) {
            correct.parentNode.style.display = '';
        }
    };

    return function(form) {
        select = form.querySelector('select[name="type"]');
        correct = form.querySelector('input[name="correct"]');
        select = form.querySelector('select[name="type"]');

        select.addEventListener('change', updateQuestionType);
        updateQuestionType();
    };
})();
