import os
from flask import Flask, sessions
from flask import jsonify, Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from backend.variableDB import user, password, host, database, jwt_key, secret_key, email, password_email
from datetime import *
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
app.config['JWT_SECRET_KEY'] = jwt_key
app.config['SESSION_PERMANENT'] = True
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['UPLOAD_FOLDER'] = '/app/'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = f'{email}'
app.config['MAIL_PASSWORD'] = f'{password_email}'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

jwt = JWTManager(app)

api = Api(app)

db = SQLAlchemy(app)

CORS(app)
