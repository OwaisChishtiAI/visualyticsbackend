import cv2
import matplotlib.pyplot as plt
import pysift as sift
from imutils import paths
# read images

class Sift:
    def __init__(self):
        self.matcher = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

    def extract_features(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _ , descriptors = sift.computeKeypointsAndDescriptors(frame)
        return descriptors
    
    def isMatch(self, d1, d2):
        matches = self.matcher.match(d1,d2)
        matches = sorted(matches, key = lambda x:x.distance)
        print("[Info] No. of Features matched: ", len(matches))
        if len(matches) >= 40:
            return True
        else:
            return False


# def iterator(file=None, usedefault=True):
#     img1 = cv2.imread('compare/2.png')
#     img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
#     keypoints_1, descriptors_1 = sift.computeKeypointsAndDescriptors(img1)
#     if usedefault:
#         file = list(paths.list_images("compare"))

#     for i in range(len(file)):
#         img2 = cv2.imread(file[i])
#         img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
#         img2 = cv2.resize(img2, img1.shape, interpolation=cv2.INTER_AREA)
#         print("[Info] Shapes of images: ", img1.shape, ", ", img2.shape)
#         keypoints_2, descriptors_2 = sift.computeKeypointsAndDescriptors(img2)

#         #feature matching
#         bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

#         matches = bf.match(descriptors_1,descriptors_2)
#         matches = sorted(matches, key = lambda x:x.distance)
#         print("2.png vs {0}: {1}".format(file[i].split("/")[1], len(matches)))

# def two():
#     # read images
#     img1 = cv2.imread('compare/2.png')
#     img2 = cv2.imread('compare/2.png')

#     img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
#     img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

#     #sift

#     keypoints_1, descriptors_1 = sift.computeKeypointsAndDescriptors(img1)
#     keypoints_2, descriptors_2 = sift.computeKeypointsAndDescriptors(img2)

#     #feature matching
#     bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

#     matches = bf.match(descriptors_1,descriptors_2)
#     matches = sorted(matches, key = lambda x:x.distance)
#     print(len(matches))
# # iterator(file=["compare/mebck.jpeg", "compare/mefnt.jpeg", "compare/meside.jpeg"], usedefault=False)
# # img3 = cv2.drawMatches(img1, keypoints_1, img2, keypoints_2, matches[:50], img2, flags=2)
# # plt.imshow(img3),plt.show()
