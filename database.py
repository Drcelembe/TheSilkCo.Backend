from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from extensions import db
from extensions import db, migrate


db = SQLAlchemy()
migrate = Migrate()
# database.py
# Single source of truth for db object used by models.


# Provide a tiny helper to attach app when needed (avoid circular import)
def init_db(app):
    db.init_app(app)
