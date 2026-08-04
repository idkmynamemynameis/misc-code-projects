import cv2 as cv
import numpy as np
def nothing(x):
    pass

cap=cv.VideoCapture(0)


while 1:
    

    _,frame = cap.read()
    hsv=cv.cvtColor(frame,cv.COLOR_BGR2HSV)
    lower_red=np.array([150,140,130])
    upper_red=np.array([255,255,255])
    mask=cv.inRange(hsv,lower_red,upper_red)
    res=cv.bitwise_and(frame,frame,mask=mask)
    cv.imshow('frame',frame)
    cv.imshow('mask',mask)
    cv.imshow('res',res)
    k = cv.waitKey(5) & 0xFF
    if k == 27:
        break

cv.destroyAllWindows()
