#3.12.10
import cv2

print("cv2")

url = "http://192.168.1.30:4747/video"
camera = cv2.VideoCapture(url)


width = 1600
height = 1000

cv2.namedWindow("oui")
cv2.resizeWindow("oui", width, height) 

while True:
    ret, frame = camera.read()

    frame = cv2.resize(frame, (width,height))

    cv2.imshow("oui",frame)
    if cv2.waitKey(1) == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()