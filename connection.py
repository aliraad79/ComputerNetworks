import socket
import pickle
import os
import struct

from enum import Enum
from time import sleep

from dotenv import load_dotenv
from utils.log import logger_config
from pathlib import Path
from utils.transport import receive_message as transport_receive_message
from utils.transport import send_message as transport_send_message

from modules.video_player import VideoPlayerClient

load_dotenv()

HOST = os.getenv("HOST")
PROXY_PORT = int(os.getenv("PROXY_PORT"))
PORT = int(os.getenv("PORT"))
logger = logger_config()


token = None
rule = None


class Rules(Enum):
    USER = 1
    ADMIN = 2
    MANAGER = 3


class ChossableLabel(Enum):
    Under_13 = 1
    Under_18 = 2
    R_rated = 3
    Violance = 4
    May_find_argumantive = 5


def get_terminal_input(
    msg, options, get_input_message="Enter your choice: ", input_type=int
):
    if msg != "":
        logger.info(msg)
    for counter, i in enumerate(options):
        print(f"\t{1 + counter}. {i}")
    while True:
        try:
            return input_type(input(get_input_message).strip())
        except ValueError:
            logger.warning("Not valid choice")


def get_network_response(socket_conn: socket.socket):
    return transport_receive_message(socket_conn).decode()


def send_message(socket_conn: socket.socket, msg):
    transport_send_message(socket_conn, bytes(msg, "utf-8"))


def send_login_info(socket_conn: socket.socket):
    username = get_terminal_input("", [], "Username: ", str)
    password = get_terminal_input("", [], "Password: ", str)
    send_message(socket_conn, f"Login {username} {password}")


def get_and_send_signup_info(socket_conn: socket.socket):
    usertype = get_terminal_input("User Access level", ["User", "Admin"])
    username = get_terminal_input("", [], "Username: ", str)
    password = get_terminal_input("", [], "Password: ", str)
    send_message(socket_conn, f"Signup {username} {password} {usertype}")


def send_file(file_path: str, socket_conn: socket.socket) -> None:
    logger.info("Sending ..........")
    with open(file_path, "rb") as file:
        file_size = os.path.getsize(file_path)
        socket_conn.sendall(struct.pack("Q", file_size))
        socket_conn.sendfile(file)

    sleep(1)

    confirmation = get_network_response(socket_conn)
    assert confirmation == "ok"

    send_message(socket_conn, "VideoFinished")

    confirmation = get_network_response(socket_conn)
    assert confirmation == "ok"
    print("video finished")


def unstrike_user_routine(socket_conn: socket.socket):
    target_username = get_terminal_input("", [], "username: ", str)
    send_message(socket_conn, f"Unstrike {token} {target_username}")

    response = get_network_response(socket_conn)
    if response == "UnstrikeSuc":
        logger.info("Unstriking User Sucessfull")
    elif response == "UnstrikeFail":
        logger.error("Unstriking User Failed")


def ban_user_routine(socket_conn: socket.socket):
    video_name = get_terminal_input("", [], "Video name: ", str)
    send_message(socket_conn, f"Ban {token} {video_name}")

    response = get_network_response(socket_conn)
    if response == "BanSuc":
        logger.info("Banning video Sucessfull")
    elif response == "BanFail":
        logger.error("Banning video Failed")


def add_label_routine(socket_conn: socket.socket):
    video_name = get_terminal_input("", [], "Video name: ", str)
    label = get_terminal_input(
        "Choose label to add",
        ["Under 13", "Under 18", "R rated", "Violance", "May find argumantive"],
    )
    send_message(socket_conn, f"AddLabel {token} {video_name} {label}")

    response = get_network_response(socket_conn)
    if response == "AddLabelSuc":
        logger.info("Label Added to video Sucessfully")
    elif response == "AddLabelFail":
        logger.error("Adding label counter error")


def comment_on_video_routine(socket_conn: socket.socket):
    video_name = get_terminal_input("", [], "Video name: ", str)
    comment = get_terminal_input("", [], "Your Comment: ", str)
    send_message(socket_conn, f"CommentVideo {token} {video_name} {comment}")

    response = get_network_response(socket_conn)
    if response == "ReactSuc":
        logger.info("Comment Submitted")
    elif response == "ReactFail":
        logger.error("Comment Fail")


