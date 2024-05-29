import sqlite3
import time
from sanitize import hash_password
from classes import *

if __name__ == "__main__":
    raise SystemExit("This file is not meant to be run directly. Please run the main script called um_members.py")


_db_connection: sqlite3.Connection = None
_db_cursor: sqlite3.Cursor = None


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
    count = _db_cursor.fetchone()[0]

    # If the users table is empty, insert a hardcoded initial user
    if count == 0:
        initial_username = "super_admin"
        initial_password = hash_password("Admin_123?")
        _db_cursor.execute("INSERT INTO users (username, password, type) VALUES (?, ?, ?)",
                           (initial_username, initial_password, SUPER_ADMIN))
        _db_connection.commit()


def close_database() -> None:
    if _db_connection:
        _db_connection.close()


def get_user(username: str, password: str) -> User:
    """
    :param username:
    :param password:
    :return: Returns a User object if the username and password match, otherwise None
    """
    time.sleep(0.2)  # this query must have a little delay to prevent brute force attacks
    _db_cursor.execute("SELECT * FROM users WHERE username=? AND password=?",
                       (username, hash_password(password)))
    user_row = _db_cursor.fetchone()
    if user_row:
        return User(*user_row)
    return None


def get_all_users() -> list[User]:
    """
    :return: Returns a list of all users in the database
    """
    _db_cursor.execute("SELECT * FROM users")
    return [User(*user_row) for user_row in _db_cursor.fetchall()]


def create_user(username: str, password: str, type: int, first_name: str, last_name: str) -> None:
    _db_cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    if _db_cursor.fetchone():
        return # user already exists

    _db_cursor.execute(
        """
        INSERT INTO users (username, password, type, first_name, last_name, registration_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            hash_password(password),
            CONSULTANT,
            first_name,
            last_name,
            time.strftime("%Y-%m-%d")
        )
    )
    _db_connection.commit()
