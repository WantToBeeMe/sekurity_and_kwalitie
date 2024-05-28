import random
from datetime import datetime

def is_valid_username(input: str) -> bool:
    usernameChars = "_'."

    if len(input) > 10:
        return False

    if not input[0].isalpha() and input[0] != "_":
        return False

    for i in input:
        if not i.isalnum() and i not in usernameChars:
            return False

    return True


def is_valid_password(input: str) -> bool:
    passwordChars = "~!@#$%&_-+=`|\\(){}[]:;'<>,.?/"

    if len(input) < 12 or len(input) > 30:
        return False

    hasLower = False
    hasUpper = False
    hasDigit = False
    hasSpecial = False
    for i in input:
        if not i.isalnum() and i not in passwordChars:
            return False

        if i.isalpha():
            if i == i.upper():
                hasUpper = True
            else:
                hasLower = True
        elif i.isdigit():
            hasDigit = True
        elif i in passwordChars:
            hasSpecial = True

    if hasLower and hasUpper and hasDigit and hasSpecial:
        return True

    return False


def is_valid_name(input: str) -> bool:
    if len(input) > 30:
        return False

    for i in input:
        if not i.isalpha() or i == " ":
            return False

    return True


def is_valid_age(input: str) -> bool:
    if len(input) > 3:
        return False

    if not input.isdigit():
        return False

    age = int(input)
    if age < 0 or age > 250:
        return False

    return True


def is_valid_weight(input: str) -> bool:
    if len(input) > 3:
        return False

    if not input.isdigit():
        return False

    weight = int(input)
    if weight < 0 or weight > 500:
        return False

    return True


def generate_user_id() -> str:
    current_year = datetime.now().year
    year_part = str(current_year)[-2:]
    random_part = ''.join(str(random.randint(0,9)) for _ in range(7))

    sum_digits = sum(int(i) for i in year_part + random_part)
    check_digit = sum_digits % 10

    return year_part + random_part + str(check_digit)