#!/usr/bin/env python3
from main import app, db


print("Creating database tables...")
with app.app_context():
    db.create_all()

print("Run \"./import questions/*.json\" to import questions")
