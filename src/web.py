import cv2 as cv, numpy as np, time

cap = cv.VideoCapture(0)
font = cv.FONT_HERSHEY_COMPLEX_SMALL
white = (239, 239, 239)


while cv.waitKey(1) != ord('q'):
    _, frame = cap.read()
    frame[460:480, 0:640] = (239, 239, 239)
    frame[0:10, 290:351], frame[10:20, 300:340] = white, white
    cv.circle(frame, (300, 10), 10, white, -1)
    cv.circle(frame, (340, 10), 10, white, -1)

    cv.putText(frame, "357", (300, 15), font, 1, 0, 1)
    cv.putText(frame, "Autonomous", (400, 475), font, 1, 0, 1)





    cv.imshow('frame', frame)
cap.release()
cv.destroyAllWindows()