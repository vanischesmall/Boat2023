import RobotAPI
import cv2 as cv, numpy as np, serial, time

mega, rapi = serial.Serial("/dev/ttyS0", baudrate=115200, stopbits=serial.STOPBITS_ONE), RobotAPI.RobotAPI(flag_serial=False)
rapi.set_camera(100, 1280, 720, 0)
fps, cntfps, timfps = 0, 0, 0
white = (239, 239, 239)
mode, compass = 0, 0
flagplay = False
message = ""
font = cv.FONT_HERSHEY_COMPLEX_SMALL
mode = 2
cropbox, cropboxnew = ((20, 460), (0, 640)), ((20, 460), (0, 640))

hsvyellow = ((0, 0, 0), (85, 255, 255))

currentstate = 0
goal, dist = 0, 0


def gate(hsvframe, low, high):
    global goal, dist, cropboxnew
    mask = cv.inRange(hsvframe, low, high)

    cntcnts, cm0, sm0, cm1, sm1 = 0, 0, 0, 0, 0
    for c in cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[0]:
        sc = cv.contourArea(c)
        if sc > sm0 and sc > 5000:
            cntcnts += 1
            cm0, sm0 = c, sc
            if sm0 > sm1:
                cm0, sm0, cm1, sm1 = cm1, sm1, c, sc

    cropboxnew = ((20, 460), (0, 640))
    if cntcnts >= 2:
        x0, y0, w0, h0 = cv.boundingRect(cm0)
        x1, y1, w1, h1 = cv.boundingRect(cm1)
        x0, x1 = x0 + w0 // 2, x1 + w1 // 2

        goal, dist = (x0 + x1) // 2, abs(x0 - x1)

        cropy = cropbox[0][0] + min(y0, y1) - 50
        croph = cropy + max(h0, h1) + 100
        if cropy < 20: cropy = 20
        if croph > 460: croph = 460
        cropboxnew = ((cropy, croph), (0, 640))

        cv.circle(mask, (x0,   y0 + h0//2), 5, 0, -1)
        cv.circle(mask, (x1,   y1 + h1//2), 5, 0, -1)

        cv.arrowedLine(mask, (cropbox[1][1] // 2, cropbox[0][1]), (goal, y1 + h1//2), 255, 1)
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


def telemetry(image):
    global fps, cntfps, timfps
    # image[0:10, 290:351], image[10:20, 300:340] = white, white # downbox
    # cv.circle(image, (300, 10), 10, white, -1)
    # cv.circle(image, (340, 10), 10, white, -1)

    # image[460:480, 0:640] = (239, 239, 239)                    # browbox

    # # compass
    # if   compass > 99: strcompass = (str(compass), 300)
    # elif compass > 9:  strcompass = (str(compass), 308)
    # else:              strcompass = (str(compass), 314)
    # cv.putText(image, strcompass[0], (strcompass[1], 15), font, 1, 0, 1)

    # pause
    if not flagplay:
        mode = 0
        cv.putText(image, "| |", (5, 475), font, 0.75, 0, 3)

    # # mode
    # strmode = ""
    # if   mode == 0: strmode = ("neutral", 270)
    # elif mode == 1: strmode = ("manual", 270)
    # elif mode == 2: strmode = ("autonomous", 248)
    # cv.putText(image, strmode[0], (strmode[1], 475), font, 1, 0, 1)

    # fps
    cntfps, tim = cntfps + 1, time.time()  # fps
    if tim > timfps + 1:
        fps, cntfps, timfps = cntfps, 0, tim
    cv.putText(image, str(fps), (610, 475), font, 1, 0, 1)


    rapi.set_frame(image, 40)

def uartmega():
    global mode, compass

    mega.write(message.encode('utf-8'))






if __name__ == "__main__":
    while rapi.get_key() != 110: telemetry(rapi.get_frame(wait_new_frame=1))
    flagplay = True

    while True:
        frame = rapi.get_frame(wait_new_frame=1)
        hsvframe = cv.cvtColor(frame[cropbox[0][0]:cropbox[0][1], cropbox[1][0]:cropbox[1][1]], cv.COLOR_BGR2HSV)




        # mask = gate(hsvframe, hsvyellow[0], hsvyellow[1])
        # frame[cropbox[0][0]:cropbox[0][1], cropbox[1][0]:cropbox[1][1]] = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)


        cropbox = cropboxnew
        # uartmega()
        telemetry(frame)