def dislike_video_routine(socket_conn: socket.socket):
    video_id = get_terminal_input("", [], "Video name: ", str)
    send_message(socket_conn, f"DisLike {token} {video_id}")

    response = get_network_response(socket_conn)
    if response == "ReactSuc":
        logger.info("DisLike Submitted")
    elif response == "ReactFail":
        logger.error("DisLike Fail")


def like_video_routine(socket_conn: socket.socket):
    video_id = get_terminal_input("", [], "Video name: ", str)
    send_message(socket_conn, f"Like {token} {video_id}")

    response = get_network_response(socket_conn)
    if response == "ReactSuc":
        logger.info("Like Submitted")
    elif response == "ReactFail":
        logger.error("Like Fail")


def upload_file_routine(socket_conn: socket.socket):
    video_path = get_terminal_input("", [], "Video Path: ", str)
    # TODO what's the filename that should be sent to server
    send_message(socket_conn, f"UploadVideo {token} {Path(video_path).name}")
    response = get_network_response(socket_conn)
    if response == "UploadSuc":
        send_file(video_path, socket_conn)
    elif response == "UploadFail":
        logger.error("Uploading Video failed")


def view_video_routine(socket_conn: socket.socket):
    video_name = get_terminal_input("", [], "Video Name: ", str)
    send_message(socket_conn, f"ViewVideo {token} {video_name}")
    response = get_network_response(socket_conn)
    if response == "View":
        video_player_client = VideoPlayerClient()
        video_player_client.start(socket_conn)
    elif response == "ViewFail":
        logger.error("Viewing Video failed")


def approve_admin_routine(socket_conn: socket.socket):
    username = get_terminal_input("", [], "Username: ", str)
    send_message(socket_conn, f"App {token} {username}")
    response = get_network_response(socket_conn)
    if response == "AppSuc":
        logger.info(f"Approved {username}")
    elif response == "AppFail":
        logger.error(f"Can't Approve {username}")


def new_ticket_routine(socket_conn: socket.socket):
    text = get_terminal_input("", [], "Your Complain: ", str)
    send_message(socket_conn, f"NewTicket {token} {text}")
    response = get_network_response(socket_conn)
    if response == "NewTicketSuc":
        logger.info(f"Ticket Created")
    elif response == "NewTicketFail":
        logger.error(f"Creating ticket has counter error")


def answer_ticket_routine(socket_conn: socket.socket):
    ticket_id = get_terminal_input("", [], "ticket_id: ", int)
    text = get_terminal_input("", [], "Your Comment on ticket: ", str)
    send_message(socket_conn, f"AnswerTicket {token} {ticket_id} {text}")
    response = get_network_response(socket_conn)
    if response == "AnswerTicketSuc":
        logger.info(f"New Comment Added")
    elif response == "AnswerTicketFail":
        logger.error(f"Answering ticket has counter error")


def change_ticket_state_routine(socket_conn: socket.socket):
    ticket_id = get_terminal_input("", [], "ticket_id: ", int)
    state = get_terminal_input("Choose State", ["New", "Pending", "Solved", "Closed"])
    send_message(socket_conn, f"ChangeTicketState {token} {ticket_id} {state}")
    response = get_network_response(socket_conn)
    if response == "ChangeTicketStateSuc":
        logger.info(f"Ticket State Changed")
    elif response == "ChangeTicketStateFail":
        logger.error(f"changing ticket state has counter error")


def see_all_tickets_routine(socket_conn: socket.socket):
    send_message(socket_conn, f"GetTickets {token} ")

    data = transport_receive_message(socket_conn)

    if data.startswith(b"GetTicketsSuc"):
        logger.info("Your Tickets:")
        pickle_data = data[len("GetTicketsSuc "):]

        target_data = pickle.loads(pickle_data)
        for i in target_data:
            print(i)
    elif data.startswith(b"GetTicketsFail"):
        logger.error(f"getting all tickets has counter error")


def logout_routine(socket_conn: socket.socket):
    global token, rule

    send_message(socket_conn, f"Logout {token}")
    response = get_network_response(socket_conn)
    if response == "LogoutSuc":
        logger.info("Logout Succesfull")
        rule = token = None
    elif response == "LogoutFail":
        logger.error("Logout failed")


