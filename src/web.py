import cv2 as cv, numpy as np, time
cv.setUseOptimized(True)

cap = cv.VideoCapture(0)
font = cv.FONT_HERSHEY_COMPLEX_SMALL
white = (239, 239, 239)
fps, cntfps, timfps = 0, 0, 0

hsvyellow = [(0, 0, 0), (85, 255, 255)]

oxoy = (320, 240)
white = (255, 255, 255)

cropbox = ((20, 460), (0, 640))

goal = 0

def gate(hsvframe, low, high):
    global goal, cropbox
    mask = cv.inRange(hsvframe, low, high)

    cntcnts, cm0, sm0, cm1, sm1 = 0, 0, 0, 0, 0
    cnts, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        sc = cv.contourArea(c)
        if sc > sm0 and sc > 5000:
            cntcnts += 1
            cm0, sm0 = c, sc
            if sm0 > sm1:
                cm0, sm0, cm1, sm1 = cm1, sm1, c, sc


    if cntcnts >= 2:
        x0, y0, w0, h0 = cv.boundingRect(cm0)
        x1, y1, w1, h1 = cv.boundingRect(cm1)
        x0, x1 = x0 + w0 // 2, x1 + w1 // 2
        goal = (x0 + x1) // 2

        cv.circle(mask, (x0,   y0 + h0//2), 5, 0, -1)
        cv.circle(mask, (x1,   y1 + h1//2), 5, 0, -1)

        cv.arrowedLine(mask, (cropbox[1][1] // 2, cropbox[0][1]), (goal, y1 + h1//2), 255, 1)

    elif cntcnts == 1:
        print('less than 2 contours on frame')

        x1, y1, w1, h1 = cv.boundingRect(cm1)
        x1 = x1 + w1 // 2
        cv.circle(mask, (x1,   y1 + h1//2), 5, 0, -1)

        if x1 < 320: goal = cropbox[1][1]
        else:        goal = cropbox[1][0]

        cv.arrowedLine(mask, (320, cropbox[0][1]), (goal, cropbox[0][1] // 2), 255, 1)

    else: print('there are no contours on frame')




    return mask


while cv.waitKey(1) != ord('q'):
    _, frame = cap.read()
    hsvframe = cv.cvtColor(frame[cropbox[0][0]:cropbox[0][1], cropbox[1][0]:cropbox[1][1]], cv.COLOR_BGR2HSV)

    # frame[460:480, 0:640] = (239, 239, 239)
    # frame[0:10, 290:351], frame[10:20, 300:340] = white, white
    # cv.circle(frame, (300, 10), 10, white, -1)
    # cv.circle(frame, (340, 10), 10, white, -1)
    #
    # cv.putText(frame, "3", (314, 15), font, 1, 0, 1)
    # cv.putText(frame, "manual", (270, 475), font, 1, 0, 1)
    # cv.line(frame, (320, 20), (320, 480), (0, 0, 255), 1)


    mask = gate(hsvframe, hsvyellow[0], hsvyellow[1])

    cv.imshow("mask", mask)


# cv.imshow('frame', frame)
cap.release()
cv.destroyAllWindows()