#!/usr/bin/env python3
from __future__ import print_function
from sqlite3 import Time

import numpy as np
from logging import Logger

import roslib
from std_msgs.msg import String
from sensor_msgs.msg import Image
from sensor_msgs.msg import CompressedImage
from sensor_msgs.msg import CameraInfo

import rospy
import sys

import glob

import sys

import cv2
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
import pyrealsense2 as rs
import message_filters

from ast import literal_eval

roslib.load_manifest('human_tracking')

class Boxes_Drawer:
    def __init__(self):
        self.bridge = CvBridge()
        self.image_sub = rospy.Subscriber(rospy.get_param("/mask_detection/color_topic"), CompressedImage, self.getImage)
        self.depth_sub = rospy.Subscriber(rospy.get_param("/mask_detection/depth_topic"), Image, self.getDepth)
        self.boxes_sub = rospy.Subscriber("/human_tracking/mask_detection/boxes", String, self.getBoxes)

        self.boxes = []
        self.classes = ["with mask", "without mask", "test"]
        self.class_ids = []
        self.confidences = []

        self.indices = []

        self.colorizer = rs.colorizer()

    def getImage(self, image):
        try:
            #np_arr = np.frombuffer(image.data, np.uint8)
            cv_image = self.bridge.compressed_imgmsg_to_cv2(image)#cv2.imdecode(np_arr, cv2.IMREAD_COLOR) 
        except CvBridgeError as e:
            print(e)

        self.show_image(cv_image)

    def getDepth(self, depth):
        try:
            #np_arr = np.frombuffer(image.data, np.uint8)
            #cv_depth = self.bridge.imgmsg_to_cv2(depth)#cv2.imdecode(np_arr, cv2.IMREAD_COLOR) 
            depth_image = self.bridge.imgmsg_to_cv2(depth, desired_encoding="passthrough")
            cv_depth = np.array(depth_image, dtype=np.float32)
            #print("depth of (100, 100) = ", cv_depth[100][100])
        except CvBridgeError as e:
            print(e)

        #self.show_image(depth_image, "depth")

    def show_image(self, cv_image, windowName = "output"):
        #indices = cv2.dnn.NMSBoxes(self.boxes, self.confidences, 0.5, 0.4)
        color = (255, 1, 12)#[int(c) for c in COLORS[class_ids[i]]]
        if len(self.indices) > 0:
            for i in self.indices.flatten():
                try:
                    if self.class_ids[i] == 0 or self.class_ids[i]:
                        #get coordinates
                        (x, y) = (self.boxes[i][0], self.boxes[i][1])
                        (w, h) = (self.boxes[i][2], self.boxes[i][3])
                        #darw bounding box
                        
                        cv2.rectangle(cv_image, (x, y), (x + w, y + h), color, 2, lineType=cv2.LINE_AA)             
                        #put text
                        text = "{}: {:.2f}".format(self.classes[self.class_ids[i]], self.confidences[i])

                        cv2.rectangle(cv_image, (x, y-28), (x + w, y), (255,255,255), -1)
                    
                        cv2.putText(cv_image, text, (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 1, lineType=cv2.LINE_AA)
                    else:
                        (x, y) = (self.boxes[i][0], self.boxes[i][1])
                        (w, h) = (self.boxes[i][2], self.boxes[i][3])
                        cv2.rectangle(cv_image, (x, y), (x + 1, y + 1), color, 2, lineType=cv2.LINE_AA)             
                except:
                    continue

        #cv2.rectangle(cv_image, (99, 99), (101, 101), color, 2, lineType=cv2.LINE_AA)       
        #cv2.rectangle(cv_image, (99, 199), (101, 201), color, 2, lineType=cv2.LINE_AA)
        #cv2.rectangle(cv_image, (99, 299), (101, 301), color, 2, lineType=cv2.LINE_AA)   
        cv2.imshow(windowName, cv_image)
        cv2.waitKey(3)

    def getBoxes(self, boxes):
        data = boxes.data
        boxes, confidences, class_ids = data.split("|")
        
        self.boxes = literal_eval(boxes)
        self.confidences = literal_eval(confidences)
        self.class_ids = literal_eval(class_ids)
        self.indices = cv2.dnn.NMSBoxes(self.boxes, self.confidences, 0.5, 0.4)
        
        


def main(args):
    rospy.init_node('boxes_drawer', anonymous=True)

    bd = Boxes_Drawer()

    rospy.spin()
    rospy.Rate = 1
    while not rospy.is_shutdown():
        rospy.sleep(rospy.Rate)

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main(sys.argv)