#3.12.10

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")
import os
os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import math
import numpy as np
import time

import threading

import cv2
import mouse
import mediapipe as mp
import pyautogui as gui

import mouse_control as mc
import graph

#print(mp.__version__)
#print(mp.__file__)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


#BGR NOT RGB !!
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (121,240,132)
RED = (76,48,246)

width = 1920
height = 1080
process_width = 640
process_height = 400
center = (width//2, height//2)

marge = 10 # in pixel

cooldown = 0.2
last_click = 0
is_click = False

round_value = 4

x = 0
y = 0
minus_t1 = 0

debug_timings = {"t1" : [], "t2" : [], "t3" : [], "t4" : [], "t5" : []}


font = cv2.FONT_HERSHEY_SIMPLEX

url = "http://192.168.1.168:4747/video"
camera = cv2.VideoCapture(url)

if not camera.isOpened():
    print("nonononon")
    url = "http://192.168.1.30:4747/video"
    camera = cv2.VideoCapture(url)


def finger_position(finger_part_name, COLOR):
    #print(finger_part_name)
    finger_part = getattr(mp_hands.HandLandmark, finger_part_name)
    #print(finger_part)
    finger_part_position = hand_landmarks.landmark[finger_part]

    CircleX = int(finger_part_position.x * width)
    CircleY = int(finger_part_position.y * height)

    cv2.circle(frame, (CircleX, CircleY), 5, COLOR, 2)

    return(CircleX,CircleY)

def finger_switch(p1,p2,distance_i_want = 100):
    distance_between_finger = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    fingerClose = False

    if distance_between_finger < distance_i_want:
        COLOR = GREEN
        fingerClose = True
        
    else:
        COLOR = RED
        fingerClose = False
        
        
    cv2.line(frame, (p1[0], p1[1]), (p2[0], p2[1]), COLOR, 2)
    return fingerClose

def reading_frame():
    ret , frame = camera.read()
    return frame

def preprocess_frame(frame):

    smaller_frame = cv2.resize(frame, (process_width, process_height))
    smaller_frame.flags.writeable = False
    smaller_frame = cv2.cvtColor(smaller_frame, cv2.COLOR_BGR2RGB)

    frame = cv2.resize(frame, (width, height))
    return smaller_frame, frame
    
def process_frame(smaller_frame):
    result = hands.process(smaller_frame)
    return result

def show_image(frame):
    cv2.imshow("oui",frame)


debug_safe = 0

with mp_hands.Hands(
    model_complexity = 1,
    min_detection_confidence = 0.5,
    min_tracking_confidence = 0.5) as hands:

    while debug_safe < 100:
        debug_safe += 1

        t0 = time.time()
        

        frame = reading_frame()
        t1 = time.time()-t0

        small_frame , frame = preprocess_frame(frame)
        t2 = time.time()-t0

        result = process_frame(small_frame)
        t3 = time.time()-t0


        
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                
                p1 = finger_position("THUMB_TIP", RED)
                p2 = finger_position("INDEX_FINGER_TIP", GREEN)
                p3 = finger_position("MIDDLE_FINGER_TIP", GREEN)
                p4 = finger_position("WRIST", WHITE)

                line1 = finger_switch(p1,p2,60)
                line2 = finger_switch(p2,p3,80)

                if line1 == True:
                    if is_click == False:
                        print("click")
                        is_click = True
                        mc.mouse_down("left")
                else:
                    if is_click == True:
                        is_click = False
                        mc.mouse_up("left")
                        print("no")

                
                if line2 == True:
                   mc.move_to(p4[0]+1920,p4[1])
                
        t4 = time.time()-t0 

        show_image(frame)

        # debug 
        t5 = time.time()-t0

        print(f"-t1 : {t0-minus_t1:.3f} | t0 : {0:.3f} | t1 : {t1:.3f} | t2 : {t2:.3f} | t3 : {t3:.3f} | t4 : {t4:.3f} | t5 : {t5:.3f} ")
        
        debug_timings["t1"].append(round(t1, round_value))
        debug_timings["t2"].append(round(t2 - t1, round_value))
        debug_timings["t3"].append(round(t3 - t2, round_value))
        debug_timings["t4"].append(round(t4 - t3, round_value))
        debug_timings["t5"].append(round(t5 - t4, round_value))


        minus_t1 = t0

        

        if cv2.waitKey(1) == ord('q'):
            break

# to avoid the mouse to press indefinilty
mc.mouse_up("left")
graph.graph_timings(debug_timings)


camera.release()
cv2.destroyAllWindows()