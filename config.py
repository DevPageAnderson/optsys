import os

BASE_DIR = os.path.dirname(__file__)

SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'optics.db'))
SQLALCHEMY_TRACK_MODIFICATION = False
SECRET_KEY = 'dev'