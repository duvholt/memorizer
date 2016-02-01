from flask.ext.cache import Cache

from memorizer.config import CACHE_TYPE

cache = Cache(config={'CACHE_TYPE': CACHE_TYPE})
