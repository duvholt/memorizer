from questions import questions 
from flask import Flask, render_template, redirect, url_for, request, session
from werkzeug.contrib.fixers import ProxyFix
import random

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route('/')
def main():
	id = random_question()
	return redirect(url_for('show_question', id=id))

@app.route('/question/<int:id>', methods=['GET', 'POST'])
def show_question(id):
	for key in ['points', 'total', 'combo']:
		if key not in session:
			session[key] = 0
	context = {}
	context['next'] = random_question()
	try:
		question = questions[id]
		context['question'] = question
	except IndexError:
		context['error'] = 'Fant ikke spørsmålet'
		return render_template('question.html', **context)
	if request.method == 'POST':
		answer = request.form.get('answer', None)
		if answer:
			context['success'] = int(answer) == question['correct']
			session['points'] += int(context['success'])
			session['total'] += 1
			if not context['success']:
				session['combo'] = 0
			else:
				session['combo'] += 1
		else:
			context['error'] = 'Blankt svar'
	return render_template('question.html', **context)

def random_question():
	return random.randint(0, len(questions) - 1)

if __name__ == '__main__':
	app.debug = True
	app.run()
