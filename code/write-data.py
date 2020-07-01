#coding=utf-8
# import the necessary packages
from imutils import paths
import face_recognition
import argparse
import pickle
import cv2
import os
import tkinter.filedialog
from tkinter import ttk
import tkinter as tk
import tkinter.font as tkFont
import sqlite3
import numpy as np

path=""
def selectPath():
	global path
	path = tk.filedialog.askopenfilename(filetypes=[("Image files", ".bmp .jpg .png")]).replace("/", "\\\\")
	status1.configure(text=path)

def cv_imread(file_path):
	cv_img = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
	return cv_img

def submit():
    global path
    conn = sqlite3.connect(".\\person_data.db")
    cursor = conn.cursor()

    idm = idnumber.get()
    sql = "SELECT * FROM person WHERE idnumber='"+idm+"'"
    cursor.execute(sql)
    result = cursor.fetchall()

    stype= 'False' if type.current()==0 else 'True'
    if result!=[]:
        status2.configure(text='错误! 该人员已存在')
    elif (path==""):
        status2.configure(text='错误! 没有选择照片')
    else:
        sql = r"INSERT INTO person VALUES ('"+name.get()+"',"+stype+",'"+idtype.get()+"','"+idnumber.get()+"','"+gender.get()+"','"+phone.get()+"','"+address.get()+"')"
        cursor.execute(sql)
        image = cv_imread(path)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb, model="hog")
        if boxes==[]:
            status2.configure(text='错误! 没有检测到人脸')
            return

        encodings = face_recognition.face_encodings(rgb, boxes)
        f = open("./encodings.pickle", "rb")
        data=pickle.loads(f.read())
        data["encodings"].append(encodings[0])
        data["names"].append(name.get())
        f = open("./encodings.pickle", "wb")
        f.write(pickle.dumps(data))

        h=image.shape[0];w=image.shape[1]
        u, r, d, l = boxes[0]
        l = 0 if l - 100 < 0 else l - 100
        r = w if r + 100 > w else r + 100
        u = 0 if u - 100 < 0 else u - 100
        d = h if d + 100 > h else d + 100
        image = image[u:d, l:r]
        cv2.imencode('.jpg', image)[1].tofile("./dataset/"+name.get()+"+"+idtype.get()+"+"+idnumber.get()+".jpg")

        path=''
        status1.configure(text=path)
        status2.configure(text='人员信息登记成功')

    conn.commit()
    conn.close()


root = tk.Tk()
tk.Label(root,text="进入小区人员信息登记").grid(row=0,column=0,columnspan=2)
tk.Label(root,text="姓名：").grid(row=1,column=0)
name = tk.Entry(root); name.grid(row=1,column=1)
tk.Label(root,text="人员类型：").grid(row=2,column=0)
type=ttk.Combobox(root, values=["外来人员","小区居民"], state="readonly"); type.grid(row=2,column=1)
tk.Label(root,text="证件类型：").grid(row=3,column=0)
idtype = ttk.Combobox(root, values=["身份证","护照"], state="readonly"); idtype.grid(row=3,column=1)
tk.Label(root,text="证件号码：").grid(row=4,column=0)
idnumber = tk.Entry(root); idnumber.grid(row=4,column=1)
tk.Label(root,text="性别：").grid(row=5,column=0)
gender = ttk.Combobox(root, values=["男","女"], state="readonly"); gender.grid(row=5,column=1)
tk.Label(root,text="电话号码：").grid(row=6,column=0)
phone = tk.Entry(root); phone.grid(row=6,column=1)
tk.Label(root,text="住址：").grid(row=7,column=0)
address = tk.Entry(root); address.grid(row=7,column=1)
tk.Label(root,text="照片：").grid(row=8,column=0)
tk.Button(root, text = "选择路径", command = selectPath).grid(row = 8, column = 1)
status1=tk.Label(root,text=""); status1.grid(row=9,column=0,columnspan=2)
button = tk.Button(text ="提交", command = submit); button.grid(row=10,column=0,columnspan=2,pady=20)
status2=tk.Label(root,text=""); status2.grid(row=11,column=0,columnspan=2)
root.mainloop()
