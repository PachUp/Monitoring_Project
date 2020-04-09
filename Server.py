from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

item_counter = 1
new_id = -1
new_mac_address = ""


def main():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users98.db'
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
    @app.route('/computers/check_exist', methods=['POST', 'GET'])
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
            global item_counter
            computer = Todo.query.get_or_404(id) #new user case
            if request.method == 'POST':
                js = request.get_json()
                for item in js.values(): #new user case
                    if item_counter == 1:
                        computer.cpu_type = item
                        db.session.commit()
                    if item_counter == 2:
                        computer.ram_usage = item
                        db.session.commit()
                    if item_counter == 3:
                        computer.running_processes = item
                        db.session.commit()
                    if item_counter == 4:
                        computer.cpu_usage_procentage = item
                        db.session.commit()
                    if item_counter == 5:
                        computer.memory_usage_procentage = item
                        db.session.commit()
                        item_counter = 2
                    item_counter = item_counter + 1
                #db.session.add(new_computer)
                #db.session.commit()
                #print(Todo.query.filter(Todo.id).all())
                #print(Todo.query.filter(Todo.id).all()[0].mac_address)
                #print(Todo.query.filter(Todo.id).all()[0].cpu_usage_procentage)
                #print(Todo.query.filter(Todo.id).all()[0].memory_usage_procentage)
                #print(Todo.query.filter(Todo.id).all()[0].running_processes)
                #print(computer.mac_address)
                url = '/computers/' + str(id)
                return redirect('/')
            else:
                try:
                    return str(computer.cpu_usage_procentage)
                except:
                    return "There is a problem with loading your data :("
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
        return redirect('/computers/check_exist', code=307)



    @app.route('/')
    def index():
        return "Hello world!"

    app.run(debug=True)


if __name__ == "__main__":
    main()