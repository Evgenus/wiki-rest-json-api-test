from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('wikiapi.config')
app.config.from_pyfile('application.cfg', silent=True)
db = SQLAlchemy(app)

from wikiapi import views