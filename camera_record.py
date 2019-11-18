import cv2
import numpy as np 
import os
from threading import Thread
import queue
import time

FPS = 24.0
my_res = '720p'
time_record = 3 #minutes
path = 0    #what camera is used to record

def change_res(cap, width, height):
    cap.set(3, width)
    cap.set(4, width)

STD_DIMENSIONS = {
    "480p": (640, 480),
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "4k": (3840, 2160),
}

def get_dims(cap, res='1080p'):
    width, height = STD_DIMENSIONS['480p']
    if res in STD_DIMENSIONS:
        width, height = STD_DIMENSIONS[res]
    change_res(cap, width, height)
    return width, height

VIDEO_TYPE = {
    'avi': cv2.VideoWriter_fourcc(*'XVID'),
    'mp4': cv2.VideoWriter_fourcc(*'XVID'),
}

def get_video_type(filename):
    filename, ext = os.path.splitext(filename)
    if ext in VIDEO_TYPE:
        return VIDEO_TYPE[ext]
    return VIDEO_TYPE['avi']

def record_video(path, filename, q):
    cap = cv2.VideoCapture(path)
    dims = get_dims(cap, res=my_res)
    video_type_cv2 = get_video_type(filename)
    out = cv2.VideoWriter(filename, video_type_cv2, FPS, dims)
    while (q.qsize() == 0):
        ret, frame = cap.read()
        if ret == True:
            out.write(frame)
            cv2.imshow(filename, frame)
            if cv2.waitKey(20) & 0xff == ord('q'):
                break
        else:
            print("cannot read")
            break
    q.get()
    cap.release()
    out.release()

    
#main video control
count_minutes = 0
while (count_minutes <= time_record):
    interrupt_queue = queue.Queue()
    if (interrupt_queue.qsize() == 0):
        filename = 'Video_' + str(count_minutes) + '.avi'

        #star record video in 1 minute
        t_record_video = Thread(target=record_video, args=(path, filename, interrupt_queue,))
        t_record_video.start()
        print(interrupt_queue.qsize())
        time.sleep(10)
        #after record 1 minute
        interrupt_queue.put(1)
        t_record_video.join()

        print(count_minutes)
        count_minutes += 1

cv2.destroyAllWindows()