import sys
import cv2
import os
import numpy as np
from hum_dist import Human
from extract_features import Sift
from scipy.spatial import distance as distClass
from time import sleep
from datetime import datetime
import pdb
import requests
from collections import defaultdict
import pandas as pd

def calc_distance(**kwargs): # returns roi number from 1 to 22
    min_dist = []
    for each in kwargs['shelf']:
        min_dist.append(distClass.euclidean(kwargs['human'], (each[0], each[1]) ))
    return min_dist.index(min(min_dist)) + 1

qs = [(5, 129), (46, 191), (71, 255), (97, 270), (143, 226), (119, 190), (79, 151), (105, 123), (146, 59), (205, 92), (236, 108), (271, 82), (302, 34), (329, 23), (353, 5), (392, 3), (460, 11), (367, 186), (313, 328), (422, 200), (370, 437), (506, 137)]

# qs_map = {i:[] for i in range(1, len(qs)+1)}
qs_map_counter = {str(i):[] for i in range(1, len(qs)+1)}

roi_map_counter = {str(i):0 for i in range(1, len(qs)+1)}

roi_pattern_counter = []

cap = cv2.VideoCapture("/root/vizStuff/images/shelf_video.mp4")

def mapper():
    map_img = cv2.imread("images/empty_shelf.png")
    map_img = cv2.resize(map_img, (512, 512), interpolation=cv2.INTER_AREA)
    return map_img

def journey(data):
    positions = defaultdict(list)
    timer = 20
    columns=["TUCASEID","start_minute","stop_minute","TUTIER1CODE","TUACTIVITY_N"]
    k=20170101170520
    for i in range(len(data)):
        for j in range(len(data[i])):
            positions[k].append(data[i][j])
            k+=1
        k=20170101170520
    d = {"TUCASEID" : [], "TUTIER1CODE" : [], "TUACTIVITY_N" : [], "start_minute" : [], "stop_minute" : []}
    for key, val in positions.items():
        for pntr in range(len(val)):
            d['TUCASEID'].append(key)
            d["TUTIER1CODE"].append(val[pntr])
            d["TUACTIVITY_N"].append(pntr+1)
            d["start_minute"].append(timer)
            d['stop_minute'].append(timer+5)
            timer += 10
        timer = 20
        
    df = pd.DataFrame(d, columns=columns)
    print("[Info] Saved CSV")
    df.to_csv("journey.csv")

sift = Sift()
human = Human()
frame_count = 1
while cap.isOpened():
    try:
        # pdb.set_trace()
        ret,frame = cap.read()
        roi_pattern = []
        print("-" * 27)
        print("[Info] Evaluating Frame: ", frame_count)
        print("-" * 27)
        frame = cv2.resize(frame, (512, 512), interpolation=cv2.INTER_AREA)
        locs, bbox_cords = human.detect(frame)


        for i in range(len(locs)):
            for pt in qs:
                lined_frame = cv2.line(frame, (locs[i][0], locs[i][1]), (pt[0], pt[1]), (0,255,0), 2)
            cv2.imshow("Frame", lined_frame)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                quit()

            # if frame_count == 123 and i == 2:
            #     pdb.set_trace()

            roi = calc_distance(human = locs[i], shelf=qs)
            roi_pattern.append(roi)
            print("[Info] Region of Interest: Q", roi)
            cropped = frame[bbox_cords[i][1]:bbox_cords[i][1]+bbox_cords[i][3], bbox_cords[i][0]:bbox_cords[i][0]+bbox_cords[i][2]]
            try:
                cropped = cv2.resize(cropped, (128, 128), interpolation=cv2.INTER_AREA)
                if not qs_map_counter[str(roi)]:

                    # if roi == 5:
                    #     cv2.imwrite("prev.png", cropped)
                    # print("[Info] Extracting Features... ")
                    features = sift.extract_features(cropped)
                    # print("[Info] Features Updated in DB")
                    human.update_roi(roi, features)
                    # print("[Info] Updating Counter.")
                    qs_map_counter[str(roi)].append(1)
                else:
                    # print("[Info] Someone already visited Q{}, Extracting Features...".format(roi))
                    maybe_new_person_features = sift.extract_features(cropped)
                    # prev_person_features = np.array(human.get_features_from_db(roi)[0][str(roi)]) ; cv2.imwrite("new.png", cropped)
                    prev_person_features = human.get_features_from_db(roi)
                    if sift.isMatch(prev_person_features, maybe_new_person_features):
                        qs_map_counter[str(roi)].append(1)
                    else:
                        # print("[Info] Features not matched, Writing to DB.")
                        human.update_roi(roi, maybe_new_person_features)
                        # print("[Info] Updating Counter.")
                        qs_map_counter[str(roi)] = []
            except:
                pass
        #Update Counter in DB
        roi_pattern_counter.append(roi_pattern)
        frame_count += 1
        if frame_count % 10 == 0:
            for key, val in qs_map_counter.items():
                if len(val) >= 10 and len(val) < 20:
                    if not roi_map_counter[key]:
                        roi_map_counter[key] = 1
                    else:
                        roi_map_counter[key] += 1
                    human.write_roi_to_db(roi_map_counter)
                    journey(roi_pattern_counter)
                    

    except Exception as e:
        print(str(e))
        cap.release()
        cv2.destroyAllWindows()


cap.release()
cv2.destroyAllWindows()
