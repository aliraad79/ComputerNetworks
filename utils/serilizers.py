from typing import Tuple


def parse_one_part_string(input_string: str) -> Tuple[str]:
    """
    <req> <part_1>
    """
    splited_string = input_string.split()
    return splited_string[1]


def parse_two_part_string(input_string: str) -> Tuple[str, str]:
    """
    <req> <part_1> <part_2>
    """
    splited_string = input_string.split()
    return splited_string[1], str.join("-", splited_string[2:])


def parse_two_part_input(input_string: str) -> Tuple[str, str]:
    """
    <req> <part_1> <part_2>
    """
    splited_string = input_string.split()
    return splited_string[1], splited_string[2]


def parse_three_part_string(input_string: str) -> Tuple[str, str, str]:
    """
    <req> <part_1> <part_2> <part_3>
    """
    splited_string = input_string.split()
    return splited_string[1], splited_string[2], splited_string[3]
