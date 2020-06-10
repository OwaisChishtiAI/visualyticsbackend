import numpy as np
import argparse
import imutils
import time
import cv2
import os
import pdb
import pymongo
from bson.objectid import ObjectId

class Human:
    def __init__(self):
        yolo = "model_weights/"
        # frame = cv2.imread("images/shelf_3_people.png")
        # frame = cv2.resize(frame, (512, 512), interpolation=cv2.INTER_AREA)
        self.args = {"confidence" : 0.5, "threshold" : 0.3}
        # confidence = 0.5
        # threshold = 0.3
        labelsPath = os.path.sep.join([yolo, "coco.names"])
        LABELS = open(labelsPath).read().strip().split("\n")
        COLORS = np.random.randint(0, 255, size=(len(LABELS), 3), dtype="uint8")
        weightsPath = os.path.sep.join([yolo, "yolov3.weights"])
        configPath = os.path.sep.join([yolo, "yolov3.cfg"])

        print("[INFO] loading YOLO from disk...")
        self.net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)
        self.ln = self.net.getLayerNames()
        self.ln = [self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = myclient["camera01_roi"]
        self.collection = self.db["camera01_roi"]

    def get_features_from_db(self, roi):
        # data = self.collection.find({"_id": ObjectId("5eb03e0a1bb4256613de6249")}, {"_id":0, "{}".format(roi) : 1})
        # return list(data)
        return np.load("npy/{}.npy".format(roi))

    def update_roi(self, roi, value):
        np.save("npy/{}.npy".format(roi), value)
        # self.collection.update({"_id" : ObjectId("5eb03e0a1bb4256613de6249")}, {"$set" : { "{}".format(roi) :  value } } ) 

    def detect(self, frame):
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        start = time.time()
        layerOutputs = self.net.forward(self.ln)
        # print("FF", time.time() - start)

        boxes = []
        confidences = []
        classIDs = []
        (W, H) = (None, None)
        (H, W) = frame.shape[:2]
        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]

                # filter out weak predictions
                centers = []
                if confidence > self.args["confidence"]:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")

                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    # update our list of bounding box coordinates,
                    # confidences, and class IDs

                    # centers.append(((x+(x+int(width)))//2, (y+(y+int(height)))//2))
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        # apply non-maxima suppression to suppress weak
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.args["confidence"], self.args["threshold"])
        # print("#######", len(idxs))
        centers = []
        bbox_cords = []
        if len(idxs) > 0:
            # loop over the indexes we are keeping
            for index, i in enumerate(idxs.flatten()):
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                bbox_cords.append([x, y , w, h])
                centers.append(((x+(x+w))//2, (y+(y+h))//2))

        return centers, bbox_cords


# cap = cv2.VideoCapture("images/shelf_video.mp4")
# human = Human()
# fff = 0
# while cap.isOpened():
#     try:
#         ret,frame = cap.read()

#         frame = cv2.resize(frame, (512, 512), interpolation=cv2.INTER_AREA)
#         locs, bbox_cords = human.detect(frame)
#         for i in range(len(locs)):
#             # frame = cv2.circle(frame, (each[0], each[1]), 5, (0,255,0), 5)
#             croped = frame[bbox_cords[i][1]:bbox_cords[i][1]+bbox_cords[i][3], bbox_cords[i][0]:bbox_cords[i][0]+bbox_cords[i][2]]
#             # cv2.imshow("img", croped)
#             # cv2.imwrite("python-compare-two-images/images/{}.png".format(fff), croped);fff+=1
#             if cv2.waitKey(10) & 0xFF == ord('q'):
#                 break
#     except Exception as e:
#         print(str(e))
#         cap.release()
#         cv2.destroyAllWindows()
# #
# #
# cap.release()
# cv2.destroyAllWindows()
# human = Human()
# img = cv2.imread("images/shelf_3_people.png")
# img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_AREA)
# locs, bbox_cords = human.detect(img)
# i = 1
# for each in bbox_cords:
#     cropped = img[each[1]:each[1]+each[3], each[0]:each[0]+each[2]]
#     # cv2.imshow("image", cropped)
#     # cv2.waitKey(0)
#     cv2.imwrite("for_face_{}.png".format(i), cropped)
#     i+=1
# print(locs, bbox_cords)