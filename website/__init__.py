import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os

db = SQLAlchemy()
DB_NAME = "database.db"
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


def start_app():
    default = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.system("flake8")
    os.chdir(default)
    app.config['SECRET_KEY'] = 'CS480-Project'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_NAME
    db.init_app(app)
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    from .models import User
    create_database(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME) and not path.exists(
            os.path.dirname(os.path.abspath(__file__)) + "\\" + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')


@app.cli.command()
def scheduled():
    """Run Scheduled Job."""
    from .services import remove_inactive_schedules
    print("Removing inactive schedules...")
    remove_inactive_schedules()
    print("Done!")


@app.cli.command()
@click.option('--records')
def create_patients_data(records):
    num_new_data = 10
    if records is not None:
        num_new_data = int(records)
    from website.test.insert_test_data import insert_dummy_patient_data
    insert_dummy_patient_data(num_new_data)


@app.cli.command()
@click.option('--records')
def create_nurses_data(records):
    num_new_data = 10
    if records is not None:
        num_new_data = int(records)
    from website.test.insert_test_data import insert_dummy_nurse_data
    insert_dummy_nurse_data(num_new_data)
