from flask import Flask
app = Flask(__name__)
from questions import questions 
import random
@app.route('/')
def main():
	question = random.choice(questions)
	return question['question']

if __name__ == '__main__':
	app.debug = True
	app.run()
