import sqlite3
import time
from classes import User, UserType
from user_validation import is_valid_username, is_valid_password, is_valid_name
from encryption import initialize_keys, encrypt_data, decrypt_data, hash_password

if __name__ == "__main__":
    raise SystemExit("This file is not meant to be run directly. Please run the main script called um_members.py")

_db_connection: sqlite3.Connection = None
_db_cursor: sqlite3.Cursor = None
_current_user: User = None


def get_current_user() -> User:
    return _current_user


def setup_database() -> None:
    """
    This function sets up the database connection and creates the users table if it doesn't exist.
    Calling this method before the rest of the code will ensure that the database is ready to be used.
    """
    global _db_connection, _db_cursor
    initialize_keys()
    _db_connection = sqlite3.connect('unique_meal.db')
    _db_cursor = _db_connection.cursor()
    _db_cursor.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, type TEXT,
                first_name TEXT, last_name TEXT, registration_date TEXT)''')

    _db_cursor.execute('''CREATE TABLE IF NOT EXISTS members
                    (id TEXT PRIMARY KEY, first_name TEXT, last_name TEXT, age TEXT
                    gender TEXT, weight REAL, street TEXT, house_number TEXT, zip TEXT,
                    city TEXT, email TEXT, phone TEXT)''')

     # Delete all users so that the check if there are 0 users is always true (and thus creates a new user)
    _db_cursor.execute("DELETE FROM users")
    _db_connection.commit()


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
                encrypt_data("super_admin"),
                encrypt_data(hash_password("Admin_123?")),
                encrypt_data(f"{UserType.SUPER_ADMIN.value}"),
                encrypt_data("Super"),
                encrypt_data("Admin"),
                encrypt_data(time.strftime("%Y-%m-%d"))
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


# we cant search for the encrtyped data in the db, since the encryption is kinda 
# random since the encryption adds random padding to the input data
# therefore we have this method to get a list of the users so we can filter on those
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
    # we cant search for the encrtyped data in the db, since the encryption is kinda 
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
           
            if user.username == username and user.password_hash == hash_password(password):
                _current_user = user
                return _current_user
            
        self.errors.append(f"Invalid username or password!")
        return None

    @authorize(UserType.ADMIN)
    def get_all_users(self) -> list[User]:
        """
        :return: Returns a list of all users in the database
        """
        return _get_all_users()
  

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
        if not all([first_name_valid,last_name_valid, username_valid, password_valid]):
            if not first_name_valid:
                self.errors.append("First name must be between 2 and 30 characters long and can only contain letters and spaces.")
            if not first_name_valid:
                self.errors.append("Last name must be between 2 and 30 characters long and can only contain letters and spaces.")
            if not username_valid:
                self.errors.append("Username must be between 3 and 20 characters long and can only contain letters, numbers, and underscores.")
            if not password_valid:
                self.errors.append("Password must be between 8 and 20 characters long and must contain at least one uppercase letter, one lowercase letter, one number, and one special character.")
            return

        all_users = _get_all_users()
        if [user for user in all_users if user.name == username]:
            self.errors.append("A user with this username already exists.")
            return  # user already exists

        _db_cursor.execute(
            """
            INSERT INTO users (username, password, type, first_name, last_name, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                encrypt_data(username),
                encrypt_data(hash_password(password)),
                encrypt_data(type.value),
                encrypt_data(first_name),
                encrypt_data(last_name),
                encrypt_data(time.strftime("%Y-%m-%d"))
            )
        )
        _db_connection.commit()
