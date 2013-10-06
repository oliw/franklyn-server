#!flask/bin/python
import sqlite3
import json
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, jsonify
from decorators import crossdomain

# configuration
DATABASE = '/tmp/franklyn.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

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
  return ""   

@app.route('/goals/today', methods = ['GET'])
def get_goals_today():
   cur = g.db.execute("select id, description, done, feedback, date_created from goals where date_created = date('now') order by id desc")
   goals = [dict(id=row[0], description=row[1], done=row[2], feedback=row[3], date_created=row[4]) for row in cur.fetchall()]
   return jsonify({'goals': goals})

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

@app.route('/')
def index():
   return "Welcome to the Franklyn Server 0.1"

# this fires up the application if we want to run it as a standalone application
if __name__ == '__main__':
    app.run(debug = True)