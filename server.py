import socket
import os

from threading import Thread
from dotenv import load_dotenv

from users import (
    User,
    login_user,
    create_manager_account,
    logout_user,
    signup_user,
    is_user_loggeed_in,
    is_user_admin_or_manager,
)
from video import Video
from serilizers import (
    parse_ban_string,
    parse_react_string,
    parse_login_string,
    parse_signup_string,
    parse_unstrike_string,
)


load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))


def handle_user_reacts(conn, data, req_type):
    token, video_id = parse_react_string(data)
    if is_user_loggeed_in(token):
        video = Video.get_video(video_id)

        if req_type == "Like":
            video.likes += 1
        elif req_type == "DisLike":
            video.dislikes += 1
        elif req_type == "CommentVideo":
            video.add_comment(User.get_user(token), data.split()[3:])

        conn.sendall(b"ReactSuc")
    else:
        conn.sendall(b"ReactFail")


def handle_user_auth(conn, data, req_type):
    if req_type == "Login":
        user_name, password = parse_login_string(data)
        user = login_user(user_name, password)
        if user:
            conn.sendall(b"LoginSuc " + bytes(user.id, "utf-8"))
        else:
            conn.sendall(b"LoginFail")

    elif req_type == "Signup":
        user_name, password, user_type = parse_signup_string(data)
        user = signup_user(user_name, password, user_type)
        if user:
            conn.sendall(b"SingupSuc " + bytes(user.id, "utf-8"))
        else:
            conn.sendall(b"SingupFail")

    elif req_type == "Logout":
        if logout_user(data[1]):
            conn.sendall(b"LogoutSuc")
        else:
            conn.sendall(b"LogoutFail")


def thread_runner(conn: socket.socket):
    while True:
        data = conn.recv(1024).decode("utf-8")
        print(f"Received: {data}")
        if data == "":
            break
        req_type = data.split()[0]

        if req_type in ["Login", "Signup", "Logout"]:
            handle_user_auth(conn, data, req_type)
        elif req_type in ["Like", "DisLike", "CommentVideo"]:
            handle_user_reacts(conn, data, req_type)

        elif req_type == "GetAllVideos":
            videos = Video.get_all()
            conn.sendall(b"Videos:\n" + b"\n".join(videos))

        elif req_type == "UploadFile":
            with open("temp", "wb") as file:
                while True:
                    bytes_read = conn.recv(1024)
                    if not bytes_read or bytes_read.decode("utf-8") == "FileFinished":
                        break

                    file.write(bytes_read)
        elif req_type == "Ban":
            token, video_id = parse_ban_string()
            if is_user_admin_or_manager(token):
                video = Video.get_video(video_id)
                if video:
                    video.is_ban = True
                    conn.sendall("BanSuc")
                else:
                    conn.sendall("BanFail")
            else:
                conn.sendall("BanFail")

        elif req_type == "Unstrike":
            token, target_username = parse_unstrike_string()
            if is_user_admin_or_manager(token):
                user = User.get_user_by_username(target_username)
                if user:
                    user.is_striked = True
                    conn.sendall("UnstrikeSuc")
                else:
                    conn.sendall("UnstrikeFail")
            else:
                conn.sendall("UnstrikeFail")


def accept_connections():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            Thread(target=thread_runner, args=(conn,)).start()


if __name__ == "__main__":
    create_manager_account(os.getenv("Manger_Username"), os.getenv("Manager_Password"))
    Thread(target=accept_connections).start()
