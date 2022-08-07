import socket
import os
import pickle

from threading import Thread
from dotenv import load_dotenv

from utils.transport import receive_message as transport_receive_message
from utils.transport import send_message as transport_send_message

from modules.ticket import Text, Ticket, create_ticket
from modules.video import Video, add_video
from modules.users import (
    User,
    login_user,
    create_manager_account,
    logout_user,
    signup_user,
    is_user_loggeed_in,
    is_user_admin_or_manager,
)
from utils.serilizers import (
    parse_one_part_string,
    parse_two_part_string,
    parse_three_part_string,
)
from modules.video_player import VideoPlayerServer

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))


def get_message(socket_conn: socket.socket):
    return transport_receive_message(socket_conn).decode()


def send_message(socket_conn: socket.socket, msg):
    transport_send_message(socket_conn, bytes(msg, "utf-8"))


def handle_user_reacts(socket_conn: socket.socket, data, req_type):
    token, video_name = parse_two_part_string(data)
    if is_user_loggeed_in(token):
        video = Video.get_video(video_name)
        if not video:
            send_message(socket_conn, "ReactFail")
        else:
            if req_type == "Like":
                video.likes += 1
            elif req_type == "DisLike":
                video.dislikes += 1
            elif req_type == "CommentVideo":
                video.add_comment(User.get_user(token), "".join(data.split()[3:]))

            send_message(socket_conn, "ReactSuc")
    else:
        send_message(socket_conn, "ReactFail")


def handle_tickets(socket_conn: socket.socket, data, req_type):
    if req_type == "NewTicket":
        token = data.split()[1]
        user = User.get_user(token)
        if user:
            text = data.split()[2:]
            ticket = create_ticket(user)
            ticket.add_chat(Text(user, " ".join(text)))

            send_message(socket_conn, "NewTicketSuc")
        else:
            send_message(socket_conn, "NewTicketFail")

    elif req_type == "AnswerTicket":
        token, ticket_id = data.split()[1:3]
        user = User.get_user(token)
        ticket = Ticket.get_ticket(int(ticket_id))
        if user and ticket:
            text = data.split()[3:]
            ticket.add_chat(Text(user, " ".join(text)))
            send_message(socket_conn, "AnswerTicketSuc")
        else:
            send_message(socket_conn, "AnswerTicketFail")

    elif req_type == "ChangeTicketState":
        token, ticket_id, state = parse_three_part_string(data)
        user = User.get_user(token)
        ticket = Ticket.get_ticket(int(ticket_id))
        if user and ticket:
            ticket.change_state(int(state))
            send_message(socket_conn, "ChangeTicketStateSuc")
        else:
            send_message(socket_conn, "ChangeTicketStateFail")

    elif req_type == "GetTickets":
        token = parse_one_part_string(data)
        user = User.get_user(token)

        if user:
            tickets = Ticket.get_user_tickets(user)
            dump = pickle.dumps(tickets)
            transport_send_message(socket_conn, bytes(f"GetTicketsSuc ", "utf-8") + dump)
        else:
            send_message(socket_conn, "GetTicketsFail")


def handle_user_auth(socket_conn: socket.socket, data, req_type):
    if req_type == "Login":
        username, password = parse_two_part_string(data)
        user = login_user(username, password)
        if user:
            if user.is_approved:
                send_message(socket_conn, f"LoginSuc {user.id} {user.access_level}")
            else:
                send_message(socket_conn, "LoginFail UserNotApprove")
        else:
            send_message(socket_conn, "LoginFail UserNotFound")

    elif req_type == "Signup":
        username, password, user_type = parse_three_part_string(data)
        user = signup_user(username, password, int(user_type))
        if user:
            send_message(socket_conn, "SignupSuc")
        else:
            send_message(socket_conn, "SignupFail")

    elif req_type == "Logout":
        token = parse_one_part_string(data)
        if logout_user(token):
            send_message(socket_conn, "LogoutSuc")
        else:
            send_message(socket_conn, "LogoutFail")


