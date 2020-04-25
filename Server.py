from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user
import requests
import json
import itertools 

new_id = -1
new_mac_address = ""
change = 5000
js = ""


def main():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users160.db'
    app.config['SECRET_KEY'] = "thisistopsecret"
    db = SQLAlchemy(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    class Todo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        mac_address = db.Column(db.TEXT)
        cpu_type = db.Column(db.TEXT)
        ram_usage = db.Column(db.FLOAT)
        running_processes = db.Column(db.TEXT)
        cpu_usage_procentage = db.Column(db.FLOAT)
        memory_usage_procentage = db.Column(db.FLOAT)
    class users(db.Model, UserMixin):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.TEXT, unique=True)
        password = db.Column(db.TEXT)
        email = db.Column(db.TEXT)
        level = db.Column(db.INTEGER) #level 1 - regular employee, level 2 - Team leader, level 3 - Manager
    db.create_all()
    


    @login_manager.user_loader
    def load_user(user_id):
        return users.query.get(int(user_id))

    @app.route('/login', methods=['POST', 'GET'])
    def login():
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            user_exists = bool(users.query.filter_by(username=username,password=password).first())
            print(user_exists)
            if user_exists:
                user = users.query.filter_by(username=username,password=password)
                login_user(user)
                return "valid"
            else:
                print("invalid")
                return "Not valid"
        if request.method == "GET":
            return render_template('/login.html')



    #verify_login
    @app.route('/computers/verify_login', methods=['POST', 'GET'])
    def check_if_user_exists():
        if request.method == 'POST':
            global new_mac_address
            js = request.get_json()
            print(js)
            if js is not None:
                for mac_address in js.values():
                    for i in range(len(Todo.query.all())):
                        if mac_address == Todo.query.filter(Todo.id).all()[i].mac_address:
                            print("True!")
                            return str(Todo.query.filter(Todo.id).all()[i].id)
                    new_mac_address = mac_address
                    print("Not found!")
                    return redirect('/computers/add')
            else:
                print("Empty? wtf")
        else:   
            return ""

    if len(Todo.query.all()) >= 0:
        @app.route('/computers/<int:id>', methods=['POST', 'GET'])
        def no_one_in_db(id):
            global js
            computer = Todo.query.get_or_404(id)
            if request.method == 'POST':
                js = request.get_json()
                for name, item in js.items():
                    if name == "CPU type:":
                        computer.cpu_type = item
                        db.session.commit()
                    if name == "Ram usage: ":
                        computer.ram_usage = item
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
                        db.session.commit()
                    if name == "CPU usage procentage":
                        computer.cpu_usage_procentage = item
                        db.session.commit()
                    if name == "Memory usage procentage":
                        computer.memory_usage_procentage = item
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
                return "" # if I want to send somethign to the client while he sends me all the data (after the client has the id ofcurse)
                #return render_template('get_json.html', json_request = js)
            else:
                running_processes = computer.running_processes
                running_processes = json.loads(running_processes)
                pid = running_processes["task status pid"]
                name = running_processes["task status name"]
                cpu_percent = running_processes["task status cpu percent"]
                memory_percent = running_processes["task status memory percent"]
                print(pid)
                return render_template('show_computer_data.html', computer=computer, timer=5000, pid=pid, name=name, cpu_percent=cpu_percent, memory_percent=memory_percent, zip=itertools.zip_longest) # if I want to send somethign to the client while he sends me all the data (after the client has the id ofcurse)
                
                
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
                        db.session.commit()
                    if name == "CPU usage procentage":
                        computer.cpu_usage_procentage = item
                        db.session.commit()
                    if name == "Memory usage procentage":
                        computer.memory_usage_procentage = item
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
    @app.route('/computers')
    def show_all_computers():
        print(len(Todo.query.all()))
        all_computers_on_the_server = []
        for i in range(len(Todo.query.all())):
            all_computers_on_the_server.append(Todo.query.all()[i].id)
        print(all_computers_on_the_server)
        return render_template('show_all_computers.html', computer_list =all_computers_on_the_server)
    @app.route('/')
    def index():
        return render_template('index.html')
    app.run(debug=True,host='192.168.1.181')
    
if __name__ == "__main__":
    main()