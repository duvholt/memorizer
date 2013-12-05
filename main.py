from questions import questions 
from flask import Flask, render_template, redirect, url_for, request, session
from werkzeug.contrib.fixers import ProxyFix
import random

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.wsgi_app = ProxyFix(app.wsgi_app)

@app.route('/')
def main():
	return redirect(url_for('show_question', id=random_id()))

@app.route('/reset')
def reset_stats():
	session.clear()
	return redirect(request.referrer or url_for('main'))

@app.route('/question/<int:id>', methods=['GET', 'POST'])
def show_question(id):
	for key in ['points', 'total', 'combo']:
		if key not in session:
			session[key] = 0
	if 'earlier_questions' not in session:
		session['earlier_questions'] = []
	context = {
		'id': id,
		'alerts': [],
		'random': random_id(id),
		'prev': id - 1 if id - 1 >= 0 else len(questions) - 1,
		'next': id + 1 if id + 1 < len(questions) else 0
	}
	try:
		question = questions[id]
		context['question'] = question
	except IndexError:
		context['alerts'].append({'msg': 'Fant ikke spørsmålet', 'level': 'danger'})
		return render_template('question.html', **context)
	if request.method == 'POST':
		answer = request.form.get('answer')
		if answer:
			context['success'] = int(answer) == question['correct']
			if id not in session['earlier_questions']:
				session['points'] += int(context['success'])
				session['total'] += 1
				session['earlier_questions'].append(id)
				if not context['success']:
					session['combo'] = 0
				else:
					session['combo'] += 1
			elif context['success']:
				context['alerts'].append({'msg': 'Du har allerede svart på dette spørsmålet så du får ikke noe poeng. :-)', 'level': 'info'})
		else:
			context['alerts'].append({'msg': 'Blankt svar', 'level': 'danger'})
	return render_template('question.html', **context)

def random_id(id=None):
	rand = id
	earlier = session.get('earlier_questions', [])
	while rand == id and (not rand or rand in earlier):
		rand = random.randint(0, len(questions) - 1)
	return rand

if __name__ == '__main__':
	app.run()
