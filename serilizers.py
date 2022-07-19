from typing import Tuple


def parse_react_string(input_string: str) -> Tuple[str, str]:
    """
    <req> <token> <video_name>
    """
    splited_string = input_string.split()
    return splited_string[1], splited_string[2]


def parse_login_string(input_string: str) -> Tuple[str, str]:
    """
    <req> <token> <password>
    """
    splited_string = input_string.split()
    return splited_string[1], splited_string[2]

def parse_logout_string(input_string: str) -> Tuple[str]:
    """
    <req> <token>
    """
    splited_string = input_string.split()
    return splited_string[1]


def parse_signup_string(input_string: str) -> Tuple[str, str, str]:
    """
    <req> <token> <password> <usertype>
    """
    splited_string = input_string.split()
    return splited_string[1], splited_string[2], splited_string[3]

def parse_ban_string(input_string: str) -> Tuple[str, str]:
    """
    <req> <token> <video_name>
    """
    splited_string = input_string.split()
    return splited_string[1], splited_string[2]

def parse_unstrike_string(input_string: str) -> Tuple[str, str]:
    """
    <req> <token> <username>
    """
    splited_string = input_string.split()
    return splited_string[1], splited_string[2]

def parse_video_string(input_string: str) -> Tuple[str, str]:
    """
    <req> <token> <video_name>
    """
    splited_string = input_string.split()
    return splited_string[1], splited_string[2]