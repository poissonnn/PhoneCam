#3.12.10
import cv2
import numpy as np

import mediapipe as mp

print(mp.__version__)
print(mp.__file__)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

width = 800
height = 500

url = "http://192.168.1.30:4747/video"
camera = cv2.VideoCapture(url)

with mp_hands.Hands(
    model_complexity = 1,
    min_detection_confidence = 0.5,
    min_tracking_confidence = 0.5) as hands:

    while True:
        _, image = camera.read()

        image = cv2.resize(image, (width, height))

        #change image to process it
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = hands.process(image)

        #reconvert it to show the image correctly later
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

                
        cv2.imshow("oui",image)

        if cv2.waitKey(1) == ord('q'):
            break

camera.release()
cv2.destroyAllWindows()