import pandas as pd
import os
from markov_autocomplete.autocomplete import Autocomplete
from collections import defaultdict

def markov(parent):
	data = pd.read_csv("journey.csv")
	data = data.iloc[:, [1, 4]]
	data = list(data.groupby("TUCASEID"))

	os.system("rm -rf journey.txt ngram")
	sents = []

	with open("journey.txt", "a", encoding='utf8', errors='ignore')as f:
		for i in range(len(data)):

			li = []
			d = list(data[i][1]['TUTIER1CODE'].values)
			for j in range(len(d) - 1):
				if d[j] != d[j + 1]:
					li.append(d[j])
			sents.append(" ".join(["q"+str(x) for x in li]))
			f.write(" ".join(["q"+str(x) for x in li]));f.write("\n")

	markov_history = Autocomplete(model_path="ngram", sentences=sents, n_model=3, n_candidates=10, match_model="start", min_freq=0, punctuations="", lowercase=True)

	path = markov_history.predictions(parent)#"q5"
	path = [item.replace('q', 'Q') for item in path[0]]
	tree = defaultdict(list)
	for each in path:
		try:
			tree[each.split(" ")[1]].append(each.split(" ")[2])
		except:
			pass

	keys_data = []
	for key in tree.keys():
		keys_data.append(key)
	tree['keys'] = keys_data
	return tree

# print(markov("q5"))
