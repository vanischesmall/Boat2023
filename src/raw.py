import cv2 as cv
import time
import RobotAPI as rapi
import serial
import numpy as np
mega = serial.Serial("/dev/ttyS0", baudrate=115200, stopbits=serial.STOPBITS_ONE)

robot = rapi.RobotAPI(flag_serial=False)
robot.set_camera(100, 640, 480)
fps = 0
fps_count = 0
t = time.time()



while 1:
    downbox = np.zeros((20, 640, 3), np.uint8)
    frame = robot.get_frame(wait_new_frame=1)

    fps_count += 1
    if time.time() > t + 1:
        fps = fps_count
        fps_count = 0
        t = time.time()

    uartmega()



    cv.putText(downbox, strmega, (300, 15), cv.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1)

    robot.set_frame(np.concatenate((frame, downbox), 0), 40)

