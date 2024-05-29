import sqlite3
import time
from user_interface import single_select, password_input, set_toast, clear_terminal
from classes import *
from user_validation import *
from sanitize import hash_password

db: sqlite3.Connection = None
c: sqlite3.Cursor = None
current_user: User = None


def setup_database() -> None:
    global db, c
    db = sqlite3.connect('unique_meal.db')
    c = db.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, type INTEGER,
                first_name TEXT, last_name TEXT, registration_date DATE)''')

    c.execute('''CREATE TABLE IF NOT EXISTS members
                    (id TEXT PRIMARY KEY, first_name TEXT, last_name TEXT, age INTEGER
                    gender TEXT, weight REAL, street TEXT, house_number TEXT, zip TEXT,
                    city TEXT, email TEXT, phone TEXT)''')

    # Check if the users table is empty
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]

    # If the users table is empty, insert a hardcoded initial user
    if count == 0:
        initial_username = "super_admin"
        initial_password = hash_password("Admin_123?")
        c.execute("INSERT INTO users (username, password, type) VALUES (?, ?, ?)",
                  (initial_username, initial_password, SUPER_ADMIN))
        db.commit()


def main() -> None:
    global db, c
    setup_database()

    set_toast("Welcome to the Unique Meal App!", "green")
    while True:
        clear_terminal()

        if not current_user:
            login()
        else:
            if current_user.type == CONSULTANT:
                ...
            elif current_user.type == ADMIN:
                ...
            elif current_user.type == SUPER_ADMIN:
                super_admin_menu()
            else:
                set_toast("Invalid user type!", "red")
                login()


def login() -> None:
    global current_user
    username = input("Username: ")
    password = password_input("Password: ")

    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    user = c.fetchone()
    time.sleep(0.2)

    if user:
        current_user = User(*user)
        set_toast(f"Welcome {current_user.username}!", "green")
    else:
        set_toast("Invalid username or password!", "red")


def super_admin_menu() -> None:
    global current_user
    options = ["View all Users", "Register new consultant", "Exit"]
    option_index = single_select("Main Menu", options, allow_back=False)

    if option_index == 0:
        view_all_users()
    elif option_index == 1:
        register_new_consultant()
    elif option_index == 2:
        current_user = None


def view_all_users() -> None:
    global db, c
    c.execute("SELECT * FROM users")
    users = [User(*user) for user in c.fetchall()]

    clear_terminal()
    options = [
        f"{user.username} ({user.first_name} {user.last_name}) "
        f"{'Consultant' if user.type == CONSULTANT else 'Admin' if user.type == ADMIN else 'Super Admin'}"
        for user in users
    ]
    single_select("All Users - (Username, Full Name, Type)", options)


def register_new_consultant() -> None:
    global db, c
    first_name = input("First name: ")
    last_name = input("Last name: ")
    username = input("Username: ")
    password = password_input("Password: ")

    if not all([is_valid_name(first_name), is_valid_name(last_name),
                is_valid_username(username), is_valid_password(password)]):
        set_toast(get_recorded_error(), "red")
        return

    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()

    if user:
        set_toast("Username already exists!", "red")
        return

    c.execute(
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
    db.commit()

    set_toast("Consultant registered successfully!", "green")


if __name__ == "__main__":
    import os  # os is only used in this if statement
    if "PYCHARM_HOSTED" in os.environ or "PYCHARM" in os.environ:
        print("This program is not intended to be run in PyCharm's terminal. \n"
              "Using this terminal could open up security vulnerabilities. \n"
              "Please run it in your system's terminal.")
        exit(1)

    try:
        main()
    finally:
        # ensure that the database connection is always closed
        # even if an exception occurs
        if db:
            db.close()
