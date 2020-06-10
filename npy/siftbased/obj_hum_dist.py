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


def calc_distance(**kwargs): # returns roi number from 1 to 22
        min_dist = []
        for each in kwargs['shelf']:
            min_dist.append(distClass.euclidean(kwargs['human'], (each[0], each[1]) ))
        return min_dist.index(min(min_dist)) + 1

qs = [(5, 129), (46, 191), (71, 255), (97, 270), (143, 226), (119, 190), (79, 151), (105, 123), (146, 59), (205, 92), (236, 108), (271, 82), (302, 34), (329, 23), (353, 5), (392, 3), (460, 11), (367, 186), (313, 328), (422, 200), (370, 437), (506, 137)]

# qs_map = {i:[] for i in range(1, len(qs)+1)}
qs_map_counter = {str(i):0 for i in range(1, len(qs)+1)}

cap = cv2.VideoCapture("images/shelf_video.mp4")

def mapper():
    map_img = cv2.imread("images/empty_shelf.png")
    map_img = cv2.resize(map_img, (512, 512), interpolation=cv2.INTER_AREA)
    return map_img

sift = Sift()
human = Human()
frame_count = 1
while cap.isOpened():
    try:
        # pdb.set_trace()
        ret,frame = cap.read()
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

            roi = calc_distance(human = locs[i], shelf=qs)
            print("[Info] Region of Interest: Q", roi)
            cropped = frame[bbox_cords[i][1]:bbox_cords[i][1]+bbox_cords[i][3], bbox_cords[i][0]:bbox_cords[i][0]+bbox_cords[i][2]]
            cropped = cv2.resize(cropped, (128, 128), interpolation=cv2.INTER_AREA)
            if not qs_map_counter[str(roi)]:

                # if roi == 5:
                #     cv2.imwrite("prev.png", cropped)

                print("[Info] Extracting Features... ")
                features = sift.extract_features(cropped)
                print("[Info] Features Updated in DB")
                human.update_roi(roi, features)
                print("[Info] Updating Counter.")
                qs_map_counter[str(roi)] = 1
            else:
                print("[Info] Someone already visited Q{}, Extracting Features...".format(roi))
                maybe_new_person_features = sift.extract_features(cropped)
                # prev_person_features = np.array(human.get_features_from_db(roi)[0][str(roi)]) ; cv2.imwrite("new.png", cropped)
                prev_person_features = human.get_features_from_db(roi)
                if sift.isMatch(prev_person_features, maybe_new_person_features):
                    pass
                else:
                    print("[Info] Features not matched, Writing to DB.")
                    human.update_roi(roi, maybe_new_person_features)
                    print("[Info] Updating Counter.")
                    qs_map_counter[str(roi)] += 1
        #Update Counter in DB
                    
        frame_count += 1
        print("[Info] ROI ", qs_map_counter)
    except Exception as e:
        print(str(e))
        cap.release()
        cv2.destroyAllWindows()


cap.release()
cv2.destroyAllWindows()
                
                        
















#  roi = calc_distance(human=( locs[i][0], locs[i][1] ) , shelf=qs) # take min distant place from 1 to 22
#             cropped_frame = frame[bbox_cords[i][1]:bbox_cords[i][1]+bbox_cords[i][3], bbox_cords[i][0]:bbox_cords[i][0]+bbox_cords[i][2]]
#             if Face().isFace(cropped_frame): # if face detected in cropped frame
#                 if qs_map[roi] != []: # if this MD place has previous cropped frames
#                     face_match_decision = []
#                     for everyFace in qs_map[roi]: # iterate over all frames or faces prev at MD place
#                         if Face().matchFace(everyFace, cropped_frame): # if any face matches
#                             if qs_map_counter[roi]: # if counter is updated
#                                 pass # do not do any thing
#                             else: # if counter is not updated
#                                 roi_map.append("Q"+str(roi)) # add ROI
#                                 qs_map_counter[roi] = 1 # update counter for similar face
#                         else: # if niether face matches
#                             face_match_decision.append(True) # create vote for negation
#                     if all(face_match_decision): # if all votes are in negation
#                         roi_map.append("Q"+str(roi)) # add ROI
#                         qs_map_counter[roi] = 0 # reset update counter
#                 else: #if no prev data or faces at this MD place
#                     roi_map.append("Q"+str(roi)) # add ROI
#                     qs_map[roi].append(cropped_frame) # add this MD place to be used in future as prev MD place
#             else:
#                 pass # if not face is detected in cropped frame, do not do anything.