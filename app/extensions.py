"""
Shared extension instances, created here (not in __init__.py) so that
models.py and routes can import them without circular-import issues.
"""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message = "ამ გვერდზე წვდომისთვის გაიარეთ ავტორიზაცია."
login_manager.login_message_category = "warning"
