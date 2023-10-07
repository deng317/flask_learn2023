# encoding:utf-8
from web_server import db, login_manager, app
from itsdangerous import TimedSerializer, BadTimeSignature, BadData, URLSafeTimedSerializer
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    image_file = db.Column(db.String(50), nullable=False, default='default.jpg')
    password = db.Column(db.String(50), nullable=False)

    # 设定relationship, 这里的Post是类的名称，因为一个User可以有多个Post
    posts = db.relationship("Post", backref="author", lazy=True)

    def generate_reset_token(self):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='auth')
        token = s.dumps({'user_id': self.id, 'username': self.username})
        return token

    @staticmethod
    def validate_token(token):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'], salt='auth')
        try:
            user_id = s.loads(token,max_age=600)['user_id']
            return User.query.get(user_id)
        except BadTimeSignature:
            return None
        except BadData:
            return None


    # debug使用以下__repr__
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    post_time = db.Column(db.DateTime, nullable=False, default=datetime.now)
    content = db.Column(db.Text, nullable=False)

    # 设定Relationship,这里的user是小写，因为一个post的author是一个人
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post(title'{self.title}',post_time '{self.post_time}', content'{self.content[:20]}')"