def handle_video_uploading(socket_conn: socket.socket, data):
    token, video_name = parse_two_part_string(data)
    user = User.get_user(token)
    if user:
        send_message(socket_conn, "UploadSuc")
        os.makedirs("videos", exist_ok=True)
        with open(os.path.join("videos", video_name), "wb") as file:
            bytes_read = transport_receive_message(socket_conn)
            file.write(bytes_read)

            send_message(socket_conn, "ok")
            finished_message = get_message(socket_conn)
            assert finished_message == "VideoFinished"

            add_video(Video(video_name, user))
            send_message(socket_conn, "ok")
    else:
        send_message(socket_conn, "UploadFail")


def handle_video_streaming(socket_conn: socket.socket, data):
    token, video_name = parse_two_part_string(data)

    video = Video.get_video(video_name)
    user = User.get_user(token)

    if user and video:
        video_player_server = VideoPlayerServer()
        send_message(socket_conn, "View")
        video_player_server.start(socket_conn, video)
    else:
        send_message(socket_conn, "ViewFail")


def handle_adding_label_to_video(socket_conn: socket.socket, data):
    token, video_name, label_id = parse_three_part_string(data)
    video = Video.get_video(video_name)
    if is_user_admin_or_manager(token) and video:
        video.add_label(int(label_id))
        send_message(socket_conn, "AddLabelSuc")
    else:
        send_message(socket_conn, "AddLabelFail")


def handle_approving_user(socket_conn: socket.socket, data):
    token, target_username = parse_two_part_string(data)
    if is_user_admin_or_manager(token):
        user = User.get_user_by_username(target_username)
        if user:
            user.is_approved = True
            send_message(socket_conn, "AppSuc")
        else:
            send_message(socket_conn, "AppFail")
    else:
        send_message(socket_conn, "AppFail")


def handle_unstricking_user(socket_conn: socket.socket, data):
    token, target_username = parse_two_part_string(data)
    if is_user_admin_or_manager(token):
        user = User.get_user_by_username(target_username)
        if user:
            user.is_striked = True
            send_message(socket_conn, "UnstrikeSuc")
        else:
            send_message(socket_conn, "UnstrikeFail")
    else:
        send_message(socket_conn, "UnstrikeFail")


def handle_banning_video(socket_conn: socket.socket, data):
    token, video_name = parse_two_part_string(data)
    if is_user_admin_or_manager(token):
        video = Video.get_video(video_name)
        if video:
            video.ban()
            send_message(socket_conn, "BanSuc")
        else:
            send_message(socket_conn, "BanFail")
    else:
        send_message(socket_conn, "BanFail")


def thread_runner(socket_conn: socket.socket):
    while True:
        data = get_message(socket_conn)
        print(f"Received: {data}")
        if data == "":
            break
        req_type = data.split()[0]

        if req_type in ["Login", "Signup", "Logout"]:
            handle_user_auth(socket_conn, data, req_type)
        elif req_type in ["Like", "DisLike", "CommentVideo"]:
            handle_user_reacts(socket_conn, data, req_type)

        elif req_type == "GetAllVideos":
            videos = Video.get_all_unband_videos()
            send_message(socket_conn, videos)

        elif req_type == "UploadVideo":
            handle_video_uploading(socket_conn, data)
        elif req_type == "ViewVideo":
            handle_video_streaming(socket_conn, data)
        elif req_type == "AddLabel":
            handle_adding_label_to_video(socket_conn, data)

        elif req_type == "Ban":
            handle_banning_video(socket_conn, data)
        elif req_type == "Unstrike":
            handle_unstricking_user(socket_conn, data)
        elif req_type == "App":
            handle_approving_user(socket_conn, data)

        elif req_type in [
            "NewTicket",
            "AnswerTicket",
            "ChangeTicketState",
            "GetTickets",
        ]:
            handle_tickets(socket_conn, data, req_type)


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
    signup_user("a", "a", 1)
    Thread(target=accept_connections).start()
