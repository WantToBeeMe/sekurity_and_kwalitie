import sqlite3
import time
from user_interface import single_select, password_input, set_toast, clear_terminal

# IMPORTANT:
#   all the code below is just purely for showing a bit around sql lite.
#   its super duper beta and pretty much everything has to change. 

db: sqlite3.Connection = None
c: sqlite3.Cursor = None
current_user: tuple[int, str, str] = None  # (id, username, password)


def setup_database() -> None:
    global db, c
    db = sqlite3.connect('unique_meal.db')
    c = db.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')

    # Check if the users table is empty
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]

    # If the users table is empty, insert a hardcoded initial user
    if count == 0:
        initial_username = "admin"
        initial_password = "test"
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (initial_username, initial_password))
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
            daily_business()


def login() -> None:
    global current_user
    username = input("Username: ")
    password = password_input("Password: ")
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    time.sleep(0.2)

    if user:
        current_user = user
        set_toast(f"Welcome {current_user[1]}!", "green")
    else:
        set_toast("Invalid username or password!", "red")


def daily_business() -> None:
    global current_user
    options = ["Create new user", "Exit"]
    option_index = single_select("Main Menu", options, allow_back=False)
    if option_index == 0:
        current_user = None
        set_toast("damm, i did not implement that ... sorry", "yellow")
        clear_terminal()
        time.sleep(1)
        set_toast("Welcome to the Unique Meal App!", "green")
    elif option_index == 1:
        current_user = None
        set_toast("Goodbye!", "yellow")
        clear_terminal()
        time.sleep(1)
        set_toast("Welcome to the Unique Meal App!", "green")


if __name__ == "__main__":
    try:
        main()
    finally:
        # ensure that the database connection is always closed
        # even if an exception occurs
        if db:
            db.close()
