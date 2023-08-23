import cv2 as cv

cap = cv.VideoCapture(0)

while True:
    _, frame = cap.read()


    frane = cv.threshold(frame, 0, 255, cv.ADAPTIVE_THRESHOLD)
    
    cv.imshow('frame', frame)