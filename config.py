DEBUG = False
SECRET_KEY = 'rebumd8xvrywgkvufsnrtvji7fyjeu4tue'
SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'

try:
    from localconfig import *
except ImportError:
    pass
