import cv2
import api
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import pymongo
import time
import base64
import io
from imageio import imread

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["camera01_roi"]
collection = db["auth_faces"]

import math

def face_distance_to_conf(face_distance, face_match_threshold=0.6):
    if face_distance > face_match_threshold:
        range = (1.0 - face_match_threshold)
        linear_val = (1.0 - face_distance) / (range * 2.0)
        return linear_val
    else:
        range = face_match_threshold
        linear_val = 1.0 - (face_distance / (range * 2.0))
        return linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))

# cap = cv2.VideoCapture(0)

def extract_features(frame, name):
	landmarks = api.face_encodings(frame)[0]
	collection.insert_one({name : landmarks.tolist()})
	return landmarks

def main():
	while cap.isOpened():
		# try:
		ret,frame = cap.read()
		locs = api.face_locations(frame)
		if locs:
			for each in locs:
				top, right, bottom, left = locs[0]
				face_image = frame[top:bottom, left:right]

			if cv2.waitKey(10) & 0xFF == ord('s'):
				name = input("Name: \n")
				lnd = extract_features(face_image, name)

			if cv2.waitKey(10) & 0xFF == ord('p'):
				res = match_features(face_image)
				print(res)
				# quit()
		else:
			face_image = frame
		cv2.imshow("frame", face_image)
		if cv2.waitKey(10) & 0xFF == ord('q'):
			quit()
	cap.release()
	cv2.destroyAllWindows()

# main()

def isFaceCheck(frame, fileName):
	try:
		locs = api.face_locations(frame)
		landmarks = api.face_encodings(frame, num_jitters=50, model="large")[0]
		np.save("/root/vizStuff/face_data/{}.npy".format(fileName), landmarks)
		return True
	except:
		return False

def isSelfieCheck(frame):
	try:
		locs = api.face_locations(frame)
		landmarks = api.face_encodings(frame, num_jitters=50, model="large")[0]
		np.save("/root/vizStuff/face_data/selfie.npy", landmarks)
		return True
	except Exception as e:
		print(e)
		return False	

def isFace(frame):
	locs = api.face_locations(frame)
	if locs:
		top, right, bottom, left = locs[0]
		face_image = frame[top:bottom, left:right]
		# cv2.imshow("face", face_image)
		# cv2.waitKey(0)
		retval, buffer = cv2.imencode('.jpg', face_image)
		img = base64.b64encode(buffer)
		return img
		# print(img)

def imgConversion(baseString):
	im_bytes = base64.b64decode(baseString)   # im_bytes is a binary image
	im_file = io.BytesIO(im_bytes)  # convert image to file-like object
	img = Image.open(im_file)   # img is now PIL Image object
	open_cv_image = np.array(img) 
	# Convert RGB to BGR 
	open_cv_image = open_cv_image[:, :, ::-1].copy()
	
	return open_cv_image

def saveUserTodb(frame, name):
	landmarks = api.face_encodings(frame)[0]
	collection.insert_one({name : landmarks.tolist()})
	return True


def match_features(frame):
	landmarks = api.face_encodings(frame)[0]
	data = list(collection.find({}, {"_id" : 0}))
	for each in data:
		for key, val in each.items():
			val = np.array(val)
			res = api.compare_faces([val], landmarks)
			if res[0]:
				return key
	return ""


def face_percentage(ref, unk):
	res = api.face_distance([ref], unk)[0]
	return res

def evaluation():
	print("Evaluating...")
	results = {"nic-nic" : None, "nic-video" : [], "nicF-selfie" : None, "nicB-selfie" : None}
	nicF = np.load("/root/vizStuff/face_data/nicfront.npy")
	nicB = np.load("/root/vizStuff/face_data/nicback.npy")
	cap = cv2.VideoCapture("/root/vizStuff/face_data/video.mp4")
	selfie = np.load("/root/vizStuff/face_data/selfie.npy")
	results["nic-nic"] = face_percentage(nicF, nicB)
	results["nicF-selfie"] = face_percentage(nicF, selfie)
	results["nicB-selfie"] = face_percentage(nicB, selfie)
	frames = 0
	while cap.isOpened():
		try:
			ret,frame = cap.read()
			_ = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			if cv2.waitKey(10) & 0xFF == ord('q'):
				quit()
			try:
				if frames % 4 == 0:
					ifFace = api.face_encodings(frame, num_jitters=50, model="large")[0]
					perc = face_percentage(nicF, ifFace)
					results["nic-video"].append(perc)
			except Exception as e:
				pass
			
		except Exception as e:
			pass
			cap.release()
			cv2.destroyAllWindows()
			# pass
		frames += 1
		
			
	cap.release()
	cv2.destroyAllWindows()

	results["nic-video"] = sum(results["nic-video"]) / len(results["nic-video"])
	for key in results.keys():
		results[key] = round(face_distance_to_conf(results[key]) * 100)
	print("Evaluation Completed.")
	return results

# print(evaluation())
"ISR"



def testingAcc(img1, img2):
	img1 = cv2.imread(img1)
	img2 = cv2.imread(img2)
	img1 = api.face_encodings(img1, num_jitters=50, model="large")[0]
	img2 = api.face_encodings(img2, num_jitters=50, model="large")[0]
	res = api.face_distance([img1], img2)[0]
	print(res)
	print("Perc: ", face_distance_to_conf(res))

# testingAcc("frontCNIC.jpg", "mus1.jpg")


