#3.12.10
import cv2
import numpy as np

print("cv2")

#BGR NOT RGB !!
color = (255,0,0)
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (121,240,132)
RED = (76,48,246)

url = "http://192.168.1.168:4747/video"
camera1 = cv2.VideoCapture(url)
url = "http://192.168.1.30:4747/video"
camera2 = cv2.VideoCapture(url)


width = 1600
height = 1000

#cv2.resizeWindow("oui", width, height) 
cv2.namedWindow("double")



while True:
    _, image1 = camera1.read()
    _, image2 = camera2.read()


    image1 = cv2.resize(image1, (width//2, height//2))
    image2 = cv2.resize(image2, (width//2, height//2))
    
    horizontal = np.concatenate((image1, image2), axis=1)

    cv2.imshow("double",horizontal)

    if cv2.waitKey(1) == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()