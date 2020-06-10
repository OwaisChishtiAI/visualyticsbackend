import cv2
import time
from datetime import datetime
import pymongo
from hum_dist import Human
#from hum_dist import detect
import pdb


class mongoDB:
	def __init__(self):
		self.client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
		self.db = self.client["camera01_roi"]
		self.human_info = self.db["camera01_roi_heatmap"]
		#self.frame_count = frame_count
	
	def find(self):
		results = self.human_info.find({})
		for result in results:
			if result:
				centerX =  result["centerX"]
				centerY =  result["centerY"]
				date = result["lastModified"]
				frame = result["frame_count"]
			else:
				return False
			return centerX, centerY, date, frame
	
	def insert(self, x, y, frame_count):
		record = {
					"centerX": x,
					"centerY": y,
					"frame_count": frame_count,
					"lastModified": datetime.now()
		}
		self.human_info.insert_one(record)
		print("Inserted")

	def update(self, x, y, frame_count, prev_frame, prev_x, prev_y):
		if (frame_count<prev_frame) or (frame_count==prev_frame):
			frame_count += prev_frame
			x.extend(prev_x)
			y.extend(prev_y)
		self.human_info.update_one(
		{"frame_count":prev_frame},
		{"$set":{"centerX": x,
				"centerY": y,
				"frame_count": frame_count,
				"lastModified": datetime.now()}}
		)
		print("Updated")

	def human(self, minutes_threshold):
		x_axis = []; y_axis = []
		frame_count = 1
		vs = cv2.VideoCapture("../images/shelf_video.mp4")
		
		while True:
			
			(grabbed, frame) = vs.read()
			
			if not grabbed:
				break
			else:
				cv2.imshow("image", frame)
				if cv2.waitKey(10) & 0xFF == ord('q'):
					quit()
				t = datetime.now()
				if t.second % 10 == 0:
					human = Human()
					frame = cv2.resize(frame, (512, 512), interpolation=cv2.INTER_AREA)
					center, bbox = human.detect(frame)
					try:
						center = list(zip(*center))
						x_axis.extend(center[0])
						y_axis.extend(center[1])
						print(frame.shape)
					
					try:
						prev_x, prev_y, result, prev_frame = self.find()
					except:
						result = None
					
					if (result==False) or (result is None):
						self.insert(x_axis, y_axis, frame_count)
					elif abs(datetime.now() - result).days > 0:
						self.insert(x_axis, y_axis, frame_count)
					else:
						self.update(x_axis, y_axis, frame_count, prev_frame, prev_x, prev_y)
					cv2.imwrite('frame.jpg', frame)
					except:
						pass
					
			if frame_count % 20 == 0:
				time.sleep(1)
			frame_count += 1
			# print("[Info] Frames ", frame_count)
				# time.sleep(minutes_threshold*60)
			

				
if __name__ == "__main__":
	#pdb.set_trace()
	db = mongoDB()
	db.human(minutes_threshold=0.17)