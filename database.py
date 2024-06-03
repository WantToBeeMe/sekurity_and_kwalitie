import sqlite3
import time
import hashlib
from classes import *

if __name__ == "__main__":
    raise SystemExit("This file is not meant to be run directly. Please run the main script called um_members.py")

_db_connection: sqlite3.Connection = None
_db_cursor: sqlite3.Cursor = None
_current_user: User = None


def get_current_user() -> User:
    return _current_user


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def setup_database() -> None:
    """
    This function sets up the database connection and creates the users table if it doesn't exist.
    Calling this method before the rest of the code will ensure that the database is ready to be used.
    """
    global _db_connection, _db_cursor
    _db_connection = sqlite3.connect('unique_meal.db')
    _db_cursor = _db_connection.cursor()
    _db_cursor.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, type INTEGER,
                first_name TEXT, last_name TEXT, registration_date DATE)''')

    _db_cursor.execute('''CREATE TABLE IF NOT EXISTS members
                    (id TEXT PRIMARY KEY, first_name TEXT, last_name TEXT, age INTEGER
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
                "super_admin",
                hash_password("Admin_123?"),
                UserType.SUPER_ADMIN.value,
                "Super",
                "Admin",
                time.strftime("%Y-%m-%d")
            )
        )
        _db_connection.commit()


def close_database() -> None:
    if _db_connection:
        _db_connection.close()


def logout_user() -> None:
    global _current_user
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
        _db_cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                           (username, hash_password(password)))
        user_row = _db_cursor.fetchone()
        if user_row:
            _current_user = User(*user_row)
            return _current_user

        self.errors.append("Invalid username or password!")
        return None

    @authorize(UserType.ADMIN)
    def get_all_users(self) -> list[User]:
        """
        :return: Returns a list of all users in the database
        """
        _db_cursor.execute("SELECT * FROM users")
        return [User(*user_row) for user_row in _db_cursor.fetchall()]

    @authorize(UserType.ADMIN)
    def create_consultant(self, username: str, password: str, first_name: str, last_name: str) -> None:
        return self._create_user(username, password, UserType.CONSULTANT, first_name, last_name)

    @authorize(UserType.SUPER_ADMIN)
    def create_admin(self, username: str, password: str, first_name: str, last_name: str) -> None:
        return self._create_user(username, password, UserType.ADMIN, first_name, last_name)

    def _create_user(self, username: str, password: str, type: UserType, first_name: str, last_name: str) -> None:
        _db_cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if _db_cursor.fetchone():
            self.errors.append("A user with this username already exists.")
            return  # user already exists

        _db_cursor.execute(
            """
            INSERT INTO users (username, password, type, first_name, last_name, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                hash_password(password),
                type.value,
                first_name,
                last_name,
                time.strftime("%Y-%m-%d")
            )
        )
        _db_connection.commit()
