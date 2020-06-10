import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.image as mpimg 
import seaborn as sns
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["camera01_roi"]
collection = db["camera01_roi_heatmap"]

def create_heatmap():
	data = list(collection.find({}, {"_id":0, "lastModified" :0 , "frame_count":0}))
	x = data[0]['centerX']
	y = data[0]['centerY']
	map_img = mpimg.imread('512x512SHELF.png') 
	plt.imshow(map_img)
	ax = sns.kdeplot(x, y, kernel="gau", bw = 0.15, cmap="jet", shade=True, shade_lowest=False, gridsize=50, alpha=0.5, cut=600)
	ax.set(aspect="equal")
	plt.axis('off')
	# plt.show()
	plt.savefig("../static/images/heatmap.png", bbox_inches='tight')

create_heatmap()