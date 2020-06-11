
import binascii
import base64
import datetime
import time
import datetime
import flask_mail
"""
file_ex = b"I am a large file"
with open("C:\\Program Files\\Java\\jdk1.8.0_191\\javafx-src.zip", "rb") as some:
    file_ex = some.read()
file_ex = binascii.b2a_base64(file_ex)
print(type(file_ex))
file_ex = file_ex.decode()
print(type(file_ex))
print("")
print("")
print("")
file_ex = binascii.a2b_base64(file_ex)
print(type(file_ex))
with open("C:\\Users\\razei\\Documents\\Monitoring_Project\\else.zip","wb") as some:
    some.write(file_ex)
"""
b = datetime.datetime.now()
time.sleep(3)
now = datetime.datetime.now()
print(now - b)
print(datetime.timedelta(seconds= 3.2)) 
print( now - b > datetime.timedelta(seconds= 3.2))
for i in range(0,1):
    print("hi")