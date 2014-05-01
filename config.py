DEBUG = False
SECRET_KEY = 'rebumd8xvrywgkvufsnrtvji7fyjeu4tue'

try:
    from localconfig import *
except ImportError:
    pass
