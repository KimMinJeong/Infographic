from flask import Flask, render_template, request, g, session, flash, redirect, \
    url_for, jsonify, json
from flask_openid import OpenID
from functools import wraps
from os import environ
from os.path import dirname, join
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import functions
from sqlalchemy.types import DateTime, Boolean
import hashlib
import os
import urllib
import json, requests


app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','post')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/editor', methods=['GET'])
def editor():
    return render_template('tool.html')


@app.route('/test', methods=['GET'])
def test():
    return render_template('test.html')

@app.route('/test2',methods=['GET'])
def test2():
    return render_template('t2.html')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0', port=int(environ.get('PORT',5000)))