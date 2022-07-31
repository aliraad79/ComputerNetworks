import socket
import pickle
import struct
import cv2

from enum import Enum
from time import sleep
from log import logger_config
from pathlib import Path

from server import HOST, PORT

token = None
rule = None
logger = logger_config()


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


def get_network_response(s):
    return s.recv(1024).decode()


def send_message(socket, msg):
    socket.sendall(bytes(msg, "utf-8"))


def send_login_info(socket):
    username = get_terminal_input("", [], "Username: ", str)
    password = get_terminal_input("", [], "Password: ", str)
    send_message(socket, f"Login {username} {password}")


def get_and_send_singup_info(socket):
    usertype = get_terminal_input("User Access level", ["User", "Admin"])
    username = get_terminal_input("", [], "Username: ", str)
    password = get_terminal_input("", [], "Password: ", str)
    send_message(socket, f"Signup {username} {password} {usertype}")


def send_file(file_path: str, socket) -> None:
    logger.info("Sending ..........")
    with open(file_path, "rb") as file:
        socket.sendfile(file)
        # while True:
        #     part_of_file = file.read(1024)
        #     if not part_of_file:
        #         break
        #     socket.sendall(part_of_file)
    # TODO: there must be a better way than this
    sleep(1)
    socket.sendall(b"VideoFinished")


def unstrike_user_routine(socket):
    target_username = get_terminal_input("", [], "username: ", str)
    send_message(socket, f"Unstrike {token} {target_username}")

    response = get_network_response(socket)
    if response == "UnstrikeSuc":
        logger.info("Unstriking User Sucessfull")
    elif response == "UnstrikeFail":
        logger.error("Unstriking User Failed")
    else:
        pass
        # TODO log or raise exception


def ban_user_routine(socket):
    video_name = get_terminal_input("", [], "Video name: ", str)
    send_message(socket, f"Ban {token} {video_name}")

    response = get_network_response(socket)
    if response == "BanSuc":
        logger.info("Banning video Sucessfull")
    elif response == "BanFail":
        logger.error("Banning video Failed")


def add_label_routine(socket):
    video_name = get_terminal_input("", [], "Video name: ", str)
    label = get_terminal_input(
        "Choose label to add",
        ["Under 13", "Under 18", "R rated", "Violance", "May find argumantive"],
    )
    send_message(socket, f"AddLabel {token} {video_name} {label}")

    response = get_network_response(socket)
    if response == "AddLabelSuc":
        logger.info("Label Added to video Sucessfully")
    elif response == "AddLabelFail":
        logger.error("Adding label counter error")


def comment_on_video_routine(socket):
    video_name = get_terminal_input("", [], "Video name: ", str)
    comment = get_terminal_input("", [], "Your Comment: ", str)
    send_message(socket, f"CommentVideo {token} {video_name} {comment}")

    response = get_network_response(socket)
    if response == "ReactSuc":
        logger.info("Comment Submitted")
    elif response == "ReactFail":
        logger.error("Comment Fail")


def dislike_video_routine(socket):
    video_id = get_terminal_input("", [], "Video name: ", str)
    send_message(socket, f"DisLike {token} {video_id}")

    response = get_network_response(socket)
    if response == "ReactSuc":
        logger.info("DisLike Submitted")
    elif response == "ReactFail":
        logger.error("DisLike Fail")


def like_video_routine(socket):
    video_id = get_terminal_input("", [], "Video name: ", str)
    send_message(socket, f"Like {token} {video_id}")

    response = get_network_response(socket)
    if response == "ReactSuc":
        logger.info("Like Submitted")
    elif response == "ReactFail":
        logger.error("Like Fail")


def upload_file_routine(socket):
    video_path = get_terminal_input("", [], "Video Path: ", str)
    # TODO what's the filename that should be sent to server
    send_message(socket, f"UploadVideo {token} {Path(video_path).name}")
    response = get_network_response(socket)
    if response == "Upload":
        send_file(video_path, socket)
    elif response == "UploadFail":
        logger.error("Uploading Video failed")

def view_video_routine(socket):
    video_name = get_terminal_input("", [], "Video Name: ", str)
    send_message(socket, f"ViewVideo {token} {video_name}")
    response = get_network_response(socket)
    if response == "View":
        #used in handling binary data from network connections
        data = b""
        # Q: unsigned long long integer(8 bytes)
        payload_size = struct.calcsize("Q")
        while True:
            while len(data) < payload_size:
                packet = socket.recv(4*1024)
                if not packet: break
                data+=packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]
            while len(data) < msg_size:
                data += socket.recv(4*1024)
            frame_data = data[:msg_size]
            data  = data[msg_size:]
            frame = pickle.loads(frame_data)
            frame_image = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            cv2.imshow("Receiving...", frame_image)
            key = cv2.waitKey(1) 
            if key  == 13:
                cv2.destroyAllWindows()
                break
    elif response == "ViewFail":
        logger.error("Viewing Video failed")

def approve_admin_routine(socket):
    username = get_terminal_input("", [], "Username: ", str)
    send_message(socket, f"App {token} {username}")
    response = get_network_response(socket)
    if response == "AppSuc":
        logger.info(f"Approved {username}")
    elif response == "AppFail":
        logger.error(f"Can't Approve {username}")


def new_ticket_routine(socket):
    text = get_terminal_input("", [], "Your Complain: ", str)
    send_message(socket, f"NewTicket {token} {text}")
    response = get_network_response(socket)
    if response == "NewTicketSuc":
        logger.info(f"Ticket Created")
    elif response == "NewTicketFail":
        logger.error(f"Creating ticket has counter error")


