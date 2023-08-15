import cv2 as cv, numpy as np, time

cap = cv.VideoCapture(0)
font = cv.FONT_HERSHEY_DUPLEX

up, down = 255-np.zeros((20, 40, 3), np.uint8), np.zeros((20, 320, 3), np.uint8)

mode = "MANUAL"
start = False

cv.putText(down, mode, (127, 15), font, 0.5, (255, 255, 255), 1)

#3 145, 2 149, 155

fps, cntfps, timfps = 0, 0, 0


while cv.waitKey(1) != ord('q'):
    _, frame = cap.read()
    frame = cv.resize(frame, (320, 240), 1)
    cv.putText(frame, "199", (145, 15), font, 0.5, (100, 200, 255), 1)

    if cv.waitKey(1) == 80: start = not start

    if not start:
        cv.line(frame, (145, 100), (145, 140), (255, 255, 255), 5)
        cv.line(frame, (175, 100), (175, 140), (255, 255, 255), 5)
        cv.putText(down, "| |", (5, 13), font, 0.35, (255, 255, 255), 2)
    else: down[0:20, 0:50] = 0


    cv.imshow('frame', np.concatenate((frame, down), 0))
cap.release()
cv.destroyAllWindows()