import socket
import os

from threading import Thread, Condition
from typing import Tuple
from dotenv import load_dotenv

from auth import authenticate_user, logout_user, signup_user


load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

# cv: Condition = Condition()


def parse_login_string(input_string: str) -> Tuple[str, str]:
    splited_string = input_string.split()
    return splited_string[1], splited_string[2]


def parse_signup_string(input_string: str) -> Tuple[str, str, str]:
    splited_string = input_string.split()
    return splited_string[1], splited_string[2], splited_string[3]


def thread_runner(conn: socket.socket):
    while True:
        data = conn.recv(1024).decode("utf-8")
        print(f"Received: {data}")
        req_type = data.split()[0]

        if req_type == "Login":
            user_name, password = parse_login_string(data)
            user = authenticate_user(user_name, password)
            if user:
                conn.sendall(b"LoginSuc")

        elif req_type == "Signup":
            user_name, password, user_type = parse_signup_string(data)
            user = signup_user(user_name, password, user_type)
            if user:
                conn.sendall(b"SingupSuc")

        elif req_type == "Logout":
            conn.sendall(b"LogoutSuc")
            logout_user(data[1])
            print("Logged Out")

        elif req_type == "UploadFile":
            with open("temp", "wb") as file:
                while True:
                    bytes_read = conn.recv(1024)
                    print(bytes_read)
                    if not bytes_read or bytes_read.decode("utf-8") == "FileFinished":
                        break

                    file.write(bytes_read)
            print("File finished")


def accept_connections():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            Thread(target=thread_runner, args=(conn,)).start()


if __name__ == "__main__":
    Thread(target=accept_connections).start()
