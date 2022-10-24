from config.default import *

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'optics.db'))
SQLALCHEMY_TRACK_MODIFICATION = False
SECRET_KEY = b'\x0c6\xcd\x93\xe1\xe9\xa7\xb2A\xf7\xb9\xc2\xaa\x8evf'