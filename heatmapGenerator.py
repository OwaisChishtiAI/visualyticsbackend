import pymongo
from datetime import datetime
import time
import sys

class Listener:
	def __init__(self):
		myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		self.db = myclient["customer_heat"]
		self.quarters = {}
		for i in range(1, 23):
			self.quarters['Q'+str(i)] = 0
		self.initial_date = datetime.strptime("1990-01-30 01:01:01.0001", "%Y-%m-%d %H:%M:%S.%f")
		self.boolean = True
		# self.initial_date = datetime.strptime("2020-04-27T19:29:29.263Z".replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S.%f")

	def listen(self):
		# rois = list(self.db.camera01.find().limit(10))
		rois = list(self.db.camera01.find({
			"timestamp": {"$gt" : self.initial_date},
			}).limit(10))
		if rois != []:
			self.initial_date = rois[-1]["timestamp"]
			# print(len(rois), rois[-1]["timestamp"])
			for each in rois:
				for every in each["ROI"]:
					self.quarters[every]+=1
			self.boolean = True
		else:
			self.boolean = False
		# print("[Info] Verbal Heat Map ", self.quarters)

	def record(self):
		if self.boolean:
			try:
				if "_id" in self.quarters.keys():
					del self.quarters['_id']
				self.db.camera01_chart.insert_one(self.quarters)
				print("[Info] Data Inserted INTO camera01_chart")
			except Exception as e:
				print(str(e))
				print(self.quarters)
				print("[Info] Avoiding Duplication")
			


l = Listener()	
while(1):
	l.listen()
	l.record()
	time.sleep(5)