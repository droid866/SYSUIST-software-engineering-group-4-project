# coding=utf-8
from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import time
import concurrent.futures
import cv2
import os
import serial
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import tkinter.font as tkFont

ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", type=str,default="encodings.pickle",
    help="path to serialized db of facial encodings")
ap.add_argument("-o", "--output", type=str,default='output/webcam_face_recognition_output.avi',
    help="path to output video")
ap.add_argument("-d", "--detection-method", type=str, default="hog",
    help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())

def findfile(dir, name):
    for relpath, dirs, files in os.walk(dir):
        for filename in files:
            if filename.split('.')[0].split('+')[0] == name:
                full_path = os.path.join(relpath, filename)
                return os.path.normpath(os.path.abspath(full_path))

def recognize(rgb,boxes):
    encodings = face_recognition.face_encodings(rgb, boxes)
    return encodings

def getTemperature():
    ser.write(bytes.fromhex('A55501FB'))
    try:
        output=ser.read(7)
    except:
        print('read tempature failed!')
    Distance=(output[5]*256+output[4])/10
    Temperature=(output[3]*256+output[2])/100
    return (Distance,Temperature)

print("[INFO] loading encodings...")
data = pickle.loads(open(args["encodings"], "rb").read())
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
writer = None
time.sleep(2.0)
print("[INFO] successful!")

Tempature_Module_Loaded=0
try:
    ser = serial.Serial()
    ser.port = 'COM3'
    ser.baudrate = 115200
    ser.bytesize = 8
    ser.parity = serial.PARITY_NONE
    ser.stopbits = 1
    ser.timeout = 0.2
    ser.open()
    Tempature_Module_Loaded=1
    print("Tempature module loaded!")
except:
    print("Tempature module not found!")

cnt=0
no_face=0
boxes=[]
names=[]
encodings=np.zeros([1,128])

def detect():
    global cnt, no_face, boxes, names, encodings
    frame = vs.read()[60:420,0:640]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb = imutils.resize(rgb, width=300)

    brightness = rgb.mean(axis=0).mean(axis=0).mean()
    val = 150 - int(brightness)
    rgb = np.where(rgb > 255-val, 255, rgb + val)

    iw, ih = Image.fromarray(rgb).size
    new_img = ImageTk.PhotoImage(Image.fromarray(rgb).crop(((iw - ih) / 2, 0, (iw + ih) / 2, ih)).resize([w, w]))
    label_img1.configure(image=new_img)
    label_img1.image = new_img

    cnt+=1
    if cnt%5==0:
        detected = face_recognition.face_locations(rgb,model=args["detection_method"])
        if detected!=[] or no_face>=6:
            boxes=detected
            no_face=0
        else:
            no_face+=1

    if cnt%50==10:
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #    future = executor.submit(lambda p: recognize(*p),(rgb,boxes))
        #    encodings = future.result()

        encodings = recognize(rgb,boxes)
        names = []
        try:
            for encoding in encodings:
                matches = face_recognition.compare_faces(data["encodings"], encoding)
                name = "Unknown"
                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    name = max(counts, key=counts.get)

                names.append(name)
        except:
            print("encodings not a list")

    if (names!=[] and names[0]!='Unknown'):
        label_1.configure(text='检测到住户:')
        label_2.configure(text=names[0])

        try:
            imgfile=findfile(r'./dataset',names[0])
            img_person=ImageTk.PhotoImage(Image.open(imgfile).resize([h1, h1]))
            label_img2.configure(image=img_person)
            label_img2.image = img_person
        except:
            None

        if Tempature_Module_Loaded==0:
            string = '体温模块未加载'
            label_4.configure(bg="DodgerBlue2", text='')
        else:
            string = '体温检测结果: '
            (Distance, Temperature) = getTemperature()
            string = string + str(Temperature) + '度';
            if Temperature <34 or Distance<20 or Distance>60:
                string='未检测到体温'
                label_4.configure(bg="DodgerBlue2",text='')
            elif Temperature<37.5:
                label_4.configure(fg = "khaki1",bg = "forest green",text='允许通行')
            else:
                label_4.configure(fg = "khaki1",bg = "red",text='禁止通行')
        label_3.configure(text=string)
    else:
        label_1.configure(text='')
        label_2.configure(text='人脸识别中...')
        label_3.configure(text='')
        label_4.configure(bg="DodgerBlue2", text='')
        label_img2.configure(image=img_default)
        label_img2.image = img_default

    root.after(10, detect)

root = tk.Tk()

#w, h = root.maxsize()
#root.geometry("{}x{}".format(w, h)) 
#root.attributes("-fullscreen", True)

w=300;h=512 #delete

h1=(h-w)//2
font1 = tkFont.Font(family='microsoft yahei', size=16, weight='bold')

f0 = tk.Frame(root,width=w,height=w,bg="light sky blue")
f0.pack_propagate(0)
f0.grid(row=0, column=0,columnspan=2,sticky='nsew')
img_png = ImageTk.PhotoImage(Image.open('who.jpg').resize([w,w]))
label_img1=tk.Label(f0, image = img_png ,width=w,height=w)
label_img1.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

f1 = tk.Frame(root,width=w-h1,height=h1,bg="light sky blue")
f1.pack_propagate(0)
f1.grid(row=1, column=0,sticky='nsew')
label_1=tk.Label(f1,text="人脸识别中...",fg = "gold4",bg = "light sky blue",font=font1)
label_1.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
label_2=tk.Label(f1,text="",fg = "gold4",bg = "light sky blue",font=font1)
label_2.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

f11 = tk.Frame(root,width=h1,height=h1,bg="light sky blue")
f11.pack_propagate(0)
f11.grid(row=1, column=1,sticky='nsew')
img_default = ImageTk.PhotoImage(Image.open('who.jpg').resize([h1,h1]))
label_img2=tk.Label(f11, image = img_default ,width=h1,height=h1)
label_img2.pack(side=tk.RIGHT)

f2 = tk.Frame(root,width=w,height=h1//2,bg="light sky blue")
f2.pack_propagate(0)
f2.grid(row=2, column=0,columnspan=2,sticky='nsew')
label_3=tk.Label(f2,text="体温检测中...",fg = "gold4",bg = "light sky blue",font=font1)
label_3.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

f3 = tk.Frame(root,width=w,height=h1//2,bg="light sky blue")
f3.pack_propagate(0)
f3.grid(row=3, column=0,columnspan=2,sticky='nsew')
label_4=tk.Label(f3,text="",fg = "gold4",bg = "DodgerBlue2",font=font1)
label_4.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)

#root.attributes("-fullscreen", True)
root.geometry("300x512") #delete

root.after(100, detect)
root.mainloop()  # 进入消息循环