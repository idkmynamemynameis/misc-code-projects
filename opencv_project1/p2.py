import cv2 as cv
import numpy as np
def nothing(x):
    pass

cap=cv.VideoCapture(0)
cv.namedWindow('control')
cv.createTrackbar('Hmin','control',0,254,nothing)
cv.createTrackbar('Smin','control',0,254,nothing)
cv.createTrackbar('Vmin','control',0,254,nothing)
cv.createTrackbar('Hmax','control',1,255,nothing)
cv.createTrackbar('Smax','control',1,255,nothing)
cv.createTrackbar('Vmax','control',1,255,nothing)





while 1:
    cv.namedWindow('control')
    img = np.zeros((300, 512, 3), np.uint8)
    hmin=cv.getTrackbarPos('Hmin','control')
    hmax=cv.getTrackbarPos('Hmax','control')
    smin=cv.getTrackbarPos('Smin','control')
    smax=cv.getTrackbarPos('Smax','control')
    vmin=cv.getTrackbarPos('Vmin','control')
    vmax=cv.getTrackbarPos('Vmax','control')

    _,frame = cap.read()
    
    height,width,channels=frame.shape

    print(height,width)
    hsv=cv.cvtColor(frame,cv.COLOR_BGR2HSV)
    lower_red=np.array([hmin,smin,vmin])
    upper_red=np.array([hmax,smax,vmax])
    mask=cv.inRange(hsv,lower_red,upper_red)
    res=cv.bitwise_and(frame,frame,mask=mask)
    cv.imshow('frame',frame)
    cv.imshow('mask',mask)
    cv.imshow('res',res)
    cv.imshow('control',img)
    k = cv.waitKey(5) & 0xFF
    if k == 27:
        break

cv.destroyAllWindows()

