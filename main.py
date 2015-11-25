#!/usr/bin/env python3
from memorizer.application import app, manager

if __name__ == '__main__':
    if app.debug:
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension(app)
    manager.run()
