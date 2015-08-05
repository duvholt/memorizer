import os
from datetime import timedelta

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
SECRET_KEY = 'rebumd8xvrywgkvufsnrtvji7fyjeu4tue'
PERMAMENT_SESSION_LIFETIME = timedelta(days=60)  # around two months
ADMIN_PASSWORD = 'password'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(PROJECT_PATH, 'memorizer.db')

# Cache
CACHE_TIME = 60 * 60 * 2 # 2 hours, pretty arbitrary
CACHE_TYPE = 'simple'

try:
    from localconfig import *
except ImportError:
    pass
