import requests
from flask_restful import Resource, Api
from flask import Flask, render_template, url_for, request, redirect, jsonify, abort, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import json
import datetime
import itertools 
from sqlalchemy import func
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import psycopg2
import redis
import os
import boto3
import binascii
from botocore.errorfactory import ClientError
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
#from celery import Celery
from flask_celery import make_celery
new_id = -1
new_mac_address = ""
change = 5000
js = ""
BUCKET = "file-download-storage"

app = Flask(__name__)
#app.config.from_envvar('APP_SETTINGS')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://uivkoiklvmepxq:0645866a06af656a780eb209d676aa6fdc2296d3ff44b82259b0dce0cc03e913@ec2-54-75-246-118.eu-west-1.compute.amazonaws.com:5432/d1c775di51cvi5'
app.config['SECRET_KEY'] = "thisistopsecret"
app.config["CELERY_BROKER_URL"] =  "redis://h:pb21f80cdd33b165745a56fbab1e6525ca2d57fc2e91536ab978ac536acca8eea@ec2-52-31-111-39.eu-west-1.compute.amazonaws.com:8449"
app.config["CELERY_RESULT_BACKEND"] = "redis://h:pb21f80cdd33b165745a56fbab1e6525ca2d57fc2e91536ab978ac536acca8eea@ec2-52-31-111-39.eu-west-1.compute.amazonaws.com:8449"
app.config["SESSION_PERMANENT"] = False
celery = make_celery(app)

celery.conf.update(BROKER_URL = "redis://h:pb21f80cdd33b165745a56fbab1e6525ca2d57fc2e91536ab978ac536acca8eea@ec2-52-31-111-39.eu-west-1.compute.amazonaws.com:8449",
                CELERY_RESULT_BACKEND="redis://h:pb21f80cdd33b165745a56fbab1e6525ca2d57fc2e91536ab978ac536acca8eea@ec2-52-31-111-39.eu-west-1.compute.amazonaws.com:8449")
db = SQLAlchemy(app)
app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'raz.monitor.website@gmail.com',
    MAIL_PASSWORD = 'AdminMonitor2020',
))
mail = Mail(app)
ser = URLSafeTimedSerializer(app.config['SECRET_KEY'])
redis_server = redis.from_url("redis://h:pb21f80cdd33b165745a56fbab1e6525ca2d57fc2e91536ab978ac536acca8eea@ec2-52-31-111-39.eu-west-1.compute.amazonaws.com:8449",charset="utf-8", decode_responses=True)
admin = Admin(app,url="/admindb")
login_manager = LoginManager()
login_manager.init_app(app)
class Todo(db.Model):
    __tablename__ = "Todo"
    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.TEXT)
    cpu_type = db.Column(db.TEXT, default="1.0")
    ram_usage = db.Column(db.FLOAT, default=1.0)
    running_processes = db.Column(db.TEXT,default="initializing")
    cpu_usage_procentage = db.Column(db.FLOAT, default=1.0)
    memory_usage_procentage = db.Column(db.FLOAT, default=1.0)
    directory_request = db.Column(db.TEXT, default="")
    directory_response = db.Column(db.TEXT, default="")
    """
    def __init__(self,id,mac_address,cpu_type,ram_usage,running_processes,cpu_usage_procentage,memory_usage_procentage):
        self.mac_address = mac_address
        self.id = id
        self.cpu_type = cpu_type
        self.ram_usage = ram_usage
        self.running_processes = running_processes
        self.cpu_usage_procentage = cpu_usage_procentage
        self.memory_usage_procentage = memory_usage_procentage
    """
admin.add_view(ModelView(Todo, db.session))
class users(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.TEXT, unique=True)
    password = db.Column(db.TEXT)
    email = db.Column(db.TEXT)
    level = db.Column(db.INTEGER) #level 1 - regular employee, level 2 - Team leader, level 3 - Manager
    computer_id = db.Column(db.Integer, default=-1) 
    allow_to_view_level_2 = db.Column(db.TEXT, default="None")
