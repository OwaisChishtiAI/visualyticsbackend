from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import pymongo
import random
from markov_chain import markov
from aggregator import aggregator
import base64
from detectLive import *

app = Flask(__name__)
CORS(app)

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["camera01_roi"]

# @app.route("/mart", methods = ['GET'])
# def mrt():
# 	return render_template("index.html")

@app.route("/camera01_roi", methods=["GET"])
def camera01feed():
	data = list(db.camera01_roi.find({}, {"_id" : 0}))
	keys, values = [], []
	for i in data[0].items():
		keys.append(i[0])
		values.append(i[1])
	# print("#############################################", data)
	return jsonify({"keys":keys, "values":values})


@app.route('/camera01_roi_img')
def send_js():
    return app.send_static_file("/root/vizStuff/images/empty_shelf_annotated.jpg")

@app.route('/camera01_hm_img')
def send_js2():
    return app.send_static_file("/root/vizStuff/images/heatmap.png")

@app.route("/camera01_markov", methods=['GET'])
def markov_path():
	parent = request.args.get("parent")
	return jsonify({"data" : markov(parent)})


@app.route("/bubblechart", methods=['GET'])
def chart1():
	return render_template("bubbleChart.html")

@app.route('/bubblejs')
def send_bubblejs():
    return app.send_static_file("js/usa_data.js")

@app.route('/bubblecsv')
def send_bubbledata():
    return app.send_static_file("csv/journey.csv")

# @app.route("/getScreenShot", methods=['POST'])
# def getScreenShotFunc():
# 	data = request.form.get("img")
# 	# print(data)
# 	try:
# 		data = data.split(";base64,")[1]
# 	except:
# 		pass
# 	data = imgConversion(data)
# 	face = isFace(data)
# 	return jsonify({"STATUS" : face.decode("utf-8")})

# @app.route("/saveuser", methods=["POST"])
# def saveuserFunc():
# 	usr = request.form.get("usr")
# 	name = request.form.get("name")
# 	try:
# 		usr = usr.split(";base64,")[1]
# 	except:
# 		pass
# 	usr = imgConversion(usr)
# 	isSaved = saveUserTodb(usr, name)
# 	if isSaved:
# 		return jsonify({"STATUS" : "200"})
# 	else:
# 		return jsonify({"STATUS" : "500"})

# @app.route("/checkuser", methods=["POST"])
# def checkuserFunc():
# 	usr = request.form.get("usr")
# 	print(usr)
	# try:
	# 	usr = usr.split(";base64,")[1]
	# except:
	# 	pass
# 	usr = imgConversion(usr)
# 	match = match_features(usr)
# 	return jsonify({"STATUS" : match})

@app.route("/nicF", methods=['POST'])
def nicFFunc():
	nicF = request.form.get("nicF")
	# print(nicF)
	try:
		nicF = nicF.split(";base64,")[1]
	except:
		pass
	nicF = imgConversion(nicF)
	nicF = isFaceCheck(nicF, "nicfront")
	if nicF:
		return jsonify({"status" : 200})
	else:
		return jsonify({"status" : 500})

@app.route("/nicB", methods=['POST'])
def nicBFunc():
	nicF = request.form.get("nicF")
	# print(nicF)
	try:
		nicF = nicF.split(";base64,")[1]
	except:
		pass
	nicF = imgConversion(nicF)
	nicF = isFaceCheck(nicF, "nicback")
	if nicF:
		return jsonify({"status" : 200})
	else:
		return jsonify({"status" : 500})


@app.route("/selfie", methods=['POST'])
def selfieFunc():
	selfie = request.form.get("selfie")
	# print(selfie)
	try:
		selfie = selfie.split(";base64,")[1]
	except:
		pass
	selfie = imgConversion(selfie)
	selfie = isSelfieCheck(selfie)
	if selfie:
		return jsonify({"status" : 200})
	else:
		return jsonify({"status" : 500})

@app.route("/video", methods=["POST"])
def videoFunc():
	file = request.files['file']
	file.save("/root/vizStuff/face_data/video.mp4")
	return jsonify({"status" : 200})

@app.route("/evaluate", methods=["GET"])
def evaFunc():
	results = evaluation()
	return jsonify({"results" : results})

@app.route('/counter', methods=['GET'])
def home():
	genderList=['Male','Female']
	ageList=['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
	emotion =  ['Anger', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

	client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
	db = client["camera01_roi"]
	human_counter = db["human_counter"]
	human_demo = db["human_demo"]
		
	dict = {}
	try:
		# count total
		_ = human_counter.find({}, {"inside":1}).sort([("inside", -1)]).limit(1)
		dict["count"] = [{"inside":[each["inside"] for each in _][0]}]
		_ = human_counter.find({}, {"outside":1}).sort([("outside", -1)]).limit(1)
		dict["count"].append({"outside": [each["outside"] for each in _][0]})
		_ = human_counter.find({}, {"_id":1}).sort([("_id", -1)]).limit(1)
		dict["count"].append({"date": [each["_id"] for each in _][0]})
		
		# count gender
		for index, each in enumerate(genderList):
			if index == 0:
				dict["gender"] = [{each: human_demo.find({"gender": each}, {"gender":1}).count()}]
			else:
				dict["gender"].append({each: human_demo.find({"gender": each}, {"gender":1}).count()})
				
		# count age
		for index, each in enumerate(ageList):
			if index == 0:
				dict["age"] = [{each: human_demo.find({"age": each[1:-1]}, {"age":1}).count()}]
			else:
				dict["age"].append({each: human_demo.find({"age": each[1:-1]}, {"age":1}).count()})
		
		# count emotion
		for index, each in enumerate(emotion):
			if index == 0:
				dict["emotion"] = [{each: human_demo.find({"emotion": each}, {"emotion":1}).count()}]
			else:
				dict["emotion"].append({each: human_demo.find({"emotion": each}, {"emotion":1}).count()})
		
		dict['emotion'].pop(1);dict['emotion'].pop(1);dict['emotion'].pop(3)
			
		#pdb.set_trace()
		dict["aggregate"] = aggregator()
		return jsonify(dict)
	except Exception as e:
		print(str(e))
		return "No Results"

if __name__ == "__main__":
	app.run('0.0.0.0', debug=True, threaded=True)