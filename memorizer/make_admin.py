from flask_script import Command, Option

from memorizer import models
from memorizer.database import db


class AdminCommand(Command):
    'Make user administrator'

    option_list = (
        Option('username', type=str, help='Username of user to make admin'),
    )

    def run(self, username):
        user = models.User.query.filter_by(username=username).first()
        if not user:
            print(f"Did not find a user with username {username}")
            return
        user.admin = True
        db.session.add(user)
        db.session.commit()
        print(f"{username} is now an administrator")
