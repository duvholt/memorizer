Memorizer
=========

[![Build Status](https://travis-ci.org/duvholt/memorizer.svg?branch=master)](https://travis-ci.org/duvholt/memorizer)
[![codecov](https://codecov.io/gh/duvholt/memorizer/branch/master/graph/badge.svg)](https://codecov.io/gh/duvholt/memorizer)

Memorizer is a webapp written in Python 3 using Flask and SQLAlchemy meant to be used for answering multiple choice questions.
It was created specifically for answering older multiple choice exams. 

Currently running on https://memorizer.io/

**Warning for users who want to adopt this project**:

This project has been used as playground for me (duvholt) to experiment with different implemenations.
The whole project is built upon the reinvent-the-wheel principle. I have deliberately avoided to build the app on big frameworks (well expect for SQLAlchemy - because who would want to deal with that mess). A good example of this is the homebrewed templating framework used to dynamically update the site. 

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

- Requires pipenv to be installed


```bash
$ pipenv install # Install requirements
$ ./main.py db upgrade # Create/upgrade database tables
$ ./main.py import questions/*.json # Import all questions (Warning: super slow if using SQLite)
$ ./main.py runserver # Run webserver
```


###Local config

To overwrite configuration in memorizer/config.py create an new file called memorizer/localconfig.py.

Example: 

```python
DEBUG = True
GOOGLE_ANALYTICS = 'UA-XXXXXXXX-Y'
SQLALCHEMY_DATABASE_URI = 'postgresql://username@localhost/memorizer'
```

Big thanks to all the [contributors](https://github.com/cXhristian/memorizer/graphs/contributors)!
