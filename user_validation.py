import random
from datetime import datetime

if __name__ == "__main__":
    raise SystemExit("This file is not meant to be run directly. Please run the main script called um_members.py")


# The reason for this class is to ensure that we cant view errors from invoked validations
# that are not related to the current validation. (for instance validation a login, and then validation a user creation)
# We could do this by clearing the errors list after each validation, but that is easy to forget,
# and thus would be a bug waiting to happen (and thus a security vulnerability).
#
# Instead, we can create a new instance of this class for each validation session, and then we can be sure that
# the errors are only from the current validation session.


class Validator:
    """
    This class is used to validate user input (things like, username, password, name, age, weight, etc.) \n
    Each validation method returns a boolean value. And it gathers all the errors along the way.
    These errors can be retrieved using the `get_errors` method.
    """

    def __init__(self):
        self.errors: list[str] = []

    def get_errors(self) -> list[str]:
        """
        :return: a list of all the errors that have been recorded in this Validator
        """
        return self.errors

    def is_valid_username(self, input: str) -> bool:
        allowed_chars = "_'."
        if not 8 <= len(input) <= 10:
            # quite a small range, but that is what the assignment requested
            self.errors.append("Username must be between 8 and 10 characters long.")
            return False

        if not input[0].isalpha() and input[0] != "_":
            self.errors.append("Username must start with a letter or an underscore.")
            return False

        for i in input:
            if not i.isalnum() and i not in allowed_chars:
                self.errors.append(
                    "Username must only contain letters, numbers, underscores, apostrophes, and periods."
                )
                return False

        return True

    def is_valid_password(self, input: str) -> bool:
        allowed_chars = "~!@#$%&_-+=`|\\(){}[]:;'<>,.?/"
        if not 12 <= len(input) <= 30:
            self.errors.append("Password must be between 12 and 30 characters long.")
            return False

        has_lower = any(char.islower() for char in input)
        has_upper = any(char.isupper() for char in input)
        has_digit = any(char.isdigit() for char in input)
        has_special = any(char in allowed_chars for char in input)

        if not all([has_lower, has_upper, has_digit, has_special]):
            self.errors.append(
                "Password must contain at least one lowercase, uppercase, digit, and a special character."
            )
            return False

        return True

    def is_valid_name(self, input: str) -> bool:
        if len(input) > 30:
            self.errors.append("Name must be less than 30 characters long.")
            return False

        for i in input:
            if not i.isalpha() or i == " ":
                self.errors.append("Name can only contain letters.")
                return False

        return True

    def is_valid_age(self, input: str) -> bool:
        if not input.isdigit():
            self.errors.append("Age must be a number.")
            return False

        if not 0 < int(input) < 250:
            self.errors.append("Age must be between 0 and 250.")
            return False

        return True

    def is_valid_weight(self, input: str) -> bool:
        if not input.isdigit():
            self.errors.append("Weight must be a number.")
            return False

        if not 0 < int(input) < 500:
            self.errors.append("Weight must be between 0 and 500.")
            return False
        return True


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
