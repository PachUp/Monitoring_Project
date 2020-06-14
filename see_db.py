from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users160.db'
db = SQLAlchemy(app)
class users(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.TEXT, unique=True)
        password = db.Column(db.TEXT)
        email = db.Column(db.TEXT)
        level = db.Column(db.INTEGER) #level 1 - regular employee, level 2 - Team leader, level 3 - Manager
print(users.query.all()[0].password)  