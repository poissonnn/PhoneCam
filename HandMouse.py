#3.12.10

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")
import os
os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import math
import numpy as np
import time

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

cooldown = 0.1
last_click = 0
is_click = False

x = 0
y = 0
minus_t1 = 0

url = "http://192.168.1.30:4747/video"
camera = cv2.VideoCapture(url)

def finger_position(position, COLOR):
    CircleX = int(position.x * width)
    CircleY = int(position.y * height)

    cv2.circle(image, (CircleX, CircleY), 5, COLOR, 2)

    return(CircleX,CircleY)

    """
    if CircleX > marge and CircleX < width - marge and CircleY > marge and CircleY < height - marge:

        
    #mc.move_to(CircleX, CircleY)

    else:
        print("under the marge")
    """

def finger_switch(p1,p2,distance_i_want = 100):
    distance_between_finger = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

    fingerClose = False

    if distance_between_finger < distance_i_want:
        COLOR = GREEN
        fingerClose = True
        
    else:
        COLOR = RED
        fingerClose = False
        
        
    cv2.line(image, (p1[0], p1[1]), (p2[0], p2[1]), COLOR, 2)
    return fingerClose


with mp_hands.Hands(
    model_complexity = 0,
    min_detection_confidence = 0.5,
    min_tracking_confidence = 0.5) as hands:

    while True:
        t0 = time.time()
        _, image = camera.read()

        image = cv2.resize(image, (width, height))
        #image = cv2.flip(image, 0)
        #Rotated_image = cv2.getRotationMatrix2D(center, 270, 1.0)
        #image = cv2.warpAffine(image, Rotated_image, (width, height))
        t1 = time.time()-t0

        #change image to process it
        small_image = cv2.resize(image, (process_width, process_height))
        small_image.flags.writeable = False
        small_image = cv2.cvtColor(small_image, cv2.COLOR_BGR2RGB)
        result = hands.process(small_image)
        t2 = time.time()-t0

        t3 = time.time()-t0
        
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                """
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
                """
                
                index_tip_position = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip_position = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                middle_tip_position = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]

                p1 = finger_position(thumb_tip_position, GREEN)
                p2 = finger_position(index_tip_position, RED)
                p3 = finger_position(middle_tip_position, GREEN)

                line1 = finger_switch(p1,p2,40)
                line2 = finger_switch(p2,p3,80)



            
                """
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
                
                if line1 == True:
                    if is_click == False:
                        is_click = True
                else:
                    if is_click == True:
                        is_click = False
                
                if time.time() >  last_click + cooldown and is_click:
                    mc.move_to(p2[0],p2[1])
                    last_click = time.time() 
                
            
        #cv2.imshow("oui",image)

        t4 = time.time()-t0

        print(f"-t1 : {round(t0-minus_t1,4)} | t0 : {t0-t0} | t1 : {round(t1,4)} | t2 : {round(t2,4)} | t3 : {round(t3,4)} | t4 : {round(t4,4)} |")

        minus_t1 = t0
        if cv2.waitKey(1) == ord('q'):
            break

camera.release()
cv2.destroyAllWindows()