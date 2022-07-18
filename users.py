from dataclasses import dataclass, field
import hashlib


def _hash(username: str, password: str):
    return hashlib.sha256(str(username + password).encode()).hexdigest()


@dataclass
class User:
    username: str
    password: str
    type: bool = field(default=0)
    is_Logged_in: bool = field(default=False)
    id: str = field(default=False)

    @classmethod
    def login_user(cls, username, password, users):
        for user in users:
            if user.id == _hash(username, password):
                user.is_Logged_in = True
                return user
        return None

    @classmethod
    def signup_user(cls, username, password, user_type):
        return cls(username, password, user_type, id=_hash(username, password))

    def __eq__(self, __o: object) -> bool:
        return self.id == __o.id


def login_user(username: str, password: str, users) -> User:
    return User.login_user(username, password, users)


def signup_user(username: str, password: str, user_type: int, users) -> User:
    for user in users:
        if user.id == _hash(username, password):
            return user
        elif user.username == username:
            return None
    new_user = User.signup_user(username, password, user_type)
    new_user.is_Logged_in = True
    users.append(new_user)
    return new_user


def logout_user(username: str, users):
    for i in users:
        if i.username == username:
            i.is_Logged_in = False
            break


def create_manager_account(username, password):
    return User.signup_user(username, password, 3)
