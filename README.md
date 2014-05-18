Memorizer
=========

Memorizer is a webapp written in Python 3 using Flask and SQLAlchemy meant to be used for answering multiple choice questions.
It was created specifically for answering older multiple choice exams. 

Currently running on http://quiz.cxhristian.com/

Features
--------

- Multiple choice answering
- Support for several categories with subcategories (courses and exams)
- Statistics about answered questions
- Correct answer combo
- Random question which will select an unanswered question if possible
- Keyboard support
  - Left/right arrows for previous/next question
  - 1, 2, 3, 4 to select answer
  - Space to answer
- Currently supports the following courses:
  - TDT4110 (IT Grunnkurs)
  - TIØ4258 (Teknologiledelse)
  - MFEL1010 (Innføring i medisin for ikke-medisinere)
  - HLS0001 (Psykosomatikk og helsepsykologi)
- Works pretty decent on mobile thanks to Bootstrap 3


Installation
------------

- Create a virtualenv for Python 3 (virtualenv is highly recommended).


```bash
$ pip install -r requirements.txt # Install Flask and SQlAlchemy
$ ./import.py # Import questions to database
$ ./main.py # Run webserver
```

- Create localconfig.py for a local config:

Example: 
```python
DEBUG = True
GOOGLE_ANALYTICS = 'UA-XXXXXXXX-Y'
SQLALCHEMY_DATABASE_URI = 'postgresql://username@localhost/memorizer'
```



Contributors
------------

- Michael McMillan
  - Keyboard support
  - HLS0001 exams
- Marius Enerly
  - MFEL1010 exams
