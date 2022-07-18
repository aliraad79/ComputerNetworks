from dataclasses import dataclass, field
from typing import List


@dataclass
class User:
    username: str
    password: str
    type: bool = field(init=False)
    is_Logged_in: bool = field(init=False)

    @classmethod
    def login_user(cls, username, password):
        return cls(username, password)

    @classmethod
    def signup_user(cls, username, password, user_type):
        return cls(username, password, user_type)


users: List[User] = []


def authenticate_user(username: str, password: str) -> User:
    return User.login_user(username, password)


def signup_user(username: str, password: str, user_type: int) -> User:
    new_user = User.signup_user(username, password, user_type)
    users.append(new_user)
    return new_user


def logout_user(username: str) -> User:
    user = find_user(username)
    user.is_Logged_in = True
    return user


def find_user(username: str):
    for i in users:
        if i.username == username:
            return i
