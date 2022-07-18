import socket
from server import HOST, PORT

is_logged_in = False
username = None


def get_terminal_input(
    msg, options, get_input_message="Enter your choice: ", input_type=int
):
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
    return username


def get_and_send_singup_info(socket):
    usertype = get_terminal_input(
        "User Type", ["User", "Admin", "Manager"], input_type=int
    )
    username = get_terminal_input("", [], "Username: ", str)
    password = get_terminal_input("", [], "Password: ", str)
    send_message(socket, f"Signup {username} {password} {usertype}")
    return username


def send_file(file_path: str, socket) -> None:
    with open(file_path, "rb") as file:
        while True:
            part_of_file = file.read(1024)
            if not part_of_file:
                break
            socket.sendall(part_of_file)
    socket.sendall(b"FileFinished")


def user_thread(socket):
    global is_logged_in, username

    if is_logged_in:
        inp = get_terminal_input("Welcome To Wetube", ["Logout", "Upload Video"])

        if inp == 1:
            send_message(socket, f"Logout {username}")
            if get_network_response(socket) == "LogoutSuc":
                print("Logout Succesfull")
                is_logged_in = False
                username = None

        elif inp == 2:
            send_message(socket, f"UploadFile")
            video_path = get_terminal_input("", [], "Video Path: ", str)
            send_file(video_path, socket)
    else:
        inp = get_terminal_input("Welcome To Wetube", ["Login", "Signup"])
        if inp == 1:
            _username = get_and_send_login_info(socket)
            if get_network_response(socket) == "LoginSuc":
                print("Login Succesfull!")
                is_logged_in = True
                username = _username

        elif inp == 2:
            _username = get_and_send_singup_info(socket)
            if get_network_response(socket) == "SingupSuc":
                print("Signup Succesfull!")
                is_logged_in = True
                username = _username


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        try:
            user_thread(s)
        except ConnectionResetError:
            print("Connection Reset")
            s.close()
            break
