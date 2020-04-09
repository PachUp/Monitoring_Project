from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

item_counter = 0


def main():
    app = Flask(__name__)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users76.db'
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
            js = request.get_json()
            print(js)
            if js is not None:
                for mac_address in js.values():
                    for i in range(len(Todo.query.all())):
                        if mac_address == Todo.query.filter(Todo.id).all()[i].mac_address:
                            print("True!")
                            return str(Todo.query.filter(Todo.id).all()[i].id)
                        else:
                            print("Not found!")
        else:
            return ""

    if len(Todo.query.all()) == 0:
        new_computer = Todo() #new user caswe
        @app.route('/computers/0', methods=['POST', 'GET'])
        def no_one_in_db():
            global item_counter
            if request.method == 'POST':
                js = request.get_json()
                for item in js.values(): #new user case
                    if item_counter == 0:
                        new_computer.mac_address = item
                    if item_counter == 1:
                        new_computer.cpu_type = item
                    if item_counter == 2:
                        new_computer.ram_usage = item
                    if item_counter == 3:
                        new_computer.running_processes = item
                    if item_counter == 4:
                        new_computer.cpu_usage_procentage = item
                    if item_counter == 5:
                        new_computer.memory_usage_procentage = item
                        item_counter = 2
                    item_counter = item_counter + 1
                db.session.add(new_computer)
                db.session.commit()
                print(Todo.query.filter(Todo.id).all())
                print(Todo.query.filter(Todo.id).all()[0].mac_address)
                print(Todo.query.filter(Todo.id).all()[0].cpu_usage_procentage)
                print(Todo.query.filter(Todo.id).all()[0].memory_usage_procentage)
                print(Todo.query.filter(Todo.id).all()[0].running_processes)
                return redirect('/')
            else:
                try:
                    return str(Todo.query.filter(Todo.id).all()[0].cpu_usage_procentage)
                except:
                    return ""

    @app.route('/')
    def index():
        return "Hello world!"

    app.run(debug=True)


if __name__ == "__main__":
    main()