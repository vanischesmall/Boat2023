import cv2 as cv, numpy as np, time
cv.setUseOptimized(True)

cap = cv.VideoCapture(0)
font = cv.FONT_HERSHEY_COMPLEX_SMALL
white = (239, 239, 239)
fps, cntfps, timfps = 0, 0, 0

hsvyellow = ((0, 0, 0), (85, 255, 255))

oxoy = (320, 240)
white = (255, 255, 255)

cropbox = ((20, 460), (0, 640))

cropboxnew = ((20, 460), (0, 640))
state, goal, dist, length = 0, 0, 0, 0


def gate(hsvframe, low, high):
    global state, goal, dist, length, cropbox, cropboxnew
    mask = cv.inRange(hsvframe, low, high)

    cropboxnew, cntcnts, cm0, sm0, cm1, sm1 = ((20, 460), (0, 640)), 0, 0, 0, 0, 0
    for c in cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[0]:
        sc = cv.contourArea(c)
        if sc > sm0 and sc > 5000:
            cntcnts, cm0, sm0 = cntcnts + 1, c, sc
            if sm0 > sm1: cm0, sm0, cm1, sm1 = cm1, sm1, c, sc

    if cntcnts >= 2:
        x0, y0, w0, h0 = cv.boundingRect(cm0)
        x1, y1, w1, h1 = cv.boundingRect(cm1)
        x0, x1 = x0 + w0 // 2, x1 + w1 // 2
        dist = abs(x0 - x1)
        goal = (x0 + x1)//2

        # if dist > 430: state += 1

        cropy = cropbox[0][0] + min(y0, y1) - 50
        croph = cropy + max(h0, h1) + 100
        if cropy < 20: cropy = 20
        if croph > 460: croph = 460
        cropboxnew = ((cropy, croph), (0, 640))

        cv.circle(mask, (x0, y0 + h0 // 2), 5, 0, -1)
        cv.circle(mask, (x1, y1 + h1 // 2), 5, 0, -1)

        cv.arrowedLine(mask, (cropbox[1][1] // 2, cropbox[0][1]), (goal, y1 + h1//2), 255, 1, tipLength=0.025)
        cv.putText(mask, str(dist), (goal - 18, y1 + h1//2 - 10), font, 1, (255, 255, 255), 1)

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


def ball(hsvframe, low, high):
    global state, goal, dist, length, cropboxnew
    mask = cv.inRange(hsvframe, low, high)

    cropboxnew, cntcnts, cm0, sm0 = ((20, 460), (0, 640)), 0, 0, 0
    for c in cv.findContours(mask, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)[0]:
        sc = cv.contourArea(c)
        if sc > sm0 and sc > 5000: cntcnts, cm0, sm0 = cntcnts + 1, c, sc

    if cntcnts > 0:
        x0, y0, w0, h0 = cv.boundingRect(cm0)

        cropy = cropbox[0][0] + y0 - 50
        croph = cropy + h0 + 100
        if cropy < 20: cropy = 20
        if croph > 460: croph = 460
        cropboxnew = ((cropy, croph), (0, 640))
        goal, y0 = x0 + w0 // 2, y0 + h0 // 2

        if abs(point - goal) < 10: state += 1

        cv.circle(mask, (goal, y0), 5, 0, -1)
        cv.arrowedLine(mask, (goal, y0), (point, 240 - cropbox[0][0]), 255, 1)

    else: print('there are no contours here')

    return mask






while cv.waitKey(1) != ord('q'):
    _, frame = cap.read()
    hsvframe = cv.cvtColor(frame[cropbox[0][0]:cropbox[0][1], cropbox[1][0]:cropbox[1][1]], cv.COLOR_BGR2HSV)

    frame[460:480, 0:640] = (239, 239, 239)
    frame[0:10, 290:351], frame[10:20, 300:340] = white, white
    cv.circle(frame, (300, 10), 10, white, -1)
    cv.circle(frame, (340, 10), 10, white, -1)

    cv.putText(frame, "3", (314, 15), font, 1, 0, 1)
    cv.putText(frame, "manual", (270, 475), font, 1, 0, 1)

    if state == 0:   # first time gates
        point = 320
        mask = gate(hsvframe, hsvyellow[0], hsvyellow[1])

    elif state == 1: # ball after gates
        point = 50
        mask = ball(hsvframe, hsvyellow[0], hsvyellow[1])

    elif state == 2: # second time gates
        point = 320
        mask = gate(hsvframe, hsvyellow[0], hsvyellow[1])


    frame[cropbox[0][0]:cropbox[0][1], cropbox[1][0]:cropbox[1][1]] = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)

    cv.circle(frame, (point, 240), 5, (0, 0, 255), -1)

    cv.imshow("frame", frame)
    cropbox = cropboxnew


cap.release()
cv.destroyAllWindows()