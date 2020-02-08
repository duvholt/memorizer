from datetime import timedelta
from os import pardir
from os.path import abspath, dirname, join
from decouple import config

PROJECT_PATH = abspath(join(dirname(__file__), pardir))

DEBUG = config('MEMORIZER_DEBUG', False)
SECRET_KEY = config('MEMORIZER_SECRET_KEY', 'super-secret')
PERMAMENT_SESSION_LIFETIME = timedelta(days=60)  # around two months

SQLALCHEMY_DATABASE_URI = config('MEMORIZER_DB', 'sqlite:///' + join(PROJECT_PATH, 'memorizer.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False

GOOGLE_ANALYTICS = config('MEMORIZER_GOOGLE_ANALYTICS', None)

# Cache
CACHE_TIME = 60 * 60 * 2  # 2 hours, pretty arbitrary
CACHE_TYPE = config('MEMORIZER_CACHE_TYPE', 'simple')
# If redis is used
CACHE_REDIS_URL = config('MEMORIZER_REDIS_URL', 'redis://localhost:6379')
