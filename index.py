#-*- coding: utf-8 -*-

__author__ = 'djstrong'

from flask import Flask, render_template, request, Response, redirect, url_for
import sqlite3
import hashlib
from flask import g
import paramiko
from tasks import *
import colorsys

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
    c.execute("create table IF NOT EXISTS connections (id TEXT PRIMARY KEY, ip TEXT, user TEXT, password TEXT, task INT, last_result INT, name TEXT)")
    get_db().commit()

def hex_color(percent):
    r,g,b= colorsys.hsv_to_rgb(float(percent)/100*120/360,1.0,1.0)

    return '#%02x%02x%02x' % (int(255*r), int(255*g), int(255*b))

@app.route('/')
def index():
    get_cursor().execute("SELECT id,ip,user,password,task,last_result,name FROM connections ")
    rows = map(lambda (id,ip,user,password,task,last_result,name):[name,id,last_result, hex_color(last_result)],  get_cursor().fetchall())
    results = sorted(filter(lambda row: row[2]!='', rows), key=lambda row: row[2], reverse=True)

    #print results
    return render_template('index.html', results=results)


@app.route('/add', methods=['GET'])
def add():
    return render_template('add.html')


@app.route('/add', methods=['POST'])
def save():
    ip = request.form['ip']
    user = request.form['user']
    password = request.form['password']
    task = int(request.form['task'])
    name = request.form['name']
    id = hashlib.sha1(ip + user + password).hexdigest()

    get_cursor().execute("SELECT * FROM connections WHERE id='%s'" % (id,))

    row = get_cursor().fetchone()

    if not row:
        get_cursor().execute("INSERT INTO connections VALUES ('%s','%s','%s','%s','%d','','%s')" % (id, ip, user, password, task, name))
        get_db().commit()
    else:
        get_cursor().execute("UPDATE connections SET task='%d', last_result='',name='%s' WHERE id='%s'" % (task,name,id))
        get_db().commit()

    return redirect(url_for('.show', id=id))



def results_percentage(results):
    count=0
    for result, description in results:
        if result:
            count+=1
    return int(100.0*count/len(results))

@app.route('/show/<id>')
def show(id):
    get_cursor().execute("SELECT id,ip,user,password,task FROM connections WHERE id='%s'" % (id,))
    row = get_cursor().fetchone()
    id,ip,user,password,task = row
    tasks_class=globals()['Tasks%d'%task]
    tasks = tasks_class(ip,user,password)
    results = tasks.perform_tasks()
    result = results_percentage(results)
    #save result
    get_cursor().execute("UPDATE connections SET last_result='%d' WHERE id='%s'" % (result,id))
    get_db().commit()


    return render_template('show.html', results=results, result=result)

@app.route('/reset')
def reset():
    #TODO reset db
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)