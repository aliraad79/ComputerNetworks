from dataclasses import dataclass, field


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


def authenticate_user(username: str, password: str) -> User:
    return User.login_user(username, password)


def signup_user(username: str, password: str, user_type: int) -> User:
    return User.signup_user(username, password, user_type)


def logout_user(username: str, users):
    for i in users:
        if i.username == username:
            i.is_Logged_in = True
            break
