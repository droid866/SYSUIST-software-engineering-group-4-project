# coding:utf-8
import sqlite3
import pickle
import numpy as np
conn = sqlite3.connect(".\\person_data.db")
cursor = conn.cursor()

sql= r"DELETE FROM person"
cursor.execute(sql)

sql= r"SELECT * FROM person WHERE idnumber='asd'"
cursor.execute(sql)
result = cursor.fetchall()
print (result,type(result))

data={"encodings":[np.zeros(128)],"names":['Nobody']}
f = open("./encodings.pickle", "wb")
f.write(pickle.dumps(data))

'''
sql = """DROP TABLE person"""
cursor.execute(sql)
sql = """CREATE TABLE person (
name TEXT(10) NOT NULL,
isresident BOOLEAN NOT NULL,
idtype TEXT(20) NOT NULL,
idnumber TEXT(20) PRIMARY KEY  NOT NULL,
gender TEXT(5) NOT NULL,
phone TEXT(20),
address TEXT(50)
)"""
cursor.execute(sql)
'''
conn.commit()
conn.close()