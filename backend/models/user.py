from . import db
from sqlalchemy import func, Index
from datetime import datetime
import pytz

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    avatar = db.Column(db.String(500), nullable=True)
    github_id = db.Column(db.String(9), unique=True, nullable=True)
    discord_id = db.Column(db.String(18), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Warsaw')), nullable=False)
    books = db.relationship('BookCollection', backref='owner', lazy=True)
    wishlist = db.relationship('WishList', backref='owner', lazy=True)

    __table_args__ = (
        Index('ix_username_lower', func.lower(username), unique=True),
        Index('ix_email_lower', func.lower(email), unique=True),
    )