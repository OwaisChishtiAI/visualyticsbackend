import pymongo
import pandas as pd
import pdb
from collections import defaultdict

def aggregator():
	dict = {}
	client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
	db = client["camera01_roi"]
	human_demo = db["human_demo"]

	results = human_demo.find({})
	df = pd.DataFrame(list(human_demo.find()))
	df['datetime'] = df['datetime'].dt.strftime('%m-%d-%Y %H:%M')
	
	# genderByTime
	gender = df.groupby(["datetime", "gender"])["gender"].count()
	gender_ = gender.index.values.tolist()
	gender_ = list(zip(*gender_))
	for i, each in enumerate(zip(gender_[0], gender_[1], gender.values.tolist())):
		if i == 0:
			dict["genderByTime"] = [each]
		else:
			dict["genderByTime"].append(each)

	# ageByTime
	# age = df.groupby(["datetime", "age"])["age"].count()
	# age_ = age.index.values.tolist()
	# age_ = list(zip(*age_))
	# for i, each in enumerate(zip(age_[0], age_[1], age.values.tolist())):
	# 	if i == 0:
	# 		dict["ageByTime"] = [each]
	# 	else:
	# 		dict["ageByTime"].append(each)
	# list(df.groupby(['age'])['datetime'])[0]
	dates = list(set(df.datetime))
	groups = set()
	data = list(df.groupby(['age'])['datetime'])
	d = defaultdict(list)
	for each in data:
		new_dt = list(list(each[1]))
		for everyDate in dates:
			d[each[0]].append(new_dt.count(everyDate))
	for eachKey in d.keys():
		groups.add(eachKey)

	# emotionByTime
	emotion = df.groupby(["datetime", "emotion"])["emotion"].count()
	emotion_ = emotion.index.values.tolist()
	emotion_ = list(zip(*emotion_))
	for i, each in enumerate(zip(emotion_[0], emotion_[1], emotion.values.tolist())):
		if i == 0:
			dict["emotionByTime"] = [each]
		else:
			dict["emotionByTime"].append(each)

	# dates = set()
	# groups = set()
	# data = {}
	# for each in dict["ageByTime"]:
	# 	dates.add(each[0])
	# 	groups.add(each[1])	
	# groups = list(groups)
	# dates = list(dates)

	# li = {}
	
	# for i in range(len(groups)):
	# 	li2 = []
	# 	for j in range(len(dict["ageByTime"])):
	# 		if groups[i] in dict["ageByTime"][j]:
	# 			if len(li2) != len(dates):
	# 				li2.append(dict["ageByTime"][j][2])
	# 			else:
	# 				li2.pop()
	# 				li2.append(dict["ageByTime"][j][2])
	# 		else:
	# 			if len(li2) != len(dates):
	# 				li2.append(0)
			
	# 	li[groups[i]] = li2


	# dates = {"dates" : dates}
	# groups = {"groups" : groups}
	# li = {"data" : li}
	# return li, groups, dates

# "aggregate": {
#     "ageByTime": [
#       [
#         "05-17-2020 20:24",
#         "25-32",
#         2
#       ],
#       [
#         "05-17-2020 20:25",
#         "25-32",
#         1
#       ],
#       [
#         "05-17-2020 20:25",
#         "4-6",
#         1
#       ]
#     ],

	# dates = set()
	# groups = set()
	# data = defaultdict(list)
	# for i in range(len(dict["ageByTime"])):
	# 	dates.add(dict["ageByTime"][i][0])
	# 	groups.add(dict["ageByTime"][i][1])
	# 	data[dict["ageByTime"][i][0]].append({dict["ageByTime"][i][1] : []})
	# dates, groups = list(dates), list(groups)

	# for i in range(len(dict["ageByTime"])):
	# 	data[dict["ageByTime"][i][0]]


	# dates = set()
	# groups = set()
	# for i in range(len(dict["ageByTime"])):
	# 	dates.add(dict["ageByTime"][i][0])
	# dates, groups = list(dates), list(groups)
	# for i in range(len(dates)):
	# 	for j in range(len(groups)):
	# df2 = df[["age", "datetime"]]
	return d, dates, list(groups)

# "group 1" : [all counts of dates]
# print(aggregator())