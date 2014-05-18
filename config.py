import os

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
SECRET_KEY = 'rebumd8xvrywgkvufsnrtvji7fyjeu4tue'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(PROJECT_PATH, 'memorizer.db')

try:
    from localconfig import *
except ImportError:
    pass
