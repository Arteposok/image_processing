import math
from concurrent.futures.thread import ThreadPoolExecutor

import cv2 as cv
import mss
import numpy as np
import time
import tkinter as tk
import random as rnd

from sympy.codegen.fnodes import dimension


def filter(img):
    use_canny=False
    coal_filter=False
    negate=False
    use_where=True
    edit = img
    black_amount=0.6
    if not use_canny:
        edit = cv.GaussianBlur(edit, (5,5), 0)
        edit = cv.medianBlur(edit, 3)
    edit = cv.GaussianBlur(edit, (3,3), 0)
    if use_canny:
        edit_gray = cv.cvtColor(edit, cv.COLOR_BGR2GRAY)
        edges_colored = cv.Canny(edit_gray, threshold1=50, threshold2=150)
    else:
        edit_gray=cv.cvtColor(edit, cv.COLOR_BGR2GRAY)
        sobel_x = cv.convertScaleAbs(cv.Sobel(edit_gray, cv.CV_64F, 1, 0, ksize=3))
        sobel_y = cv.convertScaleAbs(cv.Sobel(edit_gray, cv.CV_64F, 0, 1, ksize=3))
        edges_colored=cv.addWeighted(sobel_x,0.5,sobel_y,0.5,1)
        #edges_colored = cv.medianBlur(edges_colored, 3)

    edges_colored = cv.cvtColor(edges_colored, cv.COLOR_GRAY2BGR)
    if negate:
        edges_colored=cv.bitwise_not(edges_colored)
    edges_colored=cv.GaussianBlur(edges_colored, (3,3), 0)
    if use_where:
        edit = np.where(edges_colored>30, img, edges_colored)
    else:
        edit = cv.addWeighted(edit, 1-black_amount, edges_colored, black_amount,0)
    return edges_colored if coal_filter else edit

def grab(sct):
    return np.array(sct.grab(sct.monitors[1]))[:, :, :3]

def size(edit, size):
    img = (int(len(edit[0])), int(len(edit)))
    length = math.sqrt(img[0] ** 2 + img[1] ** 2)
    dimensions = [int(img[0] / length * size), int(img[1] / length * size)]
    return cv.resize(edit, dimensions)

def video_loop():
    open_it=False
    fast_save=False
    stich=False
    capture=True
    file_in = "horse_sample.mp4"
    file_out = "recording.mp4"
    video = cv.VideoCapture(0)#file_in if open_it else 0)
    if not video.isOpened():
        print("Error: Couldn't open video.")
        exit()
    codec = cv.VideoWriter_fourcc(*'mp4v')
    screen=np.array(mss.mss().grab(mss.mss().monitors[1]))[:,:,:3]
    fps = video.get(cv.CAP_PROP_FPS) if open_it else 5
    frame_time = 1 / fps
    width = int(video.get(cv.CAP_PROP_FRAME_WIDTH)) if open_it else len(screen[0])
    height = int(video.get(cv.CAP_PROP_FRAME_HEIGHT)) if open_it else len(screen)
    if stich:
        print(width)
        width *= 2
        print(width)
    else:
        width *= 1
    out = cv.VideoWriter(file_out, codec, fps, (width, height))
    frame_n=0
    shoot_next_frame=False
    win=tk.Tk()
    win.resizable=False
    def shoot(*x):
        nonlocal shoot_next_frame
        nonlocal shoot_next_frame
        shoot_next_frame=True
    shot_button=tk.Button(win,text="snapshot", command=shoot)
    shot_button.pack()
    executor=ThreadPoolExecutor()
    with mss.mss() as sct:
        while video.isOpened():
            win.update()
            prev_time = time.perf_counter()
            if open_it:
                ret, frame = executor.submit(video.read).result()
                if not ret:
                    break
            else:
                frame = grab(sct)

            edit = executor.submit(filter,frame).result()
            if stich:
                edit = cv.hconcat([frame, edit])
            if not fast_save:
                cv.imshow("edit", size(edit, 2000))
            out.write(edit)
            if capture and shoot_next_frame:
                x=str(rnd.randint(0,10))
                y=str(rnd.randint(0,10))
                z=str(rnd.randint(0,10))
                cv.imwrite(x+y+z+".png", edit)
                shoot_next_frame=False
            if fast_save:
                continue
            delay = time.perf_counter() - prev_time
            frame_n += 1
            wait = max(0, frame_time - delay)
            time.sleep(wait)
            if cv.waitKey(1) & 0xFF == ord("q") and not fast_save:
                break

    video.release()
    out.release()

def image_shot(name):
    image=cv.imread(name)
    image=filter(image)
    img=(int(len(image[0])), int(len(image)))
    length=math.sqrt(img[0]**2+img[1]**2)
    size=1000
    dimensions=[int(img[0]/length*size), int(img[1]/length*size)]
    image2=cv.resize(image, dimensions)
    cv.imshow(name, image2)
    #cv.imwrite("sample1_out.webp", image)
    cv.waitKey()
    cv.destroyAllWindows()

def images():
    for x in range(1,13):
        image_shot(f"_{x}.png")

video_loop()