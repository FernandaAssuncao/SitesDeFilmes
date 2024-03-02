from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)

app.config['SECRET_KEY'] = '6134c6b4b65537f51d38fea0a04d2f6a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///filmes.db'

database = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para visualizar essa pagína!'
login_manager.login_message_category = 'alert-info'

from PartyTv import routes
