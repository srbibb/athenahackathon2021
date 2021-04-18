from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    points = db.Column(db.Integer, default=0)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    action = db.Column(db.String(64))
    item = db.Column(db.String(64))
    timestamp = db.Column(db.String, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    points = db.Column(db.Integer,default=0)

    def __repr__(self):
        return '<Post {}>'.format(self.body)

    def calculate_points(self):
        actions = {'donated':20,'recycled':1,'upcycled':15,'reused':3,'purchased second hand':20,'have something else to share':0}
        self.points = actions[self.action]

