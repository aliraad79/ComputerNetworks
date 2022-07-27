import socket
import os
import pickle

from threading import Thread
from dotenv import load_dotenv
from ticket import Text, Ticket, create_ticket

from users import (
    User,
    login_user,
    create_manager_account,
    logout_user,
    signup_user,
    is_user_loggeed_in,
    is_user_admin_or_manager,
)
from video import Video, add_video
from serilizers import (
    parse_two_part_string,
    parse_one_part_string,
    parse_three_part_string,
)

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))


def handle_user_reacts(conn, data, req_type):
    token, video_name = parse_two_part_string(data)
    if is_user_loggeed_in(token):
        video = Video.get_video(video_name)

        if req_type == "Like":
            video.likes += 1
        elif req_type == "DisLike":
            video.dislikes += 1
        elif req_type == "CommentVideo":
            video.add_comment(User.get_user(token), "".join(data.split()[3:]))

        conn.sendall(b"ReactSuc")
    else:
        conn.sendall(b"ReactFail")


def handle_tickets(conn, data, req_type):
    if req_type == "NewTicket":
        token = data.split()[1]
        user = User.get_user(token)
        if user:
            text = data.split()[2:]
            ticket = create_ticket(user)
            ticket.add_chat(Text(user, " ".join(text)))

            conn.sendall(b"NewTicketSuc")
        else:
            conn.sendall(b"NewTicketFail")

    elif req_type == "AnswerTicket":
        token, ticket_id = data.split()[1:3]
        user = User.get_user(token)
        ticket = Ticket.get_ticket(int(ticket_id))
        if user and ticket:
            text = data.split()[3:]
            ticket.add_chat(Text(user, " ".join(text)))
            conn.sendall(b"AnswerTicketSuc")
        else:
            conn.sendall(b"AnswerTicketFail")

    elif req_type == "ChangeTicketState":
        token, ticket_id, state = parse_three_part_string(data)
        user = User.get_user(token)
        ticket = Ticket.get_ticket(int(ticket_id))
        if user and ticket:
            ticket.change_state(int(state))
            conn.sendall(b"ChangeTicketStateSuc")
        else:
            conn.sendall(b"ChangeTicketStateFail")

    elif req_type == "GetTickets":
        token = parse_one_part_string(data)
        user = User.get_user(token)

        if user:
            tickets = Ticket.get_user_tickets(user)
            dump = pickle.dumps(tickets)
            conn.sendall(bytes(f"GetTicketsSuc ", "utf-8") + dump)
        else:
            conn.sendall(b"GetTicketsFail")


def handle_user_auth(conn, data, req_type):
    if req_type == "Login":
        username, password = parse_two_part_string(data)
        user = login_user(username, password)
        if user:
            if user.is_approved:
                conn.sendall(bytes(f"LoginSuc {user.id} {user.access_level}", "utf-8"))
            else:
                conn.sendall(b"LoginFail UserNotApprove")
        else:
            conn.sendall(b"LoginFail UserNotFound")

    elif req_type == "Signup":
        username, password, user_type = parse_three_part_string(data)
        user = signup_user(username, password, int(user_type))
        if user:
            conn.sendall(bytes(f"SingupSuc", "utf-8"))
        else:
            conn.sendall(b"SingupFail")

    elif req_type == "Logout":
        token = parse_one_part_string(data)
        if logout_user(token):
            conn.sendall(b"LogoutSuc")
        else:
            conn.sendall(b"LogoutFail")


def handle_video_uploading(conn, data):
    token, video_name = parse_two_part_string(data)
    user = User.get_user(token)
    if user:
        conn.sendall(b"Upload")
        with open(f"videos/{video_name}", "wb") as file:
            while True:
                bytes_read = conn.recv(1024)
                if not bytes_read:
                    break
                try:
                    if bytes_read.decode("utf-8") == "VideoFinished":
                        break
                except:
                    pass

                file.write(bytes_read)

            add_video(Video(video_name, user))
    else:
        conn.sendall(b"UploadFail")


def handle_approving_user(conn, data):
    token, target_username = parse_two_part_string(data)
    if is_user_admin_or_manager(token):
        user = User.get_user_by_username(target_username)
        if user:
            user.is_approved = True
            conn.sendall(b"AppSuc")
        else:
            conn.sendall(b"AppFail")
    else:
        conn.sendall(b"AppFail")


def handle_unstricking_user(conn, data):
    token, target_username = parse_two_part_string(data)
    if is_user_admin_or_manager(token):
        user = User.get_user_by_username(target_username)
        if user:
            user.is_striked = True
            conn.sendall(b"UnstrikeSuc")
        else:
            conn.sendall(b"UnstrikeFail")
    else:
        conn.sendall(b"UnstrikeFail")


def handle_banning_user(conn, data):
    token, video_name = parse_two_part_string(data)
    if is_user_admin_or_manager(token):
        video = Video.get_video(video_name)
        if video:
            video.is_ban = True
            conn.sendall(b"BanSuc")
        else:
            conn.sendall(b"BanFail")
    else:
        conn.sendall(b"BanFail")


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
            conn.sendall(bytes(videos, "utf-8"))

        elif req_type == "UploadVideo":
            handle_video_uploading(conn, data)

        elif req_type == "Ban":
            handle_banning_user(conn, data)
        elif req_type == "Unstrike":
            handle_unstricking_user(conn, data)
        elif req_type == "App":
            handle_approving_user(conn, data)

        elif req_type in [
            "NewTicket",
            "AnswerTicket",
            "ChangeTicketState",
            "GetTickets",
        ]:
            handle_tickets(conn, data, req_type)


def accept_connections():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(10)
        while True:
            conn, addr = s.accept()
            Thread(target=thread_runner, args=(conn,)).start()


if __name__ == "__main__":
    create_manager_account(os.getenv("Manger_Username"), os.getenv("Manager_Password"))
    create_manager_account("t", "t")
    Thread(target=accept_connections).start()
