from lib.RobotAPI import RobotAPI
import cv2 as cv, numpy as np, serial, time

framew, frameh = 320, 240
mega, rapi = serial.Serial("/dev/ttyS0", baudrate=115200, stopbits=serial.STOPBITS_ONE), RobotAPI(flag_serial=False)
rapi.set_camera(100, framew, frameh)
fps, cntfps, timfps = 0, 0, 0
mode, compass = 0, 0
message = ""

font = cv.FONT_HERSHEY_COMPLEX_SMALL
white = (255, 255, 255)


def telemetry(image):
    global fps, cntfps, timfps
    boxh = 10
    upbox, downbox = np.zeros((framew, boxh, 1), np.uint8), np.zeros((framew, boxh, 1), np.uint8)

    # compass
    strmidx = int(framew / 2) - int(cv.getTextSize(str(compass), font, 1, 2)[0] / 2)
    cv.putText(upbox, str(compass), (strmidx, 2), font, 1, 1)

    # mode
    strmode = "None"
    if mode == 0: strmidx, strmode = cv.getTextSize("Neutral",    font, 1, 2)[0], "Neutral"
    if mode == 1: strmidx, strmode = cv.getTextSize("Autonomous", font, 1, 2)[0], "Autonomous"
    if mode == 2: strmidx, strmode = cv.getTextSize("Manual",     font, 1, 2)[0], "Manual"
    cv.putText(downbox, strmode, (strmidx, 2), font, 1, 1)

    # fps
    cntfps, tim = cntfps + 1, time.time()  # fps
    if tim > timfps:
        fps, cntfps, timfps = cntfps, 0, tim
    cv.putText(downbox, str(fps), (framew - 40, 2), font, 1, 1)


    rapi.set_frame(np.concatenate((np.concatenate((upbox, image), 0), downbox), 0), 40)


def uartmega():
    global mode, compass
    mode, compass = mega.read(), mega.read(3)  # mega uart
    compass -= 100

    mega.write(message.encode('utf-8'))


# oxoy = (320, 240)
# white = (255, 255, 255)
# def gate(hsvframe, low, high):
#     global frame
#     mask = cv.inRange(hsvframe, low, high)
#
#     sm0, sm1 = 0, 0
#     cm0, cm1 = 0, 0
#     cnts, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
#     if len(cnts) > 1:
#         for c in cnts:
#             sc = cv.contourArea(c)
#             if sc > 1000:
#                 if sc > sm0:
#                     sm0 = sc
#                     cm0 = c
#                     if sm0 > sm1:
#                         sm0, sm1 = sm1, sc
#                         cm0, cm1 = cm1, c
#
#         x0, y0, w0, h0 = cv.boundingRect(cm0)
#         x1, y1, w1, h1 = cv.boundingRect(cm1)
#         left, right = x0 + w0 // 2, x1 + w1 // 2
#
#         cv.rectangle(frame, (x0, y0), (x0 + w0, y0 + h0), white, 2)
#         cv.rectangle(frame, (x1, y1), (x1 + w1, y1 + h1), white, 2)
#
#         if x0 < x1:
#             left, right, yl, yr = left, right, y0, y1
#         else:
#             left, right, yl, yr = right, left, y1, y0
#
#         cv.circle(frame, (left, yl), 5, white, -1)
#         cv.circle(frame, (right, yr), 5, white, -1)
#
#         goal = (left + right) // 2
#         cv.arrowedLine(frame, (480, oxoy[1]), (goal, (yl + yr) // 2), white, 1)


while True:
    frame = rapi.get_frame(wait_new_frame=1)

    uartmega()
    telemetry()
