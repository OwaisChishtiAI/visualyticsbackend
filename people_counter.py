# import the necessary packages
from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
from imutils.video import VideoStream
from imutils.video import FPS
from detect import *
from tensorflow import keras
#from deepface import DeepFace
#from fer import FER
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
import pdb
import pymongo
from datetime import datetime

faceNet, ageNet, genderNet, counterNet, model = load_model()
human_counter, human_demo = db_init()

input = r"./videos/example_04.mp4"
output = None
confidence = 0.4
skip_frames = 30

# initialize the list of class labels MobileNet SSD was trained to detect
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]

if len(input) == 0:
	vs = cv2.VideoCapture(0)
else:
	vs = cv2.VideoCapture(input)

W = None
H = None

# instantiate our centroid tracker, then initialize a list to store
# each of our dlib correlation trackers
ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
trackers = []
trackableObjects = {}

totalFrames = 0
totalDown = 0
totalUp = 0

# start the frames per second throughput estimator
fps = FPS().start()
counter = {}
demo = {}
cont = False
cont2 = False

while True:
	grabbed, frame = vs.read()
	if not grabbed:
		break

	frame = imutils.resize(frame, width=500)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

	if W is None or H is None:
		(H, W) = frame.shape[:2]

	status = "Waiting"
	rects = []
	if totalFrames % skip_frames == 0:
		status = "Detecting"
		trackers = []

		blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
		counterNet.setInput(blob)
		detections = counterNet.forward()

		# loop over the detections
		for i in np.arange(0, detections.shape[2]):
			confidence_ = detections[0, 0, i, 2]
			if confidence_ > confidence:
				idx = int(detections[0, 0, i, 1])
				if CLASSES[idx] != "person":
					continue

				# compute the (x, y)-coordinates of the bounding box
				box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
				(startX, startY, endX, endY) = box.astype("int")

				# construct a dlib rectangle object from the bounding
				# box coordinates and then start the dlib correlation
				# tracker
				tracker = dlib.correlation_tracker()
				rect = dlib.rectangle(startX, startY, endX, endY)
				tracker.start_track(rgb, rect)
				trackers.append(tracker)

	else:
		# loop over the trackers
		for tracker in trackers:
			status = "Tracking"

			# update the tracker and grab the updated position
			tracker.update(rgb)
			pos = tracker.get_position()

			# unpack the position object
			startX = int(pos.left())
			startY = int(pos.top())
			endX = int(pos.right())
			endY = int(pos.bottom())

			# add the bounding box coordinates to the rectangles list
			rects.append((startX, startY, endX, endY))

	# draw a horizontal line in the center of the frame 
	cv2.line(frame, (0, H // 2), (W, H // 2), (0, 255, 255), 2)

	# use the centroid tracker to associate the (1) old object
	# centroids with (2) the newly computed object centroids
	objects = ct.update(rects)
	
	# loop over the tracked objects
	for (objectID, centroid) in objects.items():
		# check to see if a trackable object exists 
		to = trackableObjects.get(objectID, None)

		if to is None:
			to = TrackableObject(objectID, centroid)

		else:
			# the difference between the y-coordinate of the *current*
			# centroid and the mean of *previous* centroids will tell
			# us in which direction the object is moving (negative for
			# 'up' and positive for 'down')
			y = [c[1] for c in to.centroids]
			direction = centroid[1] - np.mean(y)
			to.centroids.append(centroid)

			# check to see if the object has been counted or not
			if not to.counted:
				if direction < 0 and centroid[1] < H // 2:
					totalUp += 1
					to.counted = True
				elif direction > 0 and centroid[1] > H // 2:
					totalDown += 1
					to.counted = True
					
				#pdb.set_trace()
				try:
					inside, outside, date = get_counter(human_counter)
				except:
					inside=None; outside=None; date=None
				try:
					if len(date)==0:
						counter["inside"] = totalDown
						counter["outside"] = totalUp
						counter["_id"] = datetime.now()
						print("Counter: ", counter)
						human_counter.insert_one(counter)
						print("Inserted")
						cont = True
					elif abs(date[-1]-datetime.now()).days == 0:
						if (cont == True) and (totalDown not in inside or totalUp not in outside):
							counter["inside"] = totalDown
							counter["outside"] = totalUp
							counter["_id"] = datetime.now()
							print("Counter: ", counter)
							human_counter.insert_one(counter)
							print("Inserted")
						elif (cont == False) and (max(inside)>totalDown or max(outside)>totalUp):
							counter["inside"] = totalDown+inside
							counter["outside"] = totalUp+outside
							counter["_id"] = datetime.now()
							print("Counter: ", counter)
							human_counter.insert_one(counter)
							print("Inserted")
							cont = True
					elif (datetime.now()-date[-1]).days > 0:
						counter["inside"] = totalDown+inside
						counter["outside"] = totalUp+outside
						counter["_id"] = datetime.now()
						print("Counter: ", counter)
						human_counter.insert_one(counter)
						print("Inserted")
						cont = True
				except:
					pass

		# store the trackable object in our dictionary
		trackableObjects[objectID] = to
					
		# draw both the ID of the object and the centroid of the
		# object on the output frame
		text = "ID {}".format(objectID)
		cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
		cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

	# construct a tuple of information we will be displaying on the frame
	info = [
		("Outside", totalUp),
		("Inside", totalDown),
		("Status", status),
	]
	
	# 1.Face Detection
	padding=20
	frame, faceBoxes = detect_face(faceNet,frame)
		
	if faceBoxes:
		for faceBox in faceBoxes:
			face=frame[max(0,faceBox[1]-padding):
					   min(faceBox[3]+padding,frame.shape[0]-1),max(0,faceBox[0]-padding)
					   :min(faceBox[2]+padding, frame.shape[1]-1)]
			
			# 2.Gender Detection
			gender = detect_gender(face, genderNet)
			print(f'Gender: {gender}')

			# 3.Age Detection
			age = detect_age(face, ageNet)
			print(f'Age: {age[1:-1]} years')
			
			# 3.Emotion Detection
			emotion, score = detect_emotion(face, model)
			
			#pdb.set_trace()
			try:
				_id, date, _ids = get_demo(human_demo)
			except:
				_id = None; date = None; _ids = None
			
			try:
				if (_id is None):
					demo["_id"] = objectID
					demo["gender"] = gender
					demo["age"] = age[1:-1]
					demo["emotion"] = emotion
					demo["datetime"] = datetime.now()
					print("Demographics: : ", demo)
					human_demo.insert_one(demo)
					print("Inserted")
					cont2 = True
				elif abs(date-datetime.now()).days == 0:
					if cont2 == True:
						if objectID not in _ids:
							demo["_id"] = objectID
							demo["gender"] = gender
							demo["age"] = age[1:-1]
							demo["emotion"] = emotion
							demo["datetime"] = datetime.now()
							#print("Demographics: : ", demo)
							human_demo.insert_one(demo)
							print("Inserted")
							cont2 = True
						else:
							pass
					else:
						if objectID not in _ids:
							demo["_id"] = objectID
							demo["gender"] = gender
							demo["age"] = age[1:-1]
							demo["emotion"] = emotion
							demo["datetime"] = datetime.now()
						else:
							demo["_id"] = _id+1
							demo["gender"] = gender
							demo["age"] = age[1:-1]
							demo["emotion"] = emotion
							demo["datetime"] = datetime.now()
						#print("Demographics: : ", demo)
						human_demo.insert_one(demo)
						print("Inserted")
						cont2 = True
			except:
				pass

			cv2.putText(frame, f'{gender}, {age}, {emotion}',(faceBox[0], faceBox[1]-10), 
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2, cv2.LINE_AA)	
			
	
	# loop over the info tuples and draw them on our frame
	for (i, (k, v)) in enumerate(info):
		text = "{}: {}".format(k, v)
		cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
			cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break

	totalFrames += 1
	fps.update()

# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))


if len(input) == 0:
	vs.stop()
else:
	vs.release()

# close any open windows
cv2.destroyAllWindows()