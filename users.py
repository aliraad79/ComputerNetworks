from dataclasses import dataclass, field
import hashlib
from typing import List


def _hash(username: str, password: str):
    return hashlib.sha256(str(username + password).encode()).hexdigest()


@dataclass
class User:
    username: str
    password: str
    type: bool = field(default=0)
    is_Logged_in: bool = field(default=False)
    is_striked: bool = field(default=False)
    is_approved: bool = field(default=False)
    id: str = field(default=False)

    @classmethod
    def login_user(cls, username, password):
        for user in users:
            if user.id == _hash(username, password):
                user.is_Logged_in = True
                return user
        return None

    @classmethod
    def signup_user(cls, username, password, user_type):
        return cls(
            username,
            password,
            user_type,
            id=_hash(username, password),
            is_approved=user_type == 1,
        )

    @classmethod
    def get_user(cls, token):
        for i in users:
            if i.id == token:
                return i
        return None

    @classmethod
    def get_user_by_username(cls, username):
        for i in users:
            if i.username == username:
                return i
        return None

    def __eq__(self, __o: object) -> bool:
        return self.id == __o.id


def login_user(username: str, password: str) -> User:
    return User.login_user(username, password)


def signup_user(username: str, password: str, user_type: int) -> User:
    for user in users:
        if user.id == _hash(username, password):
            return user
        elif user.username == username:
            return None
    new_user = User.signup_user(username, password, user_type)
    new_user.is_Logged_in = True
    users.append(new_user)
    return new_user


def logout_user(user_id: str):
    for i in users:
        if i.id == user_id:
            i.is_Logged_in = False
            return True
    return False


def create_manager_account(username, password):
    new_user = User.signup_user(username, password, 3)
    users.append(new_user)
    return new_user


def is_user_loggeed_in(token):
    user = User.get_user(token)
    if user and user.is_Logged_in:
        return user
    return None


def is_user_admin_or_manager(token):
    user = User.get_user(token)
    if user and user.type in [2, 3]:
        return user
    return None


users: List[User] = []
