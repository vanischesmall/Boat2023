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
mode = 0



def telemetry(image):
    global fps, cntfps, timfps
    image[0:10, 290:351], image[10:20, 300:340] = white, white # downbox
    cv.circle(image, (300, 10), 10, white, -1)
    cv.circle(image, (340, 10), 10, white, -1)

    image[460:480, 0:640] = (239, 239, 239)                    # browbox

    # compass
    if   compass > 99: strcompass = (str(compass), 300)
    elif compass > 9:  strcompass = (str(compass), 308)
    else:              strcompass = (str(compass), 314)
    cv.putText(image, strcompass[0], (strcompass[1], 15), font, 1, 0, 1)

    # pause
    if not flagplay:
        cv.putText(image, "| |", (5, 475), font, 0.75, 0, 3)

    # mode
    if   mode == 0: strmode = ("neutral", 270)
    elif mode == 1: strmode = ("manual", 270)
    elif mode == 2: strmode = ("autonomous", 248)
    cv.putText(image, strmode[0], (strmode[1], 475), font, 1, 0, 1)

    # fps
    cntfps, tim = cntfps + 1, time.time()  # fps
    if tim > timfps + 1:
        fps, cntfps, timfps = cntfps, 0, tim
    cv.putText(image, str(fps), (610, 15), font, 1, 0, 1)


    rapi.set_frame(image, 40)

def uartmega():
    global mode, compass

    mega.write(message.encode('utf-8'))


def gate(hsvframe, low, high):
    mask = cv.inRange(hsvframe, low, high)

    cm0, sm0, cm1, sm1 = 0, 0, 0, 0
    cnts, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        sc = cv.contourArea(c)
        if sc > sm0:
            cm0, sm0 = c, sc
            if sm0 > sm1:
                cm0, sm0, cm1, sm1 = cm1, sm1, c, sc

    x0, y0, w0, h0 = cv.boundingRect(cm0)
    x1, y1, w1, h1 = cv.boundingRect(cm1)
    x0, x1 = x0 + w0 // 2, x1 + w1 // 2
    goal = (x0 + x1) // 2

    cv.circle(mask, (x0,   y0 + h0//2), 5, 0, -1)
    cv.circle(mask, (x1,   y1 + h1//2), 5, 0, -1)
    # cv.circle(mask, (goal, y1 + h1//2), 5, 255, -1)

    cv.arrowedLine(mask, (320, 300), (goal, y1 + h1//2), 255, 1)




if __name__ == "__main__":
    while rapi.get_key() != 110: telemetry(rapi.get_frame(wait_new_frame=1))
    flagplay = True

    while True:
        frame = rapi.get_frame(wait_new_frame=1)













        # uartmega()
        telemetry(frame)