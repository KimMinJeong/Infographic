# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, g, session, flash, redirect, \
    url_for, jsonify, json
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.login import login_user, logout_user, current_user, login_required
from functools import wraps
from os import environ
from os.path import dirname, join
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import functions
from sqlalchemy.types import DateTime, Boolean
from sqlalchemy import create_engine
import hashlib
import os
import urllib
import json, requests
import socket


app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1111@localhost:5432/infographic'
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = os.urandom(24)
app.config.from_envvar('FLASKR_SETTING', silent=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = u"Please log in to access this page"
login_manager.session_protection = "strong"


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True)
    name = db.Column(db.String(20), unique=False)
    password = db.Column(db.String(30),unique=False)
    posts = db.relationship('Post', backref='author',
                            cascade="all, delete-orphan", passive_deletes=True)
    comments = db.relationship('Comment', backref='user', 
                               cascade="all, delete-orphan", passive_deletes=True)
                           
    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password = password
        
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return unicode(self.id)
    

    def __repr__(self):
        return "<User id={0!r}, email={1!r}, name={2!r}, password={3!r}>".\
                format(self.id, self.email, self.name, self.password)
                

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(Integer, primary_key=True)
    subject = db.Column(db.String(50))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(DateTime(timezone=True),
                           nullable=False, 
                           default=functions.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'))
    
    
    def __init__(self, subject, content, user_id):
        self.subject = subject
        self.content = content
        self.user_id = user_id
        
    def __repr__(self):
        return "<Post id={0!r}, subject={1!r}, user_id={2!r}>".\
                format(self.id, self.subject, self.user_id)
                

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id',ondelete='cascade'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id',ondelete='cascade'))
    created_at = db.Column(DateTime(timezone=True), 
                           nullable=True, 
                           default=functions.now())
    
    def __init__(self, comment, user_id, post_id):
        self.comment = comment
        self.user_id = user_id
        self.post_id = post_id
    
    def __repr__(self):
        return "<Comment id={0!r}, comment={1!r}, user_id={2!r}, post_id{3!r}>".\
                format(self.id, self.comment, self.user_id, self.post_id)


db.session.commit()
@app.route('/t2', methods=['GET'])
def t2():
    return render_template('t2.html')


@app.before_request
def before_request():
    if not session.get('user_email') is None:
        g.user = User.query.filter_by(email=session.get('user_email')).first()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/signup', methods=['POST']) 
def signup():
    email = request.form["email"]
    name = request.form["name"]
    password = request.form["password"]
    db_insert = User(email, name, password)
    db.session.add(db_insert)
    db.session.commit()
    flash(u'You were signed in')
    return redirect(url_for('login_page'))


@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


@app.route('/login_page', methods=['GET'])
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html',)
    email = request.form['login_email']
    password = request.form['login_pwd']
    registered_user = User.query.filter_by(email=email, password=password).first()
    if registered_user is None:
        flash(u'Email or Password is invalid', 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    print "login"
    session['user_email'] = email
    flash(u'Logged in successfully')
    return redirect(request.args.get('next') or url_for('index'))
   
   
@app.route('/editor', methods=['POST'])
@login_required
def editor():
    subject = request.form["subject"]
    return render_template('editor.html', subject=subject)

    
@app.route('/editor', methods=['POST'])
def insertInfo():
    content = request.form["content"]   
    user_id = g.user.id
    db_insert = Post(content, user_id)
    db.session.add(db_insert)
    db.session.commit()    
    return redirect(url_for('savedInfo', id=db_insert.id))


@app.route('/savedInfo', methods=['POST'])
@login_required
def savedInfo():
    subject = request.form["subject"]
    return render_template('savedInfo.html', subject=subject)
    
    
@app.route('/activation')
@login_required
def user_infomation():
    active = User.query.filter_by(email=session.get('user_email')).first()
    return render_template('user_infomation.html', acitve=active)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_email', None)
    return redirect(url_for('index'))
    
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=int(environ.get('PORT',5000)))