import sqlite3
import time
from classes import User, UserType
from user_validation import *
from encryption import initialize_keys, encrypt_data_str, decrypt_data, hash_password, compare_passwords
from logging import Logger, LogEntry

if __name__ == "__main__":
    raise SystemExit("This file is not meant to be run directly. Please run the main script called um_members.py")

_db_connection: sqlite3.Connection = None
_db_cursor: sqlite3.Cursor = None
_current_user: User = None
_logger: Logger = None


def get_logs() -> list[LogEntry]:
    return _logger.get_recent_logs()


def get_current_user() -> User:
    return _current_user


def setup_database() -> None:
    """
    This function sets up the database connection and creates the users table if it doesn't exist.
    Calling this method before the rest of the code will ensure that the database is ready to be used.
    """
    global _db_connection, _db_cursor, _logger
    initialize_keys()
    _logger = Logger("./logs.bin")
    _db_connection = sqlite3.connect('unique_meal.db')
    _db_cursor = _db_connection.cursor()
    _db_cursor.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, type TEXT,
                first_name TEXT, last_name TEXT, registration_date TEXT)''')

    _db_cursor.execute('''CREATE TABLE IF NOT EXISTS members
                    (id TEXT PRIMARY KEY, first_name TEXT, last_name TEXT, age TEXT
                    gender TEXT, weight REAL, street TEXT, house_number TEXT, zip TEXT,
                    city TEXT, email TEXT, phone TEXT)''')

    # Check if the users table is empty
    _db_cursor.execute("SELECT COUNT(*) FROM users")

    if _db_cursor.fetchone()[0] == 0:
        # creating the super admin user if there is no user in the database (aka if its newly created)
        _db_cursor.execute(
            """
            INSERT INTO users (username, password, type, first_name, last_name, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                encrypt_data_str("super_admin"),
                encrypt_data_str(hash_password("Admin_123?")),
                encrypt_data_str(f"{UserType.SUPER_ADMIN.value}"),
                encrypt_data_str("Super"),
                encrypt_data_str("Admin"),
                encrypt_data_str(time.strftime("%Y-%m-%d"))
            )
        )
        _db_connection.commit()
        _logger.log("System", "Database setup", "The database has been setup", False)


def close_database() -> None:
    if _db_connection:
        _db_connection.close()


def logout_user() -> None:
    global _current_user
    _logger.log(_current_user.username, "Logged out", "", False)
    _current_user = None


def is_authorized(user_type: UserType) -> bool:
    if not _current_user:
        return False
    return _current_user.type.value >= user_type.value


# note that this error will probably never happen in our application since you will not be able to view options that
# you are not authorized to.
# However, as specially on the web, you cant just assume that people are only using your interface
def authorize(user_type: UserType):
    """
    This is a decorator that will check if the current user is authorized to perform the action.
    If the user is not authorized, then an error will be added to the errors list.
    \n Usage: @authorize(UserType.ADMIN)
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if not is_authorized(user_type):
                self.errors.append("You are not authorized to perform this action.")
                return None
            return func(self, *args, **kwargs)

        return wrapper

    return decorator


# we cant search for the encrypted data in the db, since the encryption is kinda
# random since the encryption adds random padding to the input data
# therefore we have this method to get a list of the users, so we can filter on those
def _get_all_users() -> list[User]:
    """
    This method returns all users, however, it is not ment to be used outside this file
    since its ment to be private (indicated by the underscore in front)
    Instead use `Database().get_all_users()` which returns the same thing,
    but has some validation if the user can actually retrieve it
    """
    _db_cursor.execute("SELECT * FROM users")
    users = _db_cursor.fetchall()

    return_list = []
    # we cant search for the encrypted data in the db, since the encryption is kinda
    # random since the encryption adds random padding to the input data
    for user in users:
        decrypted_user = tuple(decrypt_data(user_data) for user_data in user[1:])
        return_list.append(User(user[0], *decrypted_user))

    return return_list


class Database:
    """
    This class is used to interact with the database. And it gathers all the errors along the way.
    These errors can be retrieved using the `get_errors` method.  Make sure to recreate this object for
    each database action to ensure that the errors are only from the current action.
    """

    def __init__(self):
        self.errors: list[str] = []

    def get_errors(self) -> list[str]:
        """
        :return: a list of all the errors that have been recorded in this Validator
        """
        return self.errors

    def login_user(self, username: str, password: str) -> User:
        """
        :param username:
        :param password:
        :return: Returns a User object if the username and password match, otherwise None
        """
        global _current_user
        if _current_user:
            self.errors.append("You are already logged in.")
            # This error will probably never happen since you will never be shown
            #   the login screen if you are already logged in
            return None

        time.sleep(0.2)  # this query must have a little delay to prevent brute force attacks

        all_users = _get_all_users()
        for user in all_users:
            if user.username == username and compare_passwords(password, user.password_hash):
                _current_user = user
                _logger.log(user.username, "Logged in", "", False)
                _logger.reset_fields()
                return _current_user

        self.errors.append(f"Invalid username or password!")
        if _logger.login_attempts > 2:
            _logger.log("...", "Unsuccessful login",
                        f"username: {username} is used for a login attempt wit a wrong "
                        "password after more than 3 failed attempts",
                        True)
        else:
            _logger.log("...", "Unsuccessful login",
                        f"username: {username} is used for a login attempt wit a wrong password", False)

        _logger.login_attempts += 1
        return None

    @authorize(UserType.ADMIN)
    def get_all_users(self) -> list[User]:
        """
        :return: Returns a list of all users in the database
        """
        return _get_all_users()

    @authorize(UserType.CONSULTANT)
    def create_member(self, member_id: str, first_name: str, last_name: str, age: str, gender: str, weight: str,
                      street: str, house_number: str, zip_code: str, city: str, email: str, phone: str) -> None:
        first_name_valid = is_valid_name(first_name)
        last_name_valid = is_valid_name(last_name)
        age_valid = is_valid_age(age)
        gender_valid = is_valid_gender(gender)
        weight_valid = is_valid_weight(weight)
        phone_valid = is_valid_phone_number(phone)
        house_number_valid = is_valid_house_number(house_number)
        street_valid = is_valid_street(street)
        zip_code_valid = is_valid_zip_code(zip_code)
        email_valid = is_valid_email(email)
        city_valid = is_valid_city(city)

        if not all([first_name_valid, last_name_valid, age_valid, gender_valid, weight_valid, phone_valid,
                    house_number_valid, street_valid, zip_code_valid, email_valid, city_valid]):
            if not first_name_valid:
                self.errors.append(
                    "First name must be between 2 and 30 characters long and can only contain letters and spaces.")
            if not last_name_valid:
                self.errors.append(
                    "Last name must be between 2 and 30 characters long and can only contain letters and spaces.")
            if not age_valid:
                self.errors.append("Age must be between 0 and 120.")
            if not gender_valid:
                self.errors.append("Gender must be 'M', 'F', or 'O'.")
            if not weight_valid:
                self.errors.append("Weight must be a positive number.")
            if not phone_valid:
                self.errors.append("Phone number must be a valid 10-digit number.")
            if not house_number_valid:
                self.errors.append("House number must be a positive integer.")
            if not street_valid:
                self.errors.append("Street must be between 2 and 50 characters long and can only contain letters,"
                                   " numbers, spaces, and hyphens.")
            if not zip_code_valid:
                self.errors.append("Zip code must be a valid postal code format.")
            if not email_valid:
                self.errors.append("Email must be a valid email address.")
            if not city_valid:
                self.errors.append("City must be a valid city name from the predefined list.")
            _logger.log(_current_user.username, "Failed to create member", "Invalid input data", False)
            return

        _db_cursor.execute(
            """
        INSERT INTO members (id, first_name, last_name, age, gender, weight, street, house_number, zip, city, email, phone)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                encrypt_data_str(member_id),
                encrypt_data_str(first_name),
                encrypt_data_str(last_name),
                encrypt_data_str(age),
                encrypt_data_str(gender),
                encrypt_data_str(str(weight)),
                encrypt_data_str(street),
                encrypt_data_str(house_number),
                encrypt_data_str(zip_code),
                encrypt_data_str(city),
                encrypt_data_str(email),
                encrypt_data_str(phone)
            )
        )

        _db_connection.commit()
        _logger.log(_current_user.username, "Created member", f"Member ID: {member_id}", False)

    @authorize(UserType.ADMIN)
    def create_consultant(self, username: str, password: str, first_name: str, last_name: str) -> None:
        return self._create_user(username, password, UserType.CONSULTANT, first_name, last_name)

    @authorize(UserType.SUPER_ADMIN)
    def create_admin(self, username: str, password: str, first_name: str, last_name: str) -> None:
        return self._create_user(username, password, UserType.ADMIN, first_name, last_name)

    def _create_user(self, username: str, password: str, type: UserType, first_name: str, last_name: str) -> None:
        first_name_valid = is_valid_name(first_name)
        last_name_valid = is_valid_name(last_name)
        username_valid = is_valid_username(username)
        password_valid = is_valid_password(password)
        if not all([first_name_valid, last_name_valid, username_valid, password_valid]):
            if not first_name_valid:
                self.errors.append(
                    "First name must be between 2 and 30 characters long and can only contain letters and spaces.")
            if not first_name_valid:
                self.errors.append(
                    "Last name must be between 2 and 30 characters long and can only contain letters and spaces.")
            if not username_valid:
                self.errors.append("Username must be between 3 and 20 characters long and can only contain letters,"
                                   " numbers, and underscores.")
            if not password_valid:
                self.errors.append("Password must be between 8 and 20 characters long and must contain at least one"
                                   " uppercase letter, one lowercase letter, one number, and one special character.")
            _logger.log(_current_user.username, "Failed to create user",
                        f"username: {username} because of invalid input", False)
            return

        all_users = _get_all_users()
        if [user for user in all_users if user.username == username]:
            self.errors.append("A user with this username already exists.")
            _logger.log(_current_user.username, "Failed to create user",
                        f"username: {username} because it already exists", False)
            return  # user already exists

        _db_cursor.execute(
            """
            INSERT INTO users (username, password, type, first_name, last_name, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                encrypt_data_str(username),
                encrypt_data_str(hash_password(password)),
                encrypt_data_str(type.value),
                encrypt_data_str(first_name),
                encrypt_data_str(last_name),
                encrypt_data_str(time.strftime("%Y-%m-%d"))
            )
        )
        _db_connection.commit()
        _logger.log(_current_user.username, "Created user", f"username: {username}", False)

    def edit_password(self, old_password: str, new_password: str) -> None:
        if not _current_user:
            self.errors.append("You must be logged in to change your password.")
            _logger.log("...", "Failed to change password", "User is not logged in", True)
            return

        if not compare_passwords(old_password, _current_user.password_hash):
            self.errors.append("Incorrect password.")
            if _logger.change_attempts > 2:
                _logger.log(_current_user.username, "Failed to change password",
                            "Old password is incorrect after more than 3 failed attempts", True)
            else:
                _logger.log(_current_user.username, "Failed to change password", "Old password is incorrect", False)
            _logger.change_attempts += 1
            return

        password_valid = is_valid_password(new_password)
        if not password_valid:
            self.errors.append("Password must be between 8 and 20 characters long and must contain at least "
                               "one uppercase letter, one lowercase letter, one number, and one special character.")
            _logger.log(_current_user.username, "Failed to change password", "New password is invalid", False)
            return

        _db_cursor.execute(
            """
            UPDATE users
            SET password = ?
            WHERE id = ?
            """,
            (
                encrypt_data_str(hash_password(new_password)),
                _current_user.id
            )
        )
        _db_connection.commit()
        _logger.log(_current_user.username, "Changed password", "", False)
        _logger.change_attempts = 0
