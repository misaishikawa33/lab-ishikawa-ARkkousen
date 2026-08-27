import cv2
from cv2 import aruco

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_50)
parameters = aruco.DetectorParameters_create()

while True:
    ret, image = cap.read()

    corners = ()
    corners, ids, rejectedImgPoints = aruco.detectMarkers(image, aruco_dict, parameters=parameters)

    detected_img = aruco.drawDetectedMarkers(image, corners, ids)

    if ids is not None:
        c = corners[0][0]
        x1, x2, x3, x4 = c[:,0]
        y1, y2, y3, y4 = c[:,1]
        
        cv2.circle(detected_img, (int(x1), int(y1)), 20, (255, 255, 255), thickness = 3, lineType=cv2.LINE_AA)
        cv2.circle(detected_img, (int(x2), int(y2)), 20, (255, 0, 0), thickness = 3, lineType=cv2.LINE_AA)
        cv2.circle(detected_img, (int(x3), int(y3)), 20, (0, 255, 0), thickness = 3, lineType=cv2.LINE_AA)
        cv2.circle(detected_img, (int(x4), int(y4)), 20, (0, 0, 255), thickness = 3, lineType=cv2.LINE_AA)            

    cv2.imshow("image", detected_img)

    key = cv2.waitKey(1) & 0xff
    if key == ord('q'):
        break
