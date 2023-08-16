import RobotAPI
import cv2 as cv, numpy as np, serial, time

mega, rapi = serial.Serial("/dev/ttyS0", baudrate=115200, stopbits=serial.STOPBITS_ONE), RobotAPI.RobotAPI(flag_serial=False)
rapi.set_camera(100, 640, 480)
fps, cntfps, timfps = 0, 0, 0
white = (239, 239, 239)
mode, compass = 0, 0
flagplay = False
message = ""
font = cv.FONT_HERSHEY_DUPLEX



def telemetry(image):
    global fps, cntfps, timfps
    frame[0:10, 290:351], frame[10:20, 300:340] = white, white # downbox
    cv.circle(frame, (300, 10), 10, white, -1)
    cv.circle(frame, (340, 10), 10, white, -1)

    frame[460:480, 0:640] = (239, 239, 239)                    # browbox


    # fps
    cntfps, tim = cntfps + 1, time.time()  # fps
    if tim > timfps + 1:
        fps, cntfps, timfps = cntfps, 0, tim
    cv.putText(image, str(fps), (610, 15), font, 1, 0, 1)


    rapi.set_frame(frame, 40)


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
    while rapi.get_key() != 110: telemetry(rapi.get_frame(wait_new_frame=1))
    flagplay = True
    while True:
        frame = rapi.get_frame(wait_new_frame=1)













        # uartmega()
        telemetry(frame)