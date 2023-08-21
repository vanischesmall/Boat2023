import cv2
import platform
index = 0 # capture device index

if platform.system() == "Windows":
    cv2.CAP_DSHOW
    #sets the Windows cv2 backend to DSHOW (Direct Video Input Show)
    cap = cv2.VideoCapture(index)
elif platform.system() == "Linux":
    cv2.CAP_GSTREAMER # set the Linux cv2 backend to GTREAMER
    #cv2.CAP_V4L
    cap = cv2.VideoCapture(index)
else:
    cap = cv2.VideoCapture(index)
    # For MAC please refer to link below for I/O
    cap.set(cv2.CAP_FFMPEG, cv2.CAP_FFMPEG_VIDEOTOOLBOX) # not sure!
    #please refer to reference link at bottom of page for more I/O

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840) # 4k/high_res
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160) # 4k/high_res
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print(width, height)

_, frame = cap.read()
height, width = frame.shape[:2]
print(width, height)

cap.release()