from flask import session
from flask_login import UserMixin, login_user

from src.common import utils
from src.common.database import Database
import uuid
import datetime
from src.common.utils import Utils
from src.models.blog import Blog


class User(UserMixin):
    def __init__(self, email, password, username, _id=None):
        self.email = email
        self.password = password
        self.username = username
        self._id = uuid.uuid4().hex if _id is None else _id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id

    def user_login(self):
        login_user(self)

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("users", {"email": email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_username(cls, username):
        data = Database.find_one("users", {"username": username})
        if data is not None:
            return cls(**data)

    @staticmethod
    def login_valid(email, password):
        verify_user = User.get_by_email(email)
        if verify_user is not None:
            return Utils.check_hashed_password(password, verify_user.password)
        return False

    @classmethod
    def register(cls, email, password, username):
        new_user = cls(email, password, username)
        new_user.save_to_mongo()
        session['email'] = email
        return True


    @staticmethod
    def login(user_email):
        session['email'] = user_email

    @staticmethod
    def logout():
        session['email'] = None

    def get_blogs(self):
        return Blog.find_by_author_id(self._id)

    def new_blog(self, title, description):
        blog = Blog(author=self.email,
                    title=title,
                    description=description,
                    author_id = self._id)

        blog.save_to_mongo()

    @staticmethod
    def new_post(blog_id, title, content, date=datetime.datetime.utcnow()):
        blog = Blog.from_mongo(blog_id)
        blog.new_post(title=title,
                      content=content,
                      date=date)

    def json(self):
        return {
            'email': self.email,
            'password': self.password,
            'username': self.username,
            '_id': self._id,
        }

    def save_to_mongo(self):
        Database.insert("users", self.json())
