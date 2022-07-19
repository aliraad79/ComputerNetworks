import socket
from server import HOST, PORT

token = None


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


def get_and_send_login_info(socket):
    username = get_terminal_input("", [], "Username: ", str)
    password = get_terminal_input("", [], "Password: ", str)
    send_message(socket, f"Login {username} {password}")


def get_and_send_singup_info(socket):
    usertype = get_terminal_input(
        "User Type", ["User", "Admin", "Manager"], input_type=int
    )
    username = get_terminal_input("", [], "Username: ", str)
    password = get_terminal_input("", [], "Password: ", str)
    send_message(socket, f"Signup {username} {password} {usertype}")


def send_file(file_path: str, socket) -> None:
    with open(file_path, "rb") as file:
        while True:
            part_of_file = file.read(1024)
            if not part_of_file:
                break
            socket.sendall(part_of_file)
    socket.sendall(b"FileFinished")


def unstrike_user_routine(socket):
    target_username = get_terminal_input("", [], "username: ", str)
    send_message(socket, f"Unstrike {token} {target_username}")

    response = get_network_response(socket)
    if response == "UnstrikeSuc":
        print("Unstriking User Sucessfull")
    elif response == "UnstrikeFail":
        print("Unstriking User Failed")


def ban_user_routine(socket):
    video_id = get_terminal_input("", [], "Video id: ", int)
    send_message(socket, f"Ban {token} {video_id}")

    response = get_network_response(socket)
    if response == "BanSuc":
        print("Banning video Sucessfull")
    elif response == "BanFail":
        print("Banning video Failed")


def comment_on_video_routine(socket):
    comment = get_terminal_input("", [], "Your Comment: ", str)
    send_message(socket, f"CommentVideo {token} {comment}")

    response = get_network_response(socket)
    if response == "ReactSuc":
        print("Comment Submitted")
    elif response == "ReactFail":
        print("Comment Fail")


def dislike_video_routine(socket):
    video_id = get_terminal_input("", [], "Video id: ", int)
    send_message(socket, f"DisLike {token} {video_id}")

    response = get_network_response(socket)
    if response == "ReactSuc":
        print("DisLike Submitted")
    elif response == "ReactFail":
        print("DisLike Fail")


def like_video_routine(socket):
    video_id = get_terminal_input("", [], "Video id: ", int)
    send_message(socket, f"Like {token} {video_id}")

    response = get_network_response(socket)
    if response == "ReactSuc":
        print("Like Submitted")
    elif response == "ReactFail":
        print("Like Fail")


def upload_file_routine(socket):
    send_message(socket, f"UploadFile")
    video_path = get_terminal_input("", [], "Video Path: ", str)
    send_file(video_path, socket)


def logout_routine(socket):
    global token

    send_message(socket, f"Logout {token}")
    response = get_network_response(socket)
    if response == "LogoutSuc":
        print("Logout Succesfull")
        token = None
    elif response == "LogoutFail":
        print("Logout failed")


def signup_routine(socket):
    global token

    get_and_send_singup_info(socket)
    response = get_network_response(socket).split()
    if response[0] == "SingupSuc":
        print("Signup Succesfull!")
        token = response[1]
    elif response[0] == "SingupFail":
        print("Signup Failed!")


def login_routine(socket):
    global token

    get_and_send_login_info(socket)

    response = get_network_response(socket).split()
    if response[0] == "LoginSuc":
        print("Login Succesfull!")
        token = response[1]
    elif response[0] == "LoginFail":
        print("Login Failed!")


def user_thread(socket):
    global token

    if token:
        inp = get_terminal_input(
            "Welcome To Wetube",
            [
                "Logout",
                "Upload Video",
                "Like video",
                "DisLike video",
                "Comment On video",
                "Ban Video",
                "Unstrike User",
                "GetAllVideos",
            ],
        )

        if inp == 1:
            logout_routine(socket)

        elif inp == 2:
            upload_file_routine(socket)

        # Reacts
        elif inp == 3:
            like_video_routine(socket)
        elif inp == 4:
            dislike_video_routine(socket)
        elif inp == 5:
            comment_on_video_routine(socket)
        # ---------------------------

        elif inp == 6:
            ban_user_routine(socket)
        elif inp == 7:
            unstrike_user_routine(socket)
        elif inp == 8:
            send_message(socket, "GetAllVideos")
            print(get_network_response(socket))

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
