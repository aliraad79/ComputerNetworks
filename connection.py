import socket
import pickle
from enum import Enum
from time import sleep

from server import HOST, PORT

token = None
rule = None


class Rules(Enum):
    USER = 1
    ADMIN = 2
    MANAGER = 3


def get_terminal_input(
    msg, options, get_input_message="Enter your choice: ", input_type=int
):
    if msg != "":
        print(msg)
    for counter, i in enumerate(options):
        print(f"\t{1 + counter}. {i}")
    while True:
        try:
            return input_type(input(get_input_message).strip())
        except ValueError:
            print("Not valid choice")


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
    print("Sending ..........")
    with open(file_path, "rb") as file:
        while True:
            part_of_file = file.read(1024)
            if not part_of_file:
                break
            socket.sendall(part_of_file)
    sleep(1)
    socket.sendall(b"VideoFinished")


def unstrike_user_routine(socket):
    target_username = get_terminal_input("", [], "username: ", str)
    send_message(socket, f"Unstrike {token} {target_username}")

    response = get_network_response(socket)
    if response == "UnstrikeSuc":
        print("Unstriking User Sucessfull")
    elif response == "UnstrikeFail":
        print("Unstriking User Failed")


def ban_user_routine(socket):
    video_name = get_terminal_input("", [], "Video name: ", str)
    send_message(socket, f"Ban {token} {video_name}")

    response = get_network_response(socket)
    if response == "BanSuc":
        print("Banning video Sucessfull")
    elif response == "BanFail":
        print("Banning video Failed")


def comment_on_video_routine(socket):
    video_name = get_terminal_input("", [], "Video name: ", str)
    comment = get_terminal_input("", [], "Your Comment: ", str)
    send_message(socket, f"CommentVideo {token} {video_name} {comment}")

    response = get_network_response(socket)
    if response == "ReactSuc":
        print("Comment Submitted")
    elif response == "ReactFail":
        print("Comment Fail")


def dislike_video_routine(socket):
    video_id = get_terminal_input("", [], "Video name: ", str)
    send_message(socket, f"DisLike {token} {video_id}")

    response = get_network_response(socket)
    if response == "ReactSuc":
        print("DisLike Submitted")
    elif response == "ReactFail":
        print("DisLike Fail")


def like_video_routine(socket):
    video_id = get_terminal_input("", [], "Video name: ", str)
    send_message(socket, f"Like {token} {video_id}")

    response = get_network_response(socket)
    if response == "ReactSuc":
        print("Like Submitted")
    elif response == "ReactFail":
        print("Like Fail")


def upload_file_routine(socket):
    video_path = get_terminal_input("", [], "Video Path: ", str)
    send_message(socket, f"UploadVideo {token} {video_path.split('/')[0]}")
    response = get_network_response(socket)
    if response == "Upload":
        send_file(video_path, socket)
    elif response == "UploadFail":
        print("Uploading Video failed")


def approve_admin_routine(socket):
    username = get_terminal_input("", [], "Username: ", str)
    send_message(socket, f"App {token} {username}")
    response = get_network_response(socket)
    if response == "AppSuc":
        print(f"Approved {username}")
    elif response == "AppFail":
        print(f"Can't Approve {username}")


def new_ticket_routine(socket):
    text = get_terminal_input("", [], "Your Complain: ", str)
    send_message(socket, f"NewTicket {token} {text}")
    response = get_network_response(socket)
    if response == "NewTicketSuc":
        print(f"Ticket Created")
    elif response == "NewTicketFail":
        print(f"Creating ticket has counter error")


def answer_ticket_routine(socket):
    ticket_id = get_terminal_input("", [], "ticket_id: ", int)
    text = get_terminal_input("", [], "Your Comment on ticket: ", str)
    send_message(socket, f"AnswerTicket {token} {ticket_id} {text}")
    response = get_network_response(socket)
    if response == "AnswerTicketSuc":
        print(f"New Comment Added")
    elif response == "AnswerTicketFail":
        print(f"Answering ticket has counter error")


def change_ticket_state_routine(socket):
    ticket_id = get_terminal_input("", [], "ticket_id: ", int)
    state = get_terminal_input("Choose State", ["New", "Pending", "Solved", "Closed"])
    send_message(socket, f"ChangeTicketState {token} {ticket_id} {state}")
    response = get_network_response(socket)
    if response == "ChangeTicketStateSuc":
        print(f"Ticket State Changed")
    elif response == "ChangeTicketStateFail":
        print(f"changing ticket state has counter error")


def see_all_tickets_routine(socket):
    send_message(socket, f"GetTickets {token} ")
    data = s.recv(1024)

    if data.startswith(b"GetTicketsSuc"):
        pickle_data = data[len("GetTicketsSuc ") :]

        target_data = pickle.loads(pickle_data)
        for i in target_data:
            print(i)
    elif data.startswith(b"GetTicketsFail"):
        print(f"getting all tickets has counter error")


def logout_routine(socket):
    global token, rule

    send_message(socket, f"Logout {token}")
    response = get_network_response(socket)
    if response == "LogoutSuc":
        print("Logout Succesfull")
        rule = token = None
    elif response == "LogoutFail":
        print("Logout failed")


def signup_routine(socket):
    global token, rule

    get_and_send_singup_info(socket)
    response = get_network_response(socket).split()
    if response[0] == "SingupSuc":
        print("Signup Succesfull!")
        token = response[1]
        rule = Rules(int(response[2]))
    elif response[0] == "SingupFail":
        print("Signup Failed!")


def login_routine(socket):
    global token, rule

    send_login_info(socket)

    response = get_network_response(socket).split()
    if response[0] == "LoginSuc":
        print("Login Succesfull!")
        token = response[1]
        rule = Rules(int(response[2]))

    elif response[0] == "LoginFail":
        print("Login Failed!")


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
            "New Ticket",
            "Answer Ticket",
            "See all my Tickets",
            "Change Ticket State",
            "Logout",
            "Disconnect",
            # add label
            # view video
        ],
    )
    if inp == 1:
        ban_user_routine(socket)
    elif inp == 2:
        unstrike_user_routine(socket)
    elif inp == 3:
        new_ticket_routine(socket)
    elif inp == 4:
        answer_ticket_routine(socket)
    elif inp == 5:
        see_all_tickets_routine(socket)
    elif inp == 6:
        change_ticket_state_routine(socket)
    elif inp == 7:
        logout_routine(socket)
    elif inp == 8:
        socket.close()
        exit()


def user_menu(socket):
    inp = get_terminal_input(
        "Welcome To Wetube",
        [
            "Upload Video",
            # view video
            "Like video",
            "DisLike video",
            "Comment On video",
            "New Ticket",
            "Answer Ticket",
            "See all my Tickets",
            "GetAllVideos",
            "Logout",
            "Disconnect",
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
            print("Connection Reset")
            s.close()
            break
