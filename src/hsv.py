import cv2 as cv
from lib import RobotAPI

cap = cv.VideoCapture(0)
h, s, v = 0,   0,   0
H, S, V = 255, 255, 255

while True:
    _, frame = cap.read()

    key = cv.waitKey(1)
    if   key == ord('q'): h += 5
    elif key == ord('a'): h -= 5
    elif key == ord('w'): s += 5
    elif key == ord('s'): s -= 5
    elif key == ord('e'): v += 5
    elif key == ord('d'): v -= 5
    elif key == ord('r'): H += 5
    elif key == ord('f'): H -= 5
    elif key == ord('t'): S += 5
    elif key == ord('g'): S -= 5
    elif key == ord('y'): V += 5
    elif key == ord('h'): V -= 5

    if   h < 0:   h = 0
    elif h > 255: h = 255
    if   s < 0:   s = 0
    elif s > 255: s = 255
    if   v < 0:   v = 0
    elif v > 255: v = 255;
    if   H < 0:   H = 0
    elif H > 255: H = 255
    if   S < 0:   S = 0
    elif S > 255: S = 255
    if   V < 0:   V = 0
    elif V > 255: V = 255

    if key == ord('z'):
        h, s, v = 0,   0,   0
        H, S, V = 255, 255, 255
    color = ((h, s, v), (H,   S,   V  ))

    frame = cv.bitwise_and(frame, cv.cvtColor(cv.inRange(frame, color[0], color[1]), cv.COLOR_GRAY2BGR))
    cv.imshow('frame', frame)
    print(color)