import json
import urllib2
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, jsonify
from decorators import crossdomain
from werkzeug.datastructures import MultiDict
import re,datetime
from app import app,db
import models

def notifyDevices(message):
  devices = models.Device.query.all()
  if len(devices) > 0:
    devices = [d.device_id for d in devices]
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

@app.route('/goals', methods = ['GET'])
@crossdomain(origin='*', headers='Content-Type')
def get_goals():
  goals = models.Goal.query.order_by(models.Goal.date_created).all()
  goals = [dict(id=goal.id, description=goal.description, done=goal.done, feedback=goal.feedback, date_created=goal.date_created.isoformat()) for goal in goals]
  return json.dumps(goals)

@app.route('/goals', methods = ['POST'])
@crossdomain(origin='*', headers='Content-Type')
def post_goals():
  description = request.json['description']
  goal = models.Goal(description)
  db.session.add(goal)  
  db.session.commit() 
  notifyDevices("todo")
  return ""   

@app.route('/goals/today', methods = ['GET'])
@crossdomain(origin='*', headers='Content-Type')
def get_goals_today():
  today = datetime.date.today()
  tomorrow = today+datetime.timedelta(days=1)
  goals = models.Goal.query.filter(models.Goal.date_created >= today).filter(models.Goal.date_created < tomorrow).order_by(models.Goal.date_created).all()
  goals = [dict(id=goal.id, description=goal.description, done=goal.done, feedback=goal.feedback, date_created=goal.date_created.isoformat()) for goal in goals]
  return json.dumps(goals)

@app.route('/goals/<int:goal_id>', methods = ['GET'])
@crossdomain(origin='*', headers='Content-Type')
def get_goal(goal_id):
  goal = models.Goal.query.get_or_404(goal_id)
  goal = dict(id=goal.id, description=goal.description, done=goal.done, feedback=goal.feedback, date_created=goal.date_created.isoformat())
  return json.dumps(goal)    

@app.route('/goals/<int:goal_id>', methods = ['PUT','OPTIONS'])
@crossdomain(origin='*',headers='Content-Type')
def update_goal(goal_id):
  goal = models.Goal.query.get_or_404(goal_id)
  goal.description = request.json['description']
  goal.done = request.json['done']
  goal.feedback = request.json['feedback']
  db.session.commit() 
  return ""            

@app.route('/goals/<int:goal_id>', methods = ['DELETE','OPTIONS'])
@crossdomain(origin='*',headers='Content-Type')
def delete_goal(goal_id):
  goal = models.Goal.query.get_or_404(goal_id)
  db.session.delete(goal)
  db.session.commit()
  return ""   

@app.route('/register_device', methods = ['POST'])
@crossdomain(origin='*',headers='Content-Type')
def register_device():
  print 'Registering new device'
  device_id = re.sub('["]', '', request.data)
  print device_id
  goal = models.Device.get(device_id)
  if goal == None:
    goal = models.Device(device_id)
    db.session.add(goal)
    db.session.commit()
  return ""    

@app.route('/')
def index():
   return "Welcome to the Franklyn Server 0.1"