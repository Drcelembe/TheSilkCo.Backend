# manage.py
from app import create_app
from extensions import db
from flask_migrate import MigrateCommand
import click
from flask.cli import with_appcontext
from flask import current_app

app = create_app()

@app.cli.command("show-config")
@with_appcontext
def show_config():
    print("DATABASE_URL:", current_app.config.get("SQLALCHEMY_DATABASE_URI"))
