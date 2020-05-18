import logging

import pymysql
from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from Config import APP_SERVER_LOG, APP_SERVER_HOST, APP_SERVER_PORT, DEBUG

pymysql.install_as_MySQLdb()
app = Flask(__name__)
app.config.from_object('Config')
app.host = APP_SERVER_HOST
app.port = APP_SERVER_PORT
app.debug = DEBUG
logging.basicConfig(filename=APP_SERVER_LOG)

db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

ma = Marshmallow(app)
ma.init_app(app)
