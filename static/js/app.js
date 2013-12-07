/**
 * Answer questions with keystrokes
 * - Select alternative: 1, 2, 3 or 4
 * - Answer: {spacebar}
 * - Next/Previous question: Arrow right/left
 */
$(document).keydown(function(e) {

	// The current question
	var currentQuestion = parseInt(window.location.pathname.split('/')[2]);

	// Select an alternative
	try {
		alternative = e.keyCode - 49;
		$('[name="answer"]')[alternative].checked = true;
	} catch (error) {
		// Not a valid alternative
	}
	
	// Submit answer to current question
	if (e.keyCode == 32) {
		$('form:first').submit();
	}
	
	// Previous question
	if (e.keyCode == 37) {
		window.location = $('#prev_question').attr('href');
	}
	
	// Next question
	if (e.keyCode == 39) {
		window.location = $('#next_question').attr('href');
	}
});