def answer_ticket_routine(socket):
    ticket_id = get_terminal_input("", [], "ticket_id: ", int)
    text = get_terminal_input("", [], "Your Comment on ticket: ", str)
    send_message(socket, f"AnswerTicket {token} {ticket_id} {text}")
    response = get_network_response(socket)
    if response == "AnswerTicketSuc":
        logger.info(f"New Comment Added")
    elif response == "AnswerTicketFail":
        logger.error(f"Answering ticket has counter error")


def change_ticket_state_routine(socket):
    ticket_id = get_terminal_input("", [], "ticket_id: ", int)
    state = get_terminal_input("Choose State", ["New", "Pending", "Solved", "Closed"])
    send_message(socket, f"ChangeTicketState {token} {ticket_id} {state}")
    response = get_network_response(socket)
    if response == "ChangeTicketStateSuc":
        logger.info(f"Ticket State Changed")
    elif response == "ChangeTicketStateFail":
        logger.error(f"changing ticket state has counter error")


def see_all_tickets_routine(socket):
    send_message(socket, f"GetTickets {token} ")
    data = s.recv(1024)

    if data.startswith(b"GetTicketsSuc"):
        logger.info("Your Tickets:")
        pickle_data = data[len("GetTicketsSuc ") :]

        target_data = pickle.loads(pickle_data)
        for i in target_data:
            print(i)
    elif data.startswith(b"GetTicketsFail"):
        logger.error(f"getting all tickets has counter error")


def logout_routine(socket):
    global token, rule

    send_message(socket, f"Logout {token}")
    response = get_network_response(socket)
    if response == "LogoutSuc":
        logger.info("Logout Succesfull")
        rule = token = None
    elif response == "LogoutFail":
        logger.error("Logout failed")


def signup_routine(socket):
    global token, rule

    get_and_send_singup_info(socket)
    response = get_network_response(socket).split()
    if response[0] == "SingupSuc":
        logger.info("Signup Succesfull!")
    elif response[0] == "SingupFail":
        logger.error("Signup Failed!")


def login_routine(socket):
    global token, rule

    send_login_info(socket)

    response = get_network_response(socket).split()
    if response[0] == "LoginSuc":
        logger.info("Login Succesfull!")
        token = response[1]
        rule = Rules(int(response[2]))

    elif response[0] == "LoginFail":
        if response[1] == "UserNotFound":
            logger.error("User Not Found!")
        elif response[1] == "UserNotApprove":
            logger.warning("Your user is not approve by manager yet!")


def manager_menu(socket):
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
        approve_admin_routine(socket)
    elif inp == 2:
        answer_ticket_routine(socket)
    elif inp == 3:
        see_all_tickets_routine(socket)
    elif inp == 4:
        change_ticket_state_routine(socket)
    elif inp == 5:
        logout_routine(socket)
    elif inp == 6:
        socket.close()
        exit()


def admin_menu(socket):
    inp = get_terminal_input(
        "Welcome To Wetube",
        [
            "Ban Video",
            "Unstrike User",
            "Add label to video",
            "New Ticket",
            "Answer Ticket",
            "See all my Tickets",
            "Change Ticket State",
            "Logout",
            "Disconnect",
            "GetAllVideos",
            # view video
        ],
    )
    if inp == 1:
        ban_user_routine(socket)
    elif inp == 2:
        unstrike_user_routine(socket)
    elif inp == 3:
        add_label_routine(socket)
    elif inp == 4:
        new_ticket_routine(socket)
    elif inp == 5:
        answer_ticket_routine(socket)
    elif inp == 6:
        see_all_tickets_routine(socket)
    elif inp == 7:
        change_ticket_state_routine(socket)
    elif inp == 8:
        logout_routine(socket)
    elif inp == 9:
        socket.close()
        exit()
    elif inp == 10:
        send_message(socket, "GetAllVideos")
        print(get_network_response(socket))


def user_menu(socket):
    inp = get_terminal_input(
        "Welcome To Wetube",
        [
            "Upload Video",
            "Like video",
            "DisLike video",
            "Comment On video",
            "New Ticket",
            "Answer Ticket",
            "See all my Tickets",
            "GetAllVideos",
            "Logout",
            "Disconnect",
            "View video",
        ],
    )
    if inp == 1:
        upload_file_routine(socket)
    elif inp == 2:
        like_video_routine(socket)
    elif inp == 3:
        dislike_video_routine(socket)
    elif inp == 4:
        comment_on_video_routine(socket)
    elif inp == 5:
        new_ticket_routine(socket)
    elif inp == 6:
        answer_ticket_routine(socket)
    elif inp == 7:
        see_all_tickets_routine(socket)
    elif inp == 8:
        send_message(socket, "GetAllVideos")
        print(get_network_response(socket))
    elif inp == 9:
        logout_routine(socket)
    elif inp == 10:
        socket.close()
        exit()
    elif inp == 11:
        view_video_routine(socket)


def user_thread(socket):
    global token, rule

    if token:
        if rule == Rules.USER:
            user_menu(socket)
        elif rule == Rules.ADMIN:
            admin_menu(socket)
        elif rule == Rules.MANAGER:
            manager_menu(socket)

    else:
        inp = get_terminal_input("Welcome To Wetube", ["Login", "Signup"])
        if inp == 1:
            login_routine(socket)
        elif inp == 2:
            signup_routine(socket)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        try:
            user_thread(s)
        except ConnectionResetError:
            logger.error("Connection Reset")
            s.close()
            break