admin.add_view(ModelView(users, db.session))


@login_manager.user_loader
def load_user(user_id):
    return users.query.get(int(user_id))

@app.route('/login', methods=['POST', 'GET'])
@login_manager.unauthorized_handler
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        check_box = request.form['CheckBox']
        print(check_box)
        print(check_box)
        send = ""
        user_check = bool(users.query.filter_by(username=username).first())
        pass_check = bool(users.query.filter_by(password=password).first())
        if user_check and not pass_check:
            return "password"
        elif not user_check:
            return "username"
        else:
            user = users.query.filter_by(username=username,password=password).first()
            if user.email_authentication == False:
                return "email"
            app.permanent_session_lifetime = False
            
            if check_box == "True":
                login_user(user, remember=True)
            elif check_box == "False":
                login_user(user, remember=False)
            else:
                return "An unexpected error has occurred"
            return "Great"
            
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect('/')
        else:
            return render_template('/login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        print(username)
        send = ""
        computer = users.query.filter(func.lower(users.username) == func.lower(username)).first()
        print(computer)
        if computer is not None:
            print("in")
            now = datetime.datetime.now()
            if now - computer.registered_date > datetime.timedelta(seconds= 300) and computer.email_authentication is False:
                db.session.delete(computer)
                db.session.commit()
        user_check = bool(users.query.filter(func.lower(users.username) == func.lower(username)).first())
        email_check = bool(users.query.filter_by(email=email).first())
        
        if (email_check) and ("@gmail.com" not in email) and user_check:
            print("all")
            return "all"
        elif user_check and ("@gmail.com" not in email):
            print("u e c")
            return "username exist email contain"
        elif user_check and email_check:
            print("u e e")
            return "username exist email exist"
        elif email_check:
            return "email exist"
        elif "@gmail.com" not in email:
            return "email contain"
        elif user_check:
            return "username exist"
        else:
            reg_token = ser.dumps(email, salt="email-confirmation")
            email_msg = Message('Email Confirmation for admin monitor', sender='raz.monitor.website@gmail.com', recipients=[email])
            mail_link = url_for('email_confirmation', emailToken = reg_token, _external= True)
            email_msg.body = "Confirmation Link: " + mail_link
            mail.send(email_msg)
            if len(users.query.all()) == 0:
                new_user = users(username = username, password=password, email=email, level=3, email_authentication_token=reg_token)
                db.session.add(new_user)
                db.session.commit()
            else:
                new_user = users(username = username, password=password, email=email, level=1, email_authentication_token=reg_token)
                db.session.add(new_user)
                db.session.commit()
            return redirect('/')
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect('/')
        else:
            return render_template('/register.html')


@app.route("/email/confim/<emailToken>")
def email_confirmation(emailToken):
    try:
        computer = users.query.filter_by(email_authentication_token=emailToken).first()
        email = ser.loads(emailToken, salt="email-confirmation", max_age=300)
    except SignatureExpired:
        return "The Token has ended."
    print(computer.email_authentication)
    computer.email_authentication = True
    computer.email_authentication_token = ""
    db.session.commit()
    return "Token is good, you can log in now!" #create template


@app.route("/computers/<int:id>/inital-call", methods=['POST'])
def inital_data(id):
    print("inital call!")
    computer = Todo.query.get_or_404(id)
    #redis_server = redis.Redis("localhost",charset="utf-8", decode_responses=True)
    
    redis_response_name = "directory response" + str(id)
    redis_request_name = "directory request" + str(id)
    redis_server.delete(redis_response_name)
    redis_server.delete(redis_request_name)
    redis_server.delete("download" + str(id))
    redis_server.delete("file-name" + str(id))
    redis_server.delete("directory name" + str(id))
    return ""

#verify_login
@app.route('/computers/verify_login', methods=['POST', 'GET'])
def check_if_user_exists():
    if request.method == 'POST':
        global new_mac_address
        js = request.get_json()
        print(js)
        if js is not None:
            mac_address = js['mac_address']
            print("MAC: " + mac_address)
            print(len(Todo.query.all()))
            for i in range(0,len(Todo.query.all())):
                current_id = Todo.query.all()[i].id
                current_mac = Todo.query.all()[i].mac_address
                if mac_address == current_mac:
                    print("True!")
                    #redis_server = redis.Redis("localhost",charset="utf-8", decode_responses=True)
                    
                    
                    return str(current_id)
            new_mac_address = mac_address
            print("Not found!?")
            return redirect('/computers/add')
        else:
            print("Empty? wtf")
    else:   
        return ""




def no_one_in_db_code(id):
    global js
    computer = Todo.query.get_or_404(id)
    js = request.get_json()
    for name, item in js.items():
        if name == "CPU type: ":
            computer.cpu_type = item
            db.session.add(computer)
            db.session.commit()
        if name == "Ram usage: ":
            computer.ram_usage = item
            db.session.add(computer)
            db.session.commit()
        if name == "running processes":
            new_item = []
            count = 0
            pid = []
            name = []
            memory_percent = []
            cpu_percent = []
            f = item
            for i in item:
                if count == 0:
                    pass
                else:
                    pid.append(str(i["pid"]))  
                    name.append(str(i["name"]))
                    memory_percent.append(str(i["memory_percent"]))
                    cpu_percent.append(str(i["cpu_percent"])) 
                count = count + 1
            dict_task = {
                "task status pid":pid,
                "task status name":name,
                "task status cpu percent":cpu_percent,
                "task status memory percent":memory_percent
            }
            dict_task_status_name = {
                "name":name
            }
            dict_task_status_cpu_percent = {
                "cpu percent":cpu_percent
            }
            dict_task_status_memory_percent = {
                "memory percent":memory_percent
            }
            dict_task = json.dumps(dict_task)
            computer.running_processes = dict_task
            db.session.add(computer)
            db.session.commit()
        if name == "CPU usage procentage":
            computer.cpu_usage_procentage = item
            db.session.add(computer)
            db.session.commit()
        if name == "Memory usage procentage":
            computer.memory_usage_procentage = item
            db.session.add(computer)
            db.session.commit()
    #db.session.add(new_computer)
    #db.session.commit()
    #print(Todo.query.filter(Todo.id).all())
    #print(Todo.query.filter(Todo.id).all()[0].mac_address)
    #print(Todo.query.filter(Todo.id).all()[0].cpu_usage_procentage)
    #print(Todo.query.filter(Todo.id).all()[0].memory_usage_procentage)
    #print(Todo.query.filter(Todo.id).all()[0].running_processes)
    #print(computer.mac_address)
    url = '/computers/' + str(id)
    return "Something" # if I want to send somethign to the client while he sends me all the data (after the client has the id ofcurse)
    #return render_template('get_json.html', json_request = js)
@app.route("/computers/<int:id>/ajax-dir", methods=["POST", "GET"])
def get_ajax_data(id):
    if request.method == "POST":
        computer = Todo.query.get_or_404(id)
        #redis_server = redis.Redis("localhost",charset="utf-8", decode_responses=True)
        
        redis_response_name = "directory response" + str(id)
        redis_request_name = "directory request" + str(id)
        redis_request_save_name = "directory name" + str(id)
        redis_server.delete(redis_response_name)
        redis_server.delete(redis_request_name)
        redis_server.delete(redis_request_save_name)
        redis_server.delete("download" + str(id))
        """
        computer.directory_response = ""
        db.session.add(computer)
        db.session.commit() 
        computer.directory_request = ""
        db.session.add(computer)
        db.session.commit()
        """
        params = request.form
        print("Pa: ", end="")
        print(params)
        try:
            print("Req recived!")
            print(type(params["DirVals"]))
            redis_server.set(redis_request_name, params["DirVals"])
            redis_server.set(redis_request_save_name, params["DirVals"])
            #computer.directory_request = params["DirVals"]
            #db.session.add(computer)
            #db.session.commit()
            print(redis_server.get(redis_request_name))
            print(redis_server.get(redis_request_save_name))
        except:
            pass
        if redis_server.get(redis_request_name) == "":
            print("None")
            return "None!"
        else:
            start_req = datetime.datetime.now()
            print("res name: ")
            print(redis_server.get(redis_response_name))
            # check in the while loop if when you click on the button there is an existing value
            get_redis_response = redis_server.lrange(redis_response_name,0, -1)
            """
            while(computer.directory_response == ""):
                computer2 = Todo.query.get(id)
                if computer2.directory_response != "":  
                    break
                else:
                    pass
            """
            print("redis_server: ", end=" ")
            print(redis_server.get(redis_response_name))
            try:
                while(redis_server.get(redis_response_name) is None):
                    waiting_for_res = datetime.datetime.now()
                    if(waiting_for_res - start_req > datetime.timedelta(seconds= 5.2)):
                        return {"dir items": ["Not Found"]}
            except:
                while(len(get_redis_response) == 0):
                    waiting_for_res = datetime.datetime.now()
                    if(waiting_for_res - start_req > datetime.timedelta(seconds= 5.2)):
                        return {"dir items": ["Not Found"]}
                    get_redis_response = redis_server.lrange(redis_response_name,0, -1)
            print("finished!")
            print("af: ", end="")
            get_redis_response = redis_server.lrange(redis_response_name,0, -1)
            temp_dict_val = get_redis_response
            print(redis_server.get(redis_request_name))
            print(get_redis_response)
            """
            computer.directory_response = ""
            db.session.add(computer)
            db.session.commit() 
            computer.directory_request = ""
            db.session.add(computer)
            db.session.commit()
            """
            redis_server.delete(redis_response_name)
            redis_server.delete(redis_request_name)
            print("end: ", end="")
            return {"dir items": temp_dict_val}


@app.route("/computers/<int:id>/get-dir", methods=['POST', 'GET'])
def get_dir_files(id):
    dir_location = ""
    computer = Todo.query.get_or_404(id)
    print(id)
    #redis_server = redis.Redis("localhost",charset="utf-8", decode_responses=True)
    
    """ delete file
    file_to_delete = redis_server.get("delete file" + str(id))
    if file_to_delete is not None and file_to_delete != "":
        try:
            print("Not empty!")
            os.remove(file_to_delete)
        except:
            pass
    """
    """ file delete using S3
    file_to_delete = redis_server.get("delete file" + str(id))
    if file_to_delete is not None and file_to_delete != "":
        print(file_to_delete)
        s3 = boto3.resource('s3',aws_access_key_id="AKIA5GAERK2YCVL7RNZ5", aws_secret_access_key= "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")
        try:
            s3.Object(BUCKET, file_to_delete).delete()
        except:
            pass
    """
    if request.method == "POST":
        print("get-dir req recived!", end="")
        request_redis = redis_server.get("directory request" + str(id))
        if request_redis is not None:
            if computer.id == id and request_redis != "":
                print("I found:" + request_redis)
                return request_redis
            else:
                print("err12")
                return "Not found"
        else:
            return "Not found"
    else:
        try:
            jq = request.get_json()
            dir_items = jq["dir list"]
            response_redis_name = "directory response" + str(id)
            redis_server.rpush(response_redis_name, *dir_items)
            print(jq["dir list"])
            #computer.directory_response = jq["dir list"]
            #db.session.add(computer)
            #db.session.commit()
            get_redis_response = redis_server.lrange(response_redis_name,0, -1)
            return ""
        except:
            print("Inncrort request")
            return "Not found"
 
@app.route("/computers/<int:id>/upload-file/<name>", methods=['POST', 'GET'])
def upload_file(name, id):
    if request.method == "GET":
        computer = Todo.query.get_or_404(id)
        print("in!")
        #redis_server = redis.Redis("localhost",charset="utf-8", decode_responses=True)
        
        redis_server.delete("download" + str(id))
        print(redis_server.get("directory name" + str(id)))
        requested_dir = redis_server.get("directory name" + str(id))
        if requested_dir != None:
            full_url = requested_dir + "\\" + name
            redis_server.set("download" + str(id), full_url)
            print(full_url)
            download = redis_server.get("download" + str(id))
            download = str(download)
            redirct_to = "/computer/" + str(id) + "/get-name"
            actual_name = name.split(".")[0]
            file_type = name.split(".")[-1]
            name = actual_name + "2" + "." + file_type
            print("name:::: " + name)
            redis_server.set("file-name" + str(id), name)
            return render_template("upload-file.html", computer = computer)
            #s3 = boto3.client('s3',aws_access_key_id="AKIA5GAERK2YCVL7RNZ5", aws_secret_access_key= "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")
            #not_found = True
            #return send_file(path, as_attachment=True)
        else:
            return ""
        
@app.route("/computers/<int:id>/get-name")
def send_name(id):
    #redis_server = redis.Redis("localhost",charset="utf-8", decode_responses=True)
    
    name = redis_server.get("download" + str(id))
    print(name)
    print("in get-name")
    if name is not None:
        return_name = name
        return name
    else:
        return ""

@app.route("/computers/<int:id>/file-ready", methods=['POST', "GET"])
def check_if_the_file_is_ready(id):
    print("recv")
    s3 = boto3.client('s3',aws_access_key_id="AKIA5GAERK2YCVL7RNZ5", aws_secret_access_key= "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")
    #redis_server = redis.Redis("localhost",charset="utf-8", decode_responses=True)
    
    name = redis_server.get("file-name" + str(id))
    print(name)
    if name != None and name != "None":
        try:
            s3.head_object(Bucket=BUCKET, Key=name)
            redis_server.set("delete file" + str(id), name)
            print("Pending?")
            print(name)
            file_download = s3.get_object(Bucket=BUCKET, Key=name)
            if request.method == "GET":
                redis_server.delete("file-name" + str(id))
                print("Get recived!")
                print(name)
                return Response(file_download["Body"].read(), headers={"Content-Disposition": "attachment;filename=" + name})
            else:
                return "Ready"
        except:
            return ""
    else:
        return ""

@app.route("/computers/<int:id>/write-file")
def write_file_to_server(id):
    #redis_server = redis.Redis("localhost",charset="utf-8", decode_responses=True)
    
    file_to_put = request.get_data()
    #file-download-storage
    if file_to_put != b"":
        s3 = boto3.resource('s3',aws_access_key_id="AKIA5GAERK2YCVL7RNZ5", aws_secret_access_key= "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")
        name = redis_server.get("download" + str(id))
        try:
            file_name = name.split("\\")[-1]
        except:
            return ""
        file_type = file_name.split(".")[-1]
        file_name = file_name.split(".")[0]
        file_name = file_name + "2"
        print("file name :L " + file_name)
        file_full_name = file_name + '.' + file_type
        #with open(file_full_name, "wb") as some_file:
        #    some_file.write(file_to_put)
        #s3.Object(BUCKET, file_full_name).put(Body=file_to_put)
        
        #file_to_put = binascii.b2a_base64(file_to_put)
        #file_to_put = list(file_to_put)
        #file_to_download = "downloadable" + str(id)
        #redis_server.delete(file_to_download)
        #redis_server.rpush(file_to_download, *file_to_put)

        """
        s3 = boto3.resource('s3',aws_access_key_id="AKIA5GAERK2YCVL7RNZ5", aws_secret_access_key= "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")
        s3.Object(BUCKET, file_full_name).put(Body=file_to_put)
        redis_server.delete("download" + str(id))
        """
        file_to_put = binascii.b2a_base64(file_to_put)
        file_to_put = file_to_put.decode()
        print("About to enter the background task!")
        redis_server.delete("download" + str(id))
        write_file_aws.delay(str(file_full_name), file_to_put)
        print("sent")
        return ""
    else:
        return ""


#celery background write file
@celery.task(name="write_file_to_aws")
def write_file_aws(file_full_name, file_to_put):
    #redis_server = redis.Redis("localhost",charset="utf-8", decode_responses=True)
    
    #list_downloadable = "downloadable" + str(id)
    #file_to_download = redis_server.lrange(list_downloadable,0, -1)
    #for i in range(0, len(file_to_download)): 
    #    file_to_download[i] = int(file_to_download[i]) 
    file_to_put = binascii.a2b_base64(file_to_put)
    s3 = boto3.resource('s3',aws_access_key_id="AKIA5GAERK2YCVL7RNZ5", aws_secret_access_key= "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")
    print("SEnding!")
    s3.Object(BUCKET, file_full_name).put(Body=file_to_put)
    return "Request sent!"



@app.route('/computers/<int:id>', methods=['POST', 'GET'])
def no_one_in_db(id):
    if len(Todo.query.all()) >= 0:
        if request.method == "POST":
            return no_one_in_db_code(id)
        else:
            if current_user.is_authenticated:
                #redis_server = redis.Redis("localhost",charset="utf-8", decode_responses=True)
                computer = Todo.query.get_or_404(id)
                if computer is not None:
                    redis_response_name = "directory response" + str(id)
                    redis_request_name = "directory request" + str(id)

                    redis_server.delete(redis_response_name)
                    redis_server.delete(redis_request_name)
                    redis_server.delete("download" + str(id))
                    computer = Todo.query.get_or_404(id)
                    running_processes = computer.running_processes
                    running_processes = json.loads(running_processes)
                    pid = running_processes["task status pid"]
                    name = running_processes["task status name"]
                    cpu_percent = running_processes["task status cpu percent"]
                    memory_percent = running_processes["task status memory percent"]
                    computer = Todo.query.get_or_404(id)
                    all_computers = []
                    for i in range(0, len(Todo.query.all())):
                        all_computers.append(Todo.query.all()[i].id)
                    if current_user.level == 1:
                        if current_user.computer_id == id:
                            return render_template('show_computer_data.html', computer=computer, timer=5000, pid=pid, name=name, cpu_percent=cpu_percent, memory_percent=memory_percent, zip=itertools.zip_longest ,level_nev = int(current_user.level), computer_list_nev=all_computers) # if I want to send somethign to the client while he sends me all the data (after the client has the id ofcurse)
                    
                        else:
                            return abort(404)
                    elif current_user.level == 2:
                        if current_user.computer_id == id:
                            return render_template('show_computer_data.html', computer=computer, timer=5000, pid=pid, name=name, cpu_percent=cpu_percent, memory_percent=memory_percent, zip=itertools.zip_longest, level_nev = int(current_user.level), computer_list_nev=all_computers) # if I want to send somethign to the client while he sends me all the data (after the client has the id ofcurse)
                    
                        try:
                            allow_to_acces = current_user.allow_to_view_level_2.split(',')
                        except:
                            allow_to_acces = current_user.allow_to_view_level_2
                        if len(allow_to_acces) == 1:
                            print("Abort!")
                            if allow_to_acces[0] == "None":
                                return abort(404)
                            elif int(allow_to_acces[0]) == id:
                                return render_template('show_computer_data.html', computer=computer, timer=5000, pid=pid, name=name, cpu_percent=cpu_percent, memory_percent=memory_percent, zip=itertools.zip_longest, level_nev = int(current_user.level), computer_list_nev=all_computers) # if I want to send somethign to the client while he sends me all the data (after the client has the id ofcurse)
                    
                        else:
                            for i in allow_to_acces:
                                i = int(i)
                                if i == id:
                                    return render_template('show_computer_data.html', computer=computer, timer=5000, pid=pid, name=name, cpu_percent=cpu_percent, memory_percent=memory_percent, zip=itertools.zip_longest, level_nev = int(current_user.level), computer_list_nev=all_computers) # if I want to send somethign to the client while he sends me all the data (after the client has the id ofcurse)
                    
                    elif current_user.level == 3:
                        return render_template('show_computer_data.html', computer=computer, timer=5000, pid=pid, name=name, cpu_percent=cpu_percent, memory_percent=memory_percent, zip=itertools.zip_longest, level_nev = int(current_user.level), computer_list_nev=all_computers) # if I want to send somethign to the client while he sends me all the data (after the client has the id ofcurse)
                else:
                    return redirect("/")
            else:
                return redirect("/login")

            


@app.route('/computers/add')
def new_computer():
    try:
        new_id = len(Todo.query.all()) + 1
    except:
        new_id = 1
    print(new_mac_address)
    print(new_id)
    new_user = Todo(mac_address=new_mac_address, id=new_id)
    db.session.add(new_user)
    db.session.commit()
    return redirect('/computers/verify_login', code=307)

@app.route('/computers/<int:id>/live', methods=['POST', 'GET'])
def live_info(id):
    computer = Todo.query.get_or_404(id)
    if request.method == 'POST':
        f = request.get_data
        js = request.get_json()
        if js is not None:
            for name, item in js.items():
                if name == "running processes":
                    new_item = ""
                    count = 0
                    for i in item:
                        if count == 0:
                            continue
                        new_item = new_item + " name: " + str(i["name"]) + " memory_percent: " + str(i["memory_percent"]) + " cpu_percent: " + str(i["cpu_percent"]) 
                        count = count + 1
                    computer.running_processes = new_item
                    db.session.add(computer)
                    db.session.commit()
                if name == "CPU usage procentage":
                    computer.cpu_usage_procentage = item
                    db.session.add(computer)
                    db.session.commit()
                if name == "Memory usage procentage":
                    computer.memory_usage_procentage = item
                    db.session.add(computer)
                    db.session.commit()
        else:
            json_txt = {"CPU usage procentage" : computer.cpu_usage_procentage, "running processes" : computer.running_processes, "Memory usage procentage": computer.memory_usage_procentage}
            return json_txt
    else:
        running_processes = computer.running_processes
        running_processes = json.loads(running_processes)
        pid = running_processes["task status pid"]
        name = running_processes["task status name"]
        cpu_percent = running_processes["task status cpu percent"]
        memory_percent = running_processes["task status memory percent"]
        json_txt = {"CPU usage procentage" : computer.cpu_usage_procentage, "Memory usage procentage": computer.memory_usage_procentage, "pid":pid, "name":name, "cpu_percent":cpu_percent,"memory_percent":memory_percent}
        
        return json_txt
        # return render_template("damn.html", jso= json.dumps(json_txt) , timer=5000), 200, {'Content-Type': 'Content-Type: application/javascript; charset=utf-8'}



def get_admin_panel_data():
    users_username = []
    computer_client_id = []
    computers_mac = []
    assigned_values = []
    levels = []
    assigned_level_2_allowed_to_view = []
    for i in range(0,len(users.query.all())):
        users_username.append(users.query.all()[i].username)
        levels.append(users.query.all()[i].level)
        if users.query.all()[i].level == 2:
            assigned_level_2_allowed_to_view.append(users.query.all()[i].allow_to_view_level_2)
        else:
            assigned_level_2_allowed_to_view.append("None")
        if users.query.all()[i].computer_id == -1:
            assigned_values.append("None")
        else:
            assigned_values.append(users.query.all()[i].computer_id)
    for i in range(0, len(Todo.query.all())):
        computer_client_id.append(Todo.query.all()[i].id)
        computers_mac.append(Todo.query.all()[i].mac_address)
    return users_username, computer_client_id, assigned_values, levels, assigned_level_2_allowed_to_view

@app.route("/admin-panel", methods=['GET', 'POST'])
@login_required
def admin_panel():
    if request.method == "POST":
        return redirect("/admin-panel/data", code=307)
    if request.method == 'GET':
        if current_user.level == 3:
            users_username, computer_client_id, assigned_values, levels, assigned_level_2_allowed_to_view = get_admin_panel_data()
            return render_template("admin_panel.html", users_username = users_username, computer_client_id=computer_client_id, assigned_values=assigned_values, levels=levels,assigned_level_2_allowed_to_view=assigned_level_2_allowed_to_view, computer_list_nev =computer_client_id, level_nev = int(current_user.level),zip=itertools.zip_longest)
        else:
            return redirect('/')



def level_2_handle(remove_vals, user,level):
    count = 0
    if level == 2:
        if remove_vals[0] == "None":
            print("Allowed to view: " + "None")
            users.query.filter_by(username = user).update(dict(allow_to_view_level_2 = "None"))
            db.session.add(users)
            db.session.commit()
        try:
            print("trying level 2")
            allow_to_view = ""
            for i in remove_vals:
                count = count + 1
                i = int(i) # checking if it only contains digits
                i = str(i)
                if count != len(remove_vals):
                    allow_to_view = allow_to_view + i + ","
                else:
                    allow_to_view = allow_to_view + i
            print("Allowed to view: " + allow_to_view)
            users.query.filter_by(username = user).update(dict(allow_to_view_level_2 = allow_to_view))
            db.session.add(users)
            db.session.commit()
        except:
            print("err level 2")
            return "None"
    else:
        print("err2")
        return "None"


@app.route("/admin-panel/data", methods=['POST'])
@login_required
def admin_data():
    if request.method == "POST":
        try:
            assign_value = -1
            user = ""
            remove_vals = []
            print(request.get_data())
            data = request.get_data().decode()
            try:
                remove_vals = data.split('&')[2]
            except:
                remove_vals = "None"
            try:
                user = data.split("=")[0]
                assign_value = data.split("=")[1]
                assign_value = assign_value.split("&")[0]
                level = data.split('&')[1]
            except:
                return {"Values" : "failed"}
            print(user)
            print(assign_value)
            print(level)
            print(remove_vals)
            if assign_value == "None":
                assign_value = -1
            try:
                assign_value = int(assign_value)
                user = str(user)
                level = int(level)
            except:
                return {"Values" : "failed"}
            user_found = False
            username_pos = -1
            for i in range(0,len(users.query.all())):
                if user ==  users.query.all()[i].username:
                    username_pos = i
            if assign_value != -1:
                for j in range(0,len(users.query.all())):
                    print("user: ", end="")
                    print(users.query.all()[j].username)
                    if user == users.query.all()[j].username:
                        user_found = True
                        print("found")
                    if assign_value == users.query.all()[j].computer_id and j != username_pos:
                        print("Failed")
                        return {"Values" : "failed"}
            if (user_found == False and assign_value != -1) or level > 3:
                print("the err2 ")
                return {"Values" : "failed"}
            print("passed!")
            users.query.filter_by(username = user).update(dict(computer_id = assign_value, level=level, allow_to_view_level_2= remove_vals))
            db.session.commit()
            print("almost there")
            if assign_value == -1:
                assign_value = "None"
            #level_2_handle(remove_vals,user,level)
            return {"computer id" : assign_value, "computer level": level, "level 2" : remove_vals}
        except:
            print("the err")
            return {"Values" : "failed"}

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')
@app.route('/')
@login_required
def index():
    all_computers = []
    for i in range(0, len(Todo.query.all())):
        all_computers.append(Todo.query.all()[i].id)
    return render_template('index.html', user=current_user.username,level =int(current_user.level) ,level_nev = int(current_user.level), computer_list_nev=all_computers)

# err handles
@app.errorhandler(401) 
def invalid_route(somearg): 
    return redirect('/login')
@app.errorhandler(404)
def not_found_route(somearg):
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)