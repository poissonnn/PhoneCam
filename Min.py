#3.12.10
import cv2
import numpy as np

print("cv2")

url = "http://192.168.1.30:4747/video"
camera = cv2.VideoCapture(url)


width = 1600
height = 1000


while True:
    _, image = camera.read()

    image = cv2.resize(image, (width, height))
    
    cv2.imshow("oui",image)

    if cv2.waitKey(1) == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()