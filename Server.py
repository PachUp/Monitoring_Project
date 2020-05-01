import requests
from flask_restful import Resource, Api
from flask import Flask, render_template, url_for, request, redirect, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
import json
import itertools 
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import psycopg2
new_id = -1
new_mac_address = ""
change = 5000
js = ""


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://dfrawwwpzamher:2290ce982f10bf8d567ed1fbee42765e550a6e84b9049c717feb8945477b38b7@ec2-54-228-251-117.eu-west-1.compute.amazonaws.com:5432/d3updufagirasd'
app.config['SECRET_KEY'] = "thisistopsecret"
db = SQLAlchemy(app)
admin = Admin(app,url="/admindb")
login_manager = LoginManager()
login_manager.init_app(app)
class Todo(db.Model):
    __tablename__ = "Todo"
    id = db.Column(db.Integer, primary_key=True)
    mac_address = db.Column(db.TEXT)
    cpu_type = db.Column(db.TEXT)
    ram_usage = db.Column(db.FLOAT)
    running_processes = db.Column(db.TEXT)
    cpu_usage_procentage = db.Column(db.FLOAT)
    memory_usage_procentage = db.Column(db.FLOAT)
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
        print(username)
        print(users.query.all())
        send = ""
        user_check = bool(users.query.filter_by(username=username).first())
        pass_check = bool(users.query.filter_by(password=password).first())
        if user_check and not pass_check:
            return "password"
        elif not user_check:
            return "username"
        else:
            user = users.query.filter_by(username=username,password=password).first()
            login_user(user)
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
        user_check = bool(users.query.filter_by(username=username).first())
        email_check = bool(users.query.filter_by(email=email).first())
        if email_check or "@gmail.com" not in email:
            return "email"
        elif user_check:
            return "username"
        else:
            if len(users.query.all()) == 0:
                new_user = users(username = username, password=password, email=email, level=3)
                db.session.add(new_user)
                db.session.commit()
            else:
                new_user = users(username = username, password=password, email=email, level=1)
                db.session.add(new_user)
                db.session.commit()
            return redirect('/')
    if request.method == "GET":
        if current_user.is_authenticated:
            return redirect('/')
        else:
            return render_template('/register.html')

#verify_login
@app.route('/computers/verify_login', methods=['POST', 'GET'])
def check_if_user_exists():
    if request.method == 'POST':
        global new_mac_address
        js = request.get_json()
        print(js)
        if js is not None:
            mac_address = js['mac_address']
            for i in range(0,len(Todo.query.all())):
                print(Todo.query.all()[i].id)
                print(Todo.query.filter_by(id = Todo.query.all()[i].id).all()[i].mac_address)
                if mac_address == Todo.query.filter_by(id = Todo.query.all()[i].id).all()[i].mac_address:
                    print("True!")
                    return str(Todo.query.filter_by(id = Todo.query.all()[i].id).all()[i].id)
            new_mac_address = mac_address
            print("Not found!")
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
    print("returnin'")
    return "Something" # if I want to send somethign to the client while he sends me all the data (after the client has the id ofcurse)
    #return render_template('get_json.html', json_request = js)

@app.route('/computers/<int:id>', methods=['POST', 'GET'])
def no_one_in_db(id):
    if len(Todo.query.all()) >= 0:
        if request.method == "POST":
            return no_one_in_db_code(id)
        else:
            if current_user.is_authenticated:
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
                        return render_template('show_computer_data.html', computer=computer, timer=5000, pid=pid, name=name, cpu_percent=cpu_percent, memory_percent=memory_percent, zip=itertools.zip_longest, level_nev = int(current_user.level), computer_list_nev=all_computers) # if I want to send somethign to the client while he sends me all the data (after the client has the id ofcurse)
                
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
            db.session.commit()
        try:
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
            db.session.commit()
        except:
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
                    if user == users.query.all()[j].username:
                        user_found = True
                        print("found")
                    if assign_value == users.query.all()[j].computer_id and j != username_pos:
                        print("Failed")
                        return {"Values" : "failed"}
            if (user_found == False and assign_value != -1) or level > 3:
                print("the err")
                return {"Values" : "failed"}
            if assign_value == -1:
                assign_value = "None"
            users.query.filter_by(username = user).update(dict(computer_id = assign_value, level=level))
            db.session.commit()
            return {"computer id" : assign_value, "computer level": level, "level 2" : remove_vals}
        except:
            print("the err")
            return {"Values" : "failed"}


@app.route('/computers')
def show_all_computers():
    print(len(Todo.query.all()))
    all_computers_on_the_server = []
    for i in range(len(Todo.query.all())):
        all_computers_on_the_server.append(Todo.query.all()[i].id)
    print(all_computers_on_the_server)
    return render_template('show_all_computers.html', computer_list_nev =all_computers_on_the_server, level_nev = int(current_user.level))
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
    return render_template('index.html', user=current_user.username,level = level ,level_nev = int(current_user.level), computer_list_nev=all_computers)

# err handles
@app.errorhandler(401) 
def invalid_route(somearg): 
    return redirect('/login')
@app.errorhandler(404)
def not_found_route(somearg):
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)