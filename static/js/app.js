/**
 * Answer questions with keystrokes
 * - Select alternative: 1, 2, 3 or 4
 * - Answer: {spacebar}
 * - Next/Previous question: Arrow right/left
 */
 $('#shortkeys').popover({ 'placement': 'bottom', 'container': 'body', 'trigger': 'hover', 'html': true});
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
	if (e.keyCode == 32 || e.keyCode == 81) {
		$('form:first').submit();
	}
	
	// Previous question
	if (e.keyCode == 37 || e.keyCode == 65) {
		if($('#prev_question').size() > 0) {
			window.location = $('#prev_question').attr('href');
		}
	}
	
	// Next question
	if (e.keyCode == 39 || e.keyCode == 68) {
		if($('#next_question').size() > 0) {
			window.location = $('#next_question').attr('href');
		}
	}
	
	// Random question
	if (e.keyCode == 38 || e.keyCode == 87) {
		if ($('#random_question').size() > 0) {
			window.location = $('#random_question').attr('href');
		}
	}
});
