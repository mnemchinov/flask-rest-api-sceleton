import logging

from flask import Flask
from flask_migrate import Migrate
from flask_restful import reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

from Config import APP_SERVER_LOG

app = Flask(__name__)
app.config.from_object('Config')
logging.basicConfig(filename=APP_SERVER_LOG)

db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)

ma = Marshmallow(app)
ma.init_app(app)

parser = reqparse.RequestParser()
