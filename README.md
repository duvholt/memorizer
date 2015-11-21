Memorizer
=========

Memorizer is a webapp written in Python 3 using Flask and SQLAlchemy meant to be used for answering multiple choice questions.
It was created specifically for answering older multiple choice exams. 

Currently running on https://memorizer.io/

Features
--------

- Multiple choice answering
- Support for several categories with subcategories (courses and exams)
- Statistics about answered questions
- Correct answer combo
- Random question which will select an unanswered question if possible
- Keyboard support
  - Left/right arrows (or a/d) for previous/next question
  - 1, 2, 3, 4 to select answer
  - Space (or q) to answer
  - r to load a random question


Installation
------------

- Create a virtualenv for Python 3 (virtualenv is highly recommended).


```bash
$ pip install -r requirements.txt # Install requirements
$ ./setup.py # Create database tables
$ ./import questions/*.json # Import all questions (Warning: super slow if using SQLite)
$ ./main.py # Run webserver
```

- Create localconfig.py for a local config:

Example: 

```python
DEBUG = True
GOOGLE_ANALYTICS = 'UA-XXXXXXXX-Y'
SQLALCHEMY_DATABASE_URI = 'postgresql://username@localhost/memorizer'
```

Big thanks to all the [contributors](https://github.com/cXhristian/memorizer/graphs/contributors)!
