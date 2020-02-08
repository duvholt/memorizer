FROM python:3.6-slim-buster

RUN pip install pipenv

WORKDIR /app

COPY Pipfile ./
COPY Pipfile.lock ./

RUN pipenv install --deploy --system && rm -r ~/.cache

COPY app.py .
COPY main.py .
COPY memorizer/ memorizer/
COPY migrations/ migrations/

EXPOSE 8000

CMD gunicorn -b0.0.0.0:8000 app:app
