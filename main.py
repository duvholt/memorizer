from flask import Flask, render_template, redirect, url_for, request, session
from werkzeug.contrib.fixers import ProxyFix
import random
import json

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.wsgi_app = ProxyFix(app.wsgi_app)
with open('questions.json', encoding='utf-8') as f:
    questions = json.load(f)['questions']

@app.route('/')
def main():
    return redirect(url_for('show_question', id=random_id()))

@app.route('/reset')
def reset_stats():
    session.clear()
    return redirect(url_for('main'))

@app.route('/question/<int:id>', methods=['GET', 'POST'])
def show_question(id):
    if id == 0:
        return redirect(url_for('show_question', id=1))
    # Setting default value for session variables
    for key in ['points', 'total', 'combo']:
        if key not in session:
            session[key] = 0
    if 'answered' not in session:
        session['answered'] = []
    context = {
        'id': id,
        'alerts': [],
        'random': random_id(id - 1),
        'prev': id - 1 if id > 1 else len(questions),
        'next': id + 1 if id < len(questions) else 1,
        'num_questions': len(questions)
    }
    try:
        question = questions[id - 1]
    except IndexError:
        context['alerts'].append({'msg': 'Fant ikke spørsmålet', 'level': 'danger'})
        return render_template('question.html', **context)

    context['question'] = question
    context['answers'] = list(enumerate(question['answers']))
    # POST request when answering
    if request.method == 'POST':
        answer = request.form.get('answer')
        if answer:
            context['success'] = int(answer) == question['correct']
            # Checking if question has already been answered
            if id not in session['answered']:
                session['points'] += int(context['success'])
                session['total'] += 1
                session['answered'].append(id)
                if not context['success']:
                    session['combo'] = 0
                else:
                    session['combo'] += 1
            elif context['success']:
                context['alerts'].append({'msg': 'Du har allerede svart på dette spørsmålet så du får ikke noe poeng. :-)', 'level': 'info'})
        else:
            context['alerts'].append({'msg': 'Blankt svar', 'level': 'danger'})
        # Preserving order on submit
        ordering = request.form.get('order')
        if ordering:
            # Resorting answers from specific values. Answer is a tuple with id and texts
            context['answers'] = [(int(x), context['answers'][int(x)][1]) for x in ordering.split(',')]
    else:
        # Random order on questions
        random.shuffle(context['answers'])
    return render_template('question.html', **context)

def random_id(id=None):
    """Returns a random id from questions that have not been answered. Returns a complete random number if none available"""
    rand = id
    earlier = session.get('answered', [])
    # all questions have been answered
    if len(questions) == len(earlier) or (id not in earlier and len(questions) == len(earlier) + 1):
        return random.randint(0, len(questions) - 1)
    while rand in earlier or rand in [id, None]:
        rand = random.randint(0, len(questions) - 1)
    return rand

@app.context_processor
def utility_processor():
    def percentage(num, total):
        if total > 0:
            return round((num * 100) / total, 2)
        return 0
    return dict(percentage=percentage)

if __name__ == '__main__':
    app.run()
