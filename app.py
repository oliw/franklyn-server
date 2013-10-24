#!flask/bin/python
import sqlite3
import json
import urllib2
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, jsonify
from decorators import crossdomain
from werkzeug.datastructures import MultiDict
import re

# configuration
DATABASE = '/tmp/franklyn.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

GCM_API_KEY = "AIzaSyCjL0IFxGGz_cn-_t_iyu0AwnCltQY_3JE"

# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
   print app.config['DATABASE']
   return sqlite3.connect(app.config['DATABASE'])

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/goals', methods = ['GET'])
@crossdomain(origin='*', headers='Content-Type')
def get_goals():
   cur = g.db.execute('select id, description, done, feedback, date_created from goals order by id desc')
   goals = [dict(id=row[0], description=row[1], done=row[2], feedback=row[3], date_created=row[4]) for row in cur.fetchall()]
   return json.dumps(goals)

@app.route('/goals', methods = ['POST'])
@crossdomain(origin='*', headers='Content-Type')
def post_goals():
  g.db.execute("insert into goals (description,date_created) VALUES (?,date('now'))",[request.json['description']])
  g.db.commit()
  notifyDevices("todo")
  return ""   

@app.route('/goals/today', methods = ['GET'])
@crossdomain(origin='*', headers='Content-Type')
def get_goals_today():
   cur = g.db.execute("select id, description, done, feedback, date_created from goals where date_created = date('now') order by id desc")
   goals = [dict(id=row[0], description=row[1], done=row[2], feedback=row[3], date_created=row[4]) for row in cur.fetchall()]
   return json.dumps(goals)

@app.route('/goals/<int:goal_id>', methods = ['GET'])
@crossdomain(origin='*', headers='Content-Type')
def get_goal(goal_id):
   cur = g.db.execute("select id, description, done, feedback, date_created from goals where id = ? order by id desc" , [goal_id])
   row = cur.fetchone()
   if row == None:
      abort(404)
   goal = dict(id=row[0], description=row[1], done=row[2], feedback=row[3], date_created=row[4])
   return json.dump(goal)    

@app.route('/goals/<int:goal_id>', methods = ['PUT','OPTIONS'])
@crossdomain(origin='*',headers='Content-Type')
def update_goal(goal_id):
  g.db.execute("update goals set description = ?, done = ?, feedback = ? where id = ?",[request.json['description'],request.json['done'],request.json['feedback'],request.json['id']])
  g.db.commit()
  return ""            

@app.route('/goals/<int:goal_id>', methods = ['DELETE','OPTIONS'])
@crossdomain(origin='*',headers='Content-Type')
def delete_goal(goal_id):
   cur = g.db.execute("delete from goals where id = ?" , [goal_id])
   row = g.db.commit()
   return ""   

@app.route('/register_device', methods = ['POST'])
@crossdomain(origin='*',headers='Content-Type')
def register_device():
  print 'Registering new device'
  request.data = re.sub('["]', '', request.data)
  print request.data
  g.db.execute("insert or ignore into devices (device_id) VALUES (?)",[request.data])
  g.db.commit()
  return ""    

@app.route('/')
def index():
   return "Welcome to the Franklyn Server 0.1"

def notifyDevices(message):
  cur = g.db.execute("select device_id from devices")
  rows = cur.fetchall()
  if len(rows) > 0:
    devices = [row[0] for row in rows]
    data = {"goalsAddedForToday":True}
    ttl = 60*60*24
    msg = json.dumps({"registration_ids" : devices, "data" : data, "time_to_live" : ttl})

    clen = len(msg)
    headers = MultiDict()
    headers['Content-Type'] = 'application/json'
    headers['Content-Length'] = clen
    headers['Authorization'] = "key=" + GCM_API_KEY 

    req = urllib2.Request("https://android.googleapis.com/gcm/send", msg, headers)
    f = urllib2.urlopen(req)
    responseMsg = f.read()
    f.close()
    return responseMsg
  else:
    print 'No devices to notify'
    return



# this fires up the application if we want to run it as a standalone application
if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)