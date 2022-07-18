import socket
import os

from threading import Thread
from typing import List, Tuple
from dotenv import load_dotenv

from auth import User, authenticate_user, logout_user, signup_user
from video import Video


load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))

users: List[User] = []
videos: List[Video] = []


def parse_react_string(input_string: str) -> Tuple[str, str]:
    """
    <req> <username> <video_id>
    """
    splited_string = input_string.split()
    return splited_string[1], splited_string[2]


def parse_login_string(input_string: str) -> Tuple[str, str]:
    """
    <req> <username> <password>
    """
    splited_string = input_string.split()
    return splited_string[1], splited_string[2]


def parse_signup_string(input_string: str) -> Tuple[str, str, str]:
    """
    <req> <username> <password> <usertype>
    """
    splited_string = input_string.split()
    return splited_string[1], splited_string[2], splited_string[3]


def handle_user_reacts(conn, data, req_type):
    user_name, video_id = parse_react_string(data)
    for video in videos:
        if video.id == video_id:
            if req_type == "Like":
                video.likes += 1
            elif req_type == "DisLike":
                video.dislikes += 1
            elif req_type == "CommentVideo":
                video.add_comment(data.split()[3:])
            break


def handle_user_auth(conn, data, req_type):
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
        logout_user(data[1], users)
        print("Logged Out")


def thread_runner(conn: socket.socket):
    while True:
        data = conn.recv(1024).decode("utf-8")
        print(f"Received: {data}")
        req_type = data.split()[0]

        if req_type in ["Login", "Signup", "Logout"]:
            handle_user_auth(conn, data, req_type)
        elif req_type in ["Like", "DisLike", "CommentVideo"]:
            handle_user_reacts(conn, data, req_type)

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
