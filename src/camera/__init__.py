import time
import imutils
import cv2
from src.golfBall import GolfBall
import numpy as np

rm = 21.335e-3  # ball radius in meters


def rotX(val: float):
    return np.array([[1, 0, 0], [0, np.cos(val), np.sin(val)], [0, np.sin(val), np.cos(val)]])


def rotY(val: float):
    return np.array([[np.cos(val), 0, np.sin(val)], [0, 1, 0], [-np.sin(val), 0, np.cos(val)]])


def rotZ(val: float):
    return np.array([[np.cos(val), -np.sin(val), 0], [np.sin(val), np.cos(val), 0], [0, 0, 1]])


def get_R(cam) -> object:
    return rotX(cam.theta[0][0]).dot(rotY(cam.theta[1][0]).dot(rotZ(cam.theta[2][0])))


class Camera:
    def __init__(self, pos=np.array([[0], [0], [0]]), theta=np.array([[0], [0], [0]]), f=1.0, cx=0.0, cy=0.0, source=None):
        self.f = f  # Camera focal length in pixels
        self.cx = cx  # Camera center in x pixel coordinates
        self.cy = cy  # Camera center in y pixel coordinates
        self.K = np.array([[f, 0, cx, 0], [0, f, cy, 0], [0, 0, 1, 0], [0, 0, 0, 1]])  # Calibration Matrix
        self.theta = theta
        R = get_R(self)
        self.E = np.concatenate((R, -pos), axis=1)
        self.E = np.resize(self.E, (4, 4))
        self.E[3] = np.array([0, 0, 0, 1])  # Transformation Matrix
        self.P = self.K.dot(self.E)  # Camera Matrix
        self.P_inv = np.linalg.inv(self.P)  # Inverse of P matrix for position calculations
        self.video_source = source
        self.img = None
        self.prev_img = None
        self.time = 0.0  # time of image in seconds

    def initialize(self):
        pass

    def read(self):
        if self.video_source is not None:
            # Try to grab frame until success
            while not self.video_source.grab():
                pass
            self.time = time.time()
            # Try to read the image until success
            while not self.video_source.retrieve(self.img):
                pass

    def grab(self):
        if self.video_source is not None:
            # using the following semi-sync process for capturing video
            self.video_source.grab()  # very fast
            self.time = time.time()

    def retrieve(self):
        if self.video_source is not None:
            self.img = self.video_source.retrieve()

    # TODO: add CUDA GPU support
    def get_ball(self):
        if self.img is not None:
            # get ball position and radius in camera coordinates
            # apply gaussian blur
            proc_img = cv2.GaussianBlur(self.img, (11, 11), 0)
            # convert to HSV colorspace
            proc_img = cv2.cvtColor(proc_img, cv2.COLOR_BGR2HSV)
            # construct a mask for the ball color
            mask = cv2.inRange(proc_img, GolfBall.ball_lower, GolfBall.ball_upper)
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            # find contours in the mask and initialize the current (x, y) center of the ball
            cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            center = None

            # only proceed if at least one contour was found
            if len(cnts) > 0:
                # find the largest contour in the mask, then use it to compute the circle
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

                # only proceed if the radius meets a minimum size
                if radius > 10:
                    # draw the circle and centroid on the frame
                    cv2.circle(self.img, (int(x), int(y)), int(radius), (0, 255, 0), 2)
                    cv2.circle(self.img, center, 5, (255, 0, 0), -1)
                    cv2.circle(self.img, (137, 97), 3, (0, 0, 0), -1)
                    cv2.imshow("Frame", self.img)
                    cv2.imshow("Mask", mask)

                    dm = radius / (rm * self.f)
                    # get pall position in spatial coordinates
                    pos_p = np.array([[x], [y], [1], [dm]])
                    pos_w = self.P_inv.dot(pos_p)
                    return pos_w / pos_w[3][0], self.time

        else:
            return None


# position = np.array([[0], [0], [0]])
# orientation = np.array([[0.0], [0.0], [0.0]])
#
# cam = Camera(pos=position, theta=orientation, f=417.03, cx=137, cy=97)
#
# cam.img = cv2.imread("../../References/images.jpg")
# # print(cam.get_ball())
# print(cam.get_ball()[0:3])
#
# while 1:
#     key = cv2.waitKey(1) & 0xFF
#     if key == ord("q"):
#         break
#
# cv2.destroyAllWindows()
