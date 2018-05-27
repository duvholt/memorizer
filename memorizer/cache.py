from flask_caching import Cache

from memorizer.config import CACHE_REDIS_URL, CACHE_TYPE

cache = Cache(config={
    'CACHE_TYPE': CACHE_TYPE,
    'CACHE_KEY_PREFIX': 'memorizer',
    'CACHE_REDIS_URL': CACHE_REDIS_URL
})