def signup_routine(socket_conn: socket.socket):
    global token, rule

    get_and_send_signup_info(socket_conn)
    response = get_network_response(socket_conn).split()
    if response[0] == "SignupSuc":
        logger.info("Signup Successful!")
    elif response[0] == "SignupFail":
        logger.error("Signup Failed!")


def login_routine(socket_conn: socket.socket):
    global token, rule

    send_login_info(socket_conn)

    response = get_network_response(socket_conn).split()
    if response[0] == "LoginSuc":
        logger.info("Login Succesfull!")
        token = response[1]
        rule = Rules(int(response[2]))

    elif response[0] == "LoginFail":
        if response[1] == "UserNotFound":
            logger.error("User Not Found!")
        elif response[1] == "UserNotApprove":
            logger.warning("Your user is not approve by manager yet!")


def manager_menu(socket_conn: socket.socket):
    inp = get_terminal_input(
        "Welcome To Wetube",
        [
            "Approve Admin account",
            "Answer Ticket",
            "See all my Tickets",
            "Change Ticket State",
            "Logout",
            "Disconnect",
        ],
    )
    if inp == 1:
        approve_admin_routine(socket_conn)
    elif inp == 2:
        answer_ticket_routine(socket_conn)
    elif inp == 3:
        see_all_tickets_routine(socket_conn)
    elif inp == 4:
        change_ticket_state_routine(socket_conn)
    elif inp == 5:
        logout_routine(socket_conn)
    elif inp == 6:
        socket_conn.close()
        exit()


def admin_menu(socket_conn: socket.socket):
    inp = get_terminal_input(
        "Welcome To Wetube",
        [
            "See all videos",
            "View video",
            "Ban Video",
            "Unstrike User",
            "Add label to video",
            "New Ticket",
            "Answer Ticket",
            "See all my Tickets",
            "Change Ticket State",
            "Logout",
            "Disconnect",
        ],
    )
    if inp == 1:
        send_message(socket_conn, "GetAllVideos")
        print(get_network_response(socket_conn))
    elif inp == 2:
        view_video_routine(socket_conn)
    elif inp == 3:
        ban_user_routine(socket_conn)
    elif inp == 4:
        unstrike_user_routine(socket_conn)
    elif inp == 5:
        add_label_routine(socket_conn)
    elif inp == 6:
        new_ticket_routine(socket_conn)
    elif inp == 7:
        answer_ticket_routine(socket_conn)
    elif inp == 8:
        see_all_tickets_routine(socket_conn)
    elif inp == 9:
        change_ticket_state_routine(socket_conn)
    elif inp == 10:
        logout_routine(socket_conn)
    elif inp == 11:
        socket_conn.close()
        exit()


def user_menu(socket_conn: socket.socket):
    inp = get_terminal_input(
        "Welcome To Wetube",
        [
            "Upload Video",
            "View video",
            "Like video",
            "DisLike video",
            "Comment On video",
            "New Ticket",
            "Answer Ticket",
            "See all my Tickets",
            "See all videos",
            "Logout",
            "Disconnect",
        ],
    )
    if inp == 1:
        upload_file_routine(socket_conn)
    elif inp == 2:
        view_video_routine(socket_conn)
    elif inp == 3:
        like_video_routine(socket_conn)
    elif inp == 4:
        dislike_video_routine(socket_conn)
    elif inp == 5:
        comment_on_video_routine(socket_conn)
    elif inp == 6:
        new_ticket_routine(socket_conn)
    elif inp == 7:
        answer_ticket_routine(socket_conn)
    elif inp == 8:
        see_all_tickets_routine(socket_conn)
    elif inp == 9:
        send_message(socket_conn, "GetAllVideos")
        print(get_network_response(socket_conn))
    elif inp == 10:
        logout_routine(socket_conn)
    elif inp == 11:
        socket_conn.close()
        exit()


def user_thread(socket_conn: socket.socket):
    global token, rule

    if token:
        if rule == Rules.USER:
            user_menu(socket_conn)
        elif rule == Rules.ADMIN:
            admin_menu(socket_conn)
        elif rule == Rules.MANAGER:
            manager_menu(socket_conn)

    else:
        inp = get_terminal_input("Welcome To Wetube", ["Login", "Signup"])
        if inp == 1:
            login_routine(socket_conn)
        elif inp == 2:
            signup_routine(socket_conn)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        try:
            user_thread(s)
        except ConnectionResetError:
            logger.error("Connection Reset")
            s.close()
            break
