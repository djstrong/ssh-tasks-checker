#-*- coding: utf-8 -*-

__author__ = 'djstrong'

from flask import Flask, render_template, request, Response, redirect, url_for
import sqlite3
import hashlib
from flask import g
import paramiko
from tasks import *

app = Flask(__name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('example.db')
    return db

def get_cursor():

    db = getattr(g, '_cursor', None)
    if db is None:
        db = g._cursor = get_db().cursor()
    return db

with app.app_context():
    c = get_cursor()
    # TODO create db
    c.execute("create table IF NOT EXISTS connections (id TEXT PRIMARY KEY, ip TEXT, user TEXT, password TEXT)")
    get_db().commit()


@app.route('/')
def index():
    #TODO present anonymous results
    return render_template('index.html')


@app.route('/add', methods=['GET'])
def add():
    return render_template('add.html')


@app.route('/add', methods=['POST'])
def save():
    ip = request.form['ip']
    user = request.form['user']
    password = request.form['password']
    id = hashlib.sha1(ip + user + password).hexdigest()

    get_cursor().execute("SELECT * FROM connections WHERE id='%s'" % (id,))

    row = get_cursor().fetchone()

    if not row:
        get_cursor().execute("INSERT INTO connections VALUES ('%s','%s','%s','%s')" % (id, ip, user, password))
        get_db().commit()

    return redirect(url_for('.show', id=id))

def check(ip,user,password,task):
    task(ip,user,password)



@app.route('/show/<id>')
def show(id):
    get_cursor().execute("SELECT ip,user,password FROM connections WHERE id='%s'" % (id,))
    row = get_cursor().fetchone()
    ip,user,password = row
    tasks = Tasks3(ip,user,password) #TODO define task
    results = tasks.perform_tasks()
    #TODO save results?
    return render_template('show.html', results=results)

@app.route('/reset')
def reset():
    #TODO reset db
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)