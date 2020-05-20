
import binascii
import base64
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
