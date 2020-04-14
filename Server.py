from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import requests
import json

new_id = -1
new_mac_address = ""
change = 5000
js = ""


def main():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users126.db'
    db = SQLAlchemy(app)

    class Todo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        mac_address = db.Column(db.TEXT)
        cpu_type = db.Column(db.TEXT)
        ram_usage = db.Column(db.FLOAT)
        running_processes = db.Column(db.TEXT)
        cpu_usage_procentage = db.Column(db.FLOAT)
        memory_usage_procentage = db.Column(db.FLOAT)
    db.create_all()
    print(Todo.query.all() is None)
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
            return render_template('show_computer_data.html', computer=computer, timer=5000) # if I want to send somethign to the client while he sends me all the data (after the client has the id ofcurse)
                
            if request.method == 'POST':
                js = request.get_json()
                print(js)
                for name, item in js.items():
                    if name == "CPU type:":
                        computer.cpu_type = item
                        db.session.commit()
                    if name == "Ram usage: ":
                        computer.ram_usage = item
                        db.session.commit()
                    if name == "running processes":
                        c_item = item.split(',')
                        count = 0
                        new_item = ""
                        for i in c_item:
                            new_item = new_item + i + "," 
                            if count%5 == 0:
                                new_item = new_item + '\n'
                            count = count + 1
                        computer.running_processes = new_item
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
                print("POST!!!")
                return render_template('show_computer_data.html', computer=computer, timer=5000) # if I want to send somethign to the client while he sends me all the data (after the client has the id ofcurse)
                #return render_template('get_json.html', json_request = js)
                
            else:
                return render_template('show_computer_data.html', computer=computer, timer=5000) # if I want to send somethign to the client while he sends me all the data (after the client has the id ofcurse)
                
                
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
            print(request.get_data())
            f = request.get_data
            js = request.get_json()
            print(js)
            if js is not None:
                for name, item in js.items():
                    if name == "running processes":
                        c_item = item.split(',')
                        count = 0
                        new_item = ""
                        for i in c_item:
                            new_item = new_item + i + "," 
                            if count%5 == 0:
                                new_item = new_item + ' '
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

                cpu_usage_procentage = request.form["CPU usage procentage"]
                memory_usage_procentage = request.form["Memory usage procentage"]
                running_processes = request.form["running processes"]
                computer.running_processes = running_processes
                db.session.commit()
                computer.cpu_usage_procentage = cpu_usage_procentage
                db.session.commit()
                computer.memory_usage_procentage = memory_usage_procentage
                db.session.commit()
            json_txt = {"CPU usage procentage" : computer.cpu_usage_procentage, "running processes" : computer.running_processes, "Memory usage procentage": computer.memory_usage_procentage}
            print(computer.cpu_usage_procentage)
            return json_txt
        else:
            
            json_txt = {"CPU usage procentage" : computer.cpu_usage_procentage, "running processes" : computer.running_processes, "Memory usage procentage": computer.memory_usage_procentage}
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