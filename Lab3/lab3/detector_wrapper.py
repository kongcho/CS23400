import numpy as np
import cv2

from lane_detector import LaneDetector
from video_capture_async import VideoCaptureAsync
import time

class DetectorWrapper:
    def __init__(self, scene="pick"):
        self.detector = LaneDetector()
        self.cap = VideoCaptureAsync(0)

        if scene == "pick":
            self.cap.set(cv2.cv.CV_CAP_PROP_SATURATION, 0.1)
            self.cap.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, 0.001)
            self.cap.set(cv2.cv.CV_CAP_PROP_CONTRAST, 1.0)
        elif scene == "home":
            self.cap.set(cv2.cv.CV_CAP_PROP_SATURATION, 0.1)
            self.cap.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, 0.5)
            self.cap.set(cv2.cv.CV_CAP_PROP_CONTRAST, 1.0)
        elif scene == "searle":
            self.cap.set(cv2.cv.CV_CAP_PROP_SATURATION, 0.1)
            self.cap.set(cv2.cv.CV_CAP_PROP_BRIGHTNESS, 0.001)
            self.cap.set(cv2.cv.CV_CAP_PROP_CONTRAST, 1.0)

        self.cap.start()

        for i in range(20):
            ret, frame = self.cap.read()

    def __del__(self):
        self.cap.stop()
        cv2.destroyAllWindows()

    def stop(self):
        self.__del__()

    def plot(self, ret):
        if len(ret) >= 1:
            frame = ret[0]
            shape = frame.shape # (width,height)
            w = shape[1]
            h = shape[0]
            if len(ret) > 1:
                _, mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx = ret

                p = frame[int(h * 2/ 3.):]
                for i in range(p.shape[0] - 1):
                    cv2.line(p, (int(left_fitx[i]), int(ploty[i])), (int(left_fitx[i + 1]), int(ploty[i + 1])), (255, 0, 0), 2)
                for i in range(p.shape[0] - 1):
                    cv2.line(p, (int(right_fitx[i]), int(ploty[i])), (int(right_fitx[i + 1]), int(ploty[i + 1])), (0, 0, 255), 2)

                #cv2.imshow("fitted_lines", p)
            cv2.waitKey(30)

    def detect(self):
        ret, frame = self.cap.read()

        if not ret:
            return False, None
        
        try:
            mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx = self.detector.detect(frame)
        except TypeError:
            print("fit error")
            return False, (frame, )

        return True, (frame, mid_x, left_fit, right_fit, ploty, left_fitx, right_fitx)
