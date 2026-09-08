from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager

CATEGORIES = ["Music", "Tech", "Art", "Sport", "Education", "Other"]

CATEGORY_LABELS = {
    "Music": "მუსიკა",
    "Tech": "ტექნოლოგიები",
    "Art": "ხელოვნება",
    "Sport": "სპორტი",
    "Education": "განათლება",
    "Other": "სხვა",
}


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_pic = db.Column(db.String(255), nullable=False, default="default.png")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    events = db.relationship(
        "Event", backref="author", lazy=True, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return f"<User {self.email}>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    short_description = db.Column(db.String(300), nullable=False)
    full_description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    ticket_price = db.Column(db.Float, nullable=False, default=0.0)
    organizer = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False, default="Other")

    posted_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Event {self.title!r}>"
