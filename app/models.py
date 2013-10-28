from app import db
import datetime
import json

class Goal(db.Model):

	id = db.Column(db.Integer, primary_key=True)
	description = db.Column(db.Text)
	done = db.Column(db.Boolean)
	feedback = db.Column(db.Text)
	date_created = db.Column(db.DateTime)

	def __init__(self, description):
		self.description = description
		self.done = None
		self.date_created = datetime.datetime.now()

	def __repr__(self):
		return '<Goal %r>' % (self.description)

class Device(db.Model):

	device_id = db.Column(db.Text, primary_key=True)

	def __init__(self, device_id):
		self.device_id = device_id

