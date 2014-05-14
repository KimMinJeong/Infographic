from flask import Flask, render_template, request, g, session, flash, redirect, \
    url_for, jsonify, json
from flask.ext.sqlalchemy import SQLAlchemy
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
import logging

app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1111@localhost:5432/infographic'
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = os.urandom(24)
app.config.from_envvar('FLASKR_SETTING', silent=True)


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

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/editor', methods=['GET'])
def editor():
    return render_template('tool.html')


@app.route('/test', methods=['GET'])
def test():
    return render_template('test.html')

@app.route('/test2',methods=['GET'])
def test2():
    return render_template('t2.html')


@app.route('/signup',methods=['POST']) 
def signup():
    email = request.form["email"]
    name = request.form["name"]
    password = request.form["password"]
    db_insert = User(email, name, password)
    db.session.add(db_insert)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    login = User.query.get(id)
    error = None
    if request.method == 'POST':
        if request.form['login_email'] != login.email:
            error = 'Invalid Username'
        elif request.form['login_pwd'] != login.password:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('nav_top.html', error=error)   
 
 
@app.route('/logout')
def logout():
    session.pop()
    return redirect('/index')
    
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=int(environ.get('PORT',5000)))