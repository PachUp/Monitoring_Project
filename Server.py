from flask import Flask
from flask_sqlalchemy import *


def main():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users1.db'
    db = SQLAlchemy(app)
    class UserInfo(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        cpu_type = db.Column(db.TEXT)
        ram_usage = db.Column(db.FLOAT)
        mac_address = db.Column(db.TEXT)
        running_processes = db.Column(db.TEXT)
        cpu_usage_procentage = db.Column(db.FLOAT)
        memory_usage_procentage = db.Column(db.FLOAT)

    @app.route('/')
    def index():
        return "Hello world!"
    app.run(debug=True)


if __name__ == "__main__":
    main()