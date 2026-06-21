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

FrameCount = 0
FRAMESTEP = 3
prev_frame_time = 0
new_frame_time = 0

x = 0
y = 0
minus_t1 = 0

recycle_result = None

font = cv2.FONT_HERSHEY_SIMPLEX

url = "http://192.168.1.168:4747/video"
camera = cv2.VideoCapture(url)

def finger_position(finger_part_name, COLOR):
    print(finger_part_name)
    finger_part = getattr(mp_hands.HandLandmark, finger_part_name)
    print(finger_part)
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


with mp_hands.Hands(
    model_complexity = 1,
    min_detection_confidence = 0.5,
    min_tracking_confidence = 0.5) as hands:

    while True:
        t0 = time.time()
        new_frame_time = time.time()

        _, frame = camera.read()

        if(FrameCount == 0):
            result = hands.process(smaller_frame)
            recycle_result = result
            cv2.rectangle(frame, (0, 0), (40, 40),GREEN, -1)
            

        elif(FrameCount !=0):
            result = recycle_result
            cv2.rectangle(frame, (0, 0), (40, 40),RED, -1)
        
        
        frame = cv2.resize(frame, (width, height))
        t1 = time.time()-t0

        #change image to process it
        smaller_frame = cv2.resize(frame, (process_width, process_height))
        smaller_frame.flags.writeable = False
        smaller_frame = cv2.cvtColor(smaller_frame, cv2.COLOR_BGR2RGB)
        
        
        t2 = time.time()-t0
        
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                
                p1 = finger_position("THUMB_TIP", RED)
                p2 = finger_position("INDEX_FINGER_TIP", GREEN)
                p3 = finger_position("MIDDLE_FINGER_TIP", GREEN)
                p4 = finger_position("WRIST", WHITE)

                line1 = finger_switch(p1,p2,60)
                line2 = finger_switch(p2,p3,80)

                if line1 == True and line2 == False:
                    if is_click == False:
                        print("click")
                        is_click = True
                        mc.mouse_down("left")
                else:
                    if is_click == True:
                        is_click = False
                        mc.mouse_up("left")
                        print("no")

                """
                if time.time() >  last_click + cooldown:
                    mc.move_to(p4[0]+1920,p4[1])
                    last_click = time.time() 
                """   
                
        #calculate fps and show it
        fps = 1/(new_frame_time-prev_frame_time)
        prev_frame_time = new_frame_time    
        cv2.putText(frame, str(int(fps)), (20, 30), font, 1, (0, 0, 0), 2)

        #show the image 
        cv2.imshow("oui",frame)

        # debug timer
        t3 = time.time()-t0
        print(f"-t1 : {round(t0-minus_t1,4)} | t0 : {t0-t0} | t1 : {round(t1,4)} | t2 : {round(t2,4)} | t3 : {round(t3,4)} |")
        minus_t1 = t0

        if (FrameCount >= FRAMESTEP):
            FrameCount = 0 
        else:
            FrameCount = FrameCount + 1


        if cv2.waitKey(1) == ord('q'):
            break

camera.release()
cv2.destroyAllWindows()