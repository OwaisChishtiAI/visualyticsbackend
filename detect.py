import cv2
import math
import argparse
import pymongo
import numpy as np
from tensorflow import keras
import pdb


def db_init():
	client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
	db = client["camera01_roi"]
	human_counter = db["human_counter"]
	human_demo = db["human_demo"]
	return human_counter, human_demo


def get_counter(human_counter):
	inside = []; outside = []; date = []
	results = human_counter.find({})
	for result in results:
		if result:
			inside.append(result["inside"])
			outside.append(result["outside"])
			date.append(result["_id"])
		else:
			inside = None
			outside = None
			date = None
			return inside, outside, date
	return inside, outside, date


def get_demo(human_demo):
	_ids = []
	results = human_demo.find({})
	for result in results:
		if result:
			_id = result["_id"]
			date = result["datetime"]
			_ids.append(_id)
		else:
			_id = None
			date = None
			_ids = None
			return _id, date, _ids
	return _id, date, _ids

	
def load_model():
	print("[INFO] loading model...")
	# Face Model
	faceProto = r"./model/face/opencv_face_detector.pbtxt"
	faceModel = r"./model/face/opencv_face_detector_uint8.pb"
	faceNet=cv2.dnn.readNet(faceModel,faceProto)
	# Age Model
	ageProto = r"./model/age/age_deploy.prototxt"
	ageModel = r"./model/age/age_net.caffemodel"
	ageNet=cv2.dnn.readNet(ageModel,ageProto)
	# Gender Model
	genderProto = r"./model/gender/gender_deploy.prototxt"
	genderModel = r"./model/gender/gender_net.caffemodel"
	genderNet=cv2.dnn.readNet(genderModel,genderProto)
	# Counter Model
	counter_prototxt = r"./mobilenet_ssd/MobileNetSSD_deploy.prototxt"
	counter_model = r"./mobilenet_ssd/MobileNetSSD_deploy.caffemodel"
	counterNet = cv2.dnn.readNetFromCaffe(counter_prototxt, counter_model)
	# Emotion Model
	model = keras.models.load_model("./model/emotion/model_35_91_61.h5")
	return faceNet, ageNet, genderNet, counterNet, model
		
	
def detect_face(net, frame, conf_threshold=0.7):
	frameOpencvDnn=frame.copy()
	frameHeight=frameOpencvDnn.shape[0]
	frameWidth=frameOpencvDnn.shape[1]
	blob=cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

	net.setInput(blob)
	detections=net.forward()
	faceBoxes=[]
	for i in range(detections.shape[2]):
		confidence=detections[0,0,i,2]
		if confidence>conf_threshold:
			x1=int(detections[0,0,i,3]*frameWidth)
			y1=int(detections[0,0,i,4]*frameHeight)
			x2=int(detections[0,0,i,5]*frameWidth)
			y2=int(detections[0,0,i,6]*frameHeight)
			faceBoxes.append([x1,y1,x2,y2])
			cv2.rectangle(frameOpencvDnn, (x1,y1), (x2,y2), (0,255,0), int(round(frameHeight/150)), 8)
	return frameOpencvDnn,faceBoxes


def detect_gender(face, genderNet):
	# Gender Detector
	MODEL_MEAN_VALUES=(78.4263377603, 87.7689143744, 114.895847746)
	genderList=['Male','Female']
	blob=cv2.dnn.blobFromImage(face, 1.0, (227,227), MODEL_MEAN_VALUES, swapRB=False)
	genderNet.setInput(blob)
	genderPreds=genderNet.forward()
	gender=genderList[genderPreds[0].argmax()]
	return gender


def detect_age(face, ageNet):
	# Age Detector
	MODEL_MEAN_VALUES=(78.4263377603, 87.7689143744, 114.895847746)
	ageList=['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
	blob=cv2.dnn.blobFromImage(face, 1.0, (227,227), MODEL_MEAN_VALUES, swapRB=False)
	ageNet.setInput(blob)
	agePreds=ageNet.forward()
	age=ageList[agePreds[0].argmax()]
	return age


def detect_emotion(face, model):
	# Emotion Detector
	emotion =  ['Anger', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
	gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
	fc = cv2.resize(gray, (48, 48))
	inp = np.reshape(fc,(1,48,48,1)).astype(np.float32)
	inp = inp/255.
	prediction = model.predict_proba(inp)
	em = emotion[np.argmax(prediction)]
	score = np.max(prediction)
	return em, score