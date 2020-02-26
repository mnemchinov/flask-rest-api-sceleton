import os
import datetime

# region APP

APP_SERVER_HOST = "0.0.0.0"
APP_SERVER_PORT = 8001
APP_SERVER_LOG = "api_server.log"
APP_DIR = os.path.abspath(os.path.dirname(__file__))
DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(APP_DIR, 'app.db?check_same_thread=False')
SQLALCHEMY_MIGRATE_REPO = os.path.join(APP_DIR, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

EMPTY_DATE = datetime.datetime(1, 1, 1, 0, 0, 0)
DATE_FORMAT = "%d.%m.%Y %H:%M:%S"

# endregion

