from flask_login import UserMixin
from enum import Enum


class User(UserMixin):
    def __init__(self, id, username, password, usertype):
        self.id = id
        self.username = username
        self.password = password
        self.usertype = usertype


class UserType(Enum):
    # Enum to represent user types, either student or teacher, for use in the application logic and database storage
    STUDENT = "student"
    TEACHER = "teacher"
