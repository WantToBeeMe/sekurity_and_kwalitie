import random
import re
from datetime import datetime

if __name__ == "__main__":
    raise SystemExit("This file is not meant to be run directly. Please run the main script called um_members.py")

"""
All validation functions are coded in a way such that they always return false unless all conditions are met.
This way we whitelist only the correct inputs.
"""

CITY_LIST = ["Amsterdam", "Rotterdam", "Utrecht", "Eindhoven", "Tilburg", "Groningen", "Breda", "Apeldoorn",
             "Nijmegen", "Haarlem"]
GENDER_LIST = ["Male", "Female", "Other", "Prefer not to say"]


def is_valid_email(input: str) -> bool:
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, input):
        return True
    return False


def is_valid_city(input: str) -> bool:
    return input in CITY_LIST


def is_valid_username(input: str) -> bool:
    allowed_chars = "_'."
    valid_length = 8 <= len(input) <= 10
    if not valid_length:
        return False  # we return early since the length can be 0, and will cause an error in the next checks
    valid_start_char = input[0].isalpha() or input[0] == "_"
    valid_chars = all(i.isalnum() or i in allowed_chars for i in input)

    if all([valid_length, valid_start_char, valid_chars]):
        return True

    return False


def is_valid_password(input: str) -> bool:
    allowed_chars = "~!@#$%&_-+=`|\\(){}[]:;'<>,.?/"

    valid_length = 12 <= len(input) <= 30
    has_lower = any(char.islower() for char in input)
    has_upper = any(char.isupper() for char in input)
    has_digit = any(char.isdigit() for char in input)
    has_special = any(char in allowed_chars for char in input)

    if all([has_lower, has_upper, has_digit, has_special, valid_length]):
        return True
    return False


def is_valid_name(input: str) -> bool:
    valid_length = 2 < len(input) < 30
    vaild_chars = all(i.isalpha() or i == " " for i in input)

    if all([valid_length, vaild_chars]):
        return True
    return False


def is_valid_age(input: str) -> bool:
    is_digit = input.isdigit()
    valid_age = False
    if is_digit:
        valid_age = 0 < int(input) < 250

    if all([is_digit, valid_age]):
        return True
    return False


def is_valid_weight(input: str) -> bool:
    is_digit = input.isdigit()
    valid_amount = False
    if is_digit:
        valid_amount = 0 < int(input) < 500

    if all([is_digit, valid_amount]):
        return True

    # "Weight must be a number between 0 and 500."
    return False


def is_valid_phone_number(input: str) -> bool:
    is_digit = input.isdigit()
    valid_length = len(input) == 8

    if all([is_digit, valid_length]):
        return True
    return False


def is_valid_house_number(input: str) -> bool:
    is_valid_length = 0 < len(input) < 5
    is_valid = [i.isdigit() for i in input[0:-1]]
    is_valid_last = input[-1].isalnum()

    if all([is_valid_length, all(is_valid), is_valid_last]):
        return True
    return False


def is_valid_street(input: str) -> bool:
    valid_length = 2 < len(input) < 30
    valid_chars = all(i.isalnum() or i == " " for i in input)
    if all([valid_length, valid_chars]):
        return True
    return False


def is_valid_zip_code(input: str) -> bool:
    valid_length = len(input) == 6
    is_valid_digits = False
    is_valid_chars = False
    if valid_length:
        is_valid_digits = all(i.isdigit() for i in input[0:4])
        is_valid_chars = input[-2:].isalpha()

    if all([valid_length, is_valid_digits, is_valid_chars]):
        return True

    return False


def is_valid_gender(input: str) -> bool:
    return input in GENDER_LIST


def generate_user_id() -> str:
    """
    This method is used to generate a unique user id for a new member
    :return: stringifies user id
    """
    current_year = datetime.now().year
    year_part = str(current_year)[-2:]
    random_part = ''.join(str(random.randint(0, 9)) for _ in range(7))
    # Theoretically a random_part could be generated that is already in use,
    # However, this is what the assignment requested so therefor it is implemented as such.
    # A better way would be to use the current time in milliseconds, since that would always be unique.

    sum_digits = sum(int(i) for i in year_part + random_part)
    check_digit = sum_digits % 10

    return year_part + random_part + str(check_digit)
