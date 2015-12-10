from os.path import abspath, dirname, join
from os import pardir
from datetime import timedelta

PROJECT_PATH = abspath(join(dirname(__file__), pardir))

DEBUG = False
SECRET_KEY = 'rebumd8xvrywgkvufsnrtvji7fyjeu4tue'
PERMAMENT_SESSION_LIFETIME = timedelta(days=60)  # around two months

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(PROJECT_PATH, 'memorizer.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Cache
CACHE_TIME = 60 * 60 * 2  # 2 hours, pretty arbitrary
CACHE_TYPE = 'simple'

try:
    from memorizer.localconfig import *
except ImportError:
    pass
