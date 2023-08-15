from lib.RobotAPI import RobotAPI
import cv2 as cv, numpy as np, serial, time

mega, rapi = serial.Serial("/dev/ttyS0", baudrate=115200, stopbits=serial.STOPBITS_ONE), RobotAPI(flag_serial=False)
rapi.set_camera(100, 320, 240)
fps, cntfps, timfps = 0, 0, 0
mode, compass = 0, 0
flagplay = False
message = ""
font = cv.FONT_HERSHEY_DUPLEX



def playbutton():
    global flagplay
    if cv.waitKey(1) == 80: flagplay = not flagplay


def telemetry(image):
    global flagplay, mode, fps, cntfps, timfps
    downbox = np.zeros((20, 320, 3), np.uint8)

    # compass
    if   compass > 99: strmidx = 145
    elif compass > 9:  strmidx = 149
    else:              strmidx = 155
    cv.putText(image, str(compass), (strmidx, 15), font, 0.5, (100, 200, 255), 1)

    # pause button on HOME key
    if not flagplay:
        mode = 0
        cv.line(frame, (145, 100), (145, 140), (255, 255, 255), 5)
        cv.line(frame, (175, 100), (175, 140), (255, 255, 255), 5)
        cv.putText(downbox, "| |", (5, 13), font, 0.35, (255, 255, 255), 2)

    # mode
    strmode = "None"
    if   mode == 0: strmode, strmidx = "Neutral",    124
    elif mode == 1: strmode, strmidx = "Autonomous", 108
    elif mode == 2: strmode, strmidx = "Manual",     127
    cv.putText(downbox, strmode, (strmidx, 15), font, 0.5, 1)

    # fps
    cntfps, tim = cntfps + 1, time.time()  # fps
    if tim > timfps:
        fps, cntfps, timfps = cntfps, 0, tim
    cv.putText(downbox, str(fps), (320 - 25, 15), font, 0.5, 1)


    rapi.set_frame(np.concatenate((image, downbox), 0), 40)


def uartmega():
    global mode, compass
    mode, compass = mega.read(), mega.read(3)  # mega uart
    compass -= 100

    if not flagplay: mode = 0

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

if __name__ == "__main__":
    while True:
        frame = rapi.get_frame(wait_new_frame=1)


        uartmega()
        playbutton()
        telemetry(frame)