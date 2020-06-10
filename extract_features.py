import cv2

class Sift:
    def __init__(self):
        self.matcher = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)
        self.sift = cv2.xfeatures2d.SIFT_create()

    def extract_features(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _ , descriptors = self.sift.detectAndCompute(frame, None)
        return descriptors
    
    def isMatch(self, d1, d2):
        matches = self.matcher.match(d1,d2)
        matches = sorted(matches, key = lambda x:x.distance)
        print("[Info] No. of Features matched: ", len(matches))
        if len(matches) >= 40:
            return True
        else:
            return False
        
        
