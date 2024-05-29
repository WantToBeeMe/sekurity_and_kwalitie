import random
from datetime import datetime

# TODO: This `last_recorded_error` is not definitive ofcourse.
#   This implementation assumes that every error updates the last_recorded_error.
#   But if for some reason we as developers forget that, then it will show the previous error message,
#   which is a vulnerability. So a better implementation would be to have a Validator class, `validator = Validator()`
#   and be able to call `validator.validate_username(username)` and then you can do `validator.get_last_error()`
#   This way if we forget to set an error, then it will just return "" ,  which is just dumb, but not a vulnerability.


last_recorded_error = ""


def get_recorded_error() -> str:
    """
    This will return the last error message that was recorded by the validation functions.
    This then can be used to display the error message to the user.
    Note that if there are no errors in a long time, that the old previous error message will still be stored.
    But this should not matter, since you would only display the error message if the validation function returns False.
    """
    return last_recorded_error


def is_valid_username(input: str) -> bool:
    global last_recorded_error
    allowed_chars = "_'."
    if 8 >= len(input) > 10:
        last_recorded_error = "Username must be between 8 and 10 characters long."
        return False

    if not input[0].isalpha() and input[0] != "_":
        last_recorded_error = "Username must start with a letter or an underscore."
        return False

    for i in input:
        if not i.isalnum() and i not in allowed_chars:
            last_recorded_error = "Username must only contain letters, numbers, underscores, apostrophes, and periods."
            return False

    return True


def is_valid_password(input: str) -> bool:
    global last_recorded_error
    allowed_chars = "~!@#$%&_-+=`|\\(){}[]:;'<>,.?/"
    if len(input) < 12 or len(input) > 30:
        last_recorded_error = "Password must be between 12 and 30 characters long."
        return False

    has_lower = any(char.islower() for char in input)
    has_upper = any(char.isupper() for char in input)
    has_digit = any(char.isdigit() for char in input)
    has_special = any(char in allowed_chars for char in input)

    if not all([has_lower, has_upper, has_digit, has_special]):
        last_recorded_error = "Password must contain at least one lowercase, uppercase, digit, and a special character."
        return False

    return True


def is_valid_name(input: str) -> bool:
    global last_recorded_error
    if len(input) > 30:
        last_recorded_error = "Name must be less than 30 characters long."
        return False

    for i in input:
        if not i.isalpha() or i == " ":
            last_recorded_error = "Name can only contain letters."
            return False

    return True


def is_valid_age(input: str) -> bool:
    global last_recorded_error
    if not input.isdigit():
        last_recorded_error = "Age must be a number."
        return False

    if not 0 < int(input) < 250:
        last_recorded_error = "Age must be between 0 and 250."
        return False

    return True


def is_valid_weight(input: str) -> bool:
    global last_recorded_error
    if not input.isdigit():
        last_recorded_error = "Weight must be a number."
        return False

    if not 0 < int(input) < 500:
        last_recorded_error = "Weight must be between 0 and 500."
        return False
    return True


def generate_user_id() -> str:
    current_year = datetime.now().year
    year_part = str(current_year)[-2:]
    random_part = ''.join(str(random.randint(0, 9)) for _ in range(7))

    sum_digits = sum(int(i) for i in year_part + random_part)
    check_digit = sum_digits % 10

    return year_part + random_part + str(check_digit)
