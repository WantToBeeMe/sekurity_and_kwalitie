from database import *
from component_library import single_select, password_input, set_toast, clear_terminal
from classes import *
from user_validation import *

current_user: User = None


def main():
    setup_database()
    set_toast("Welcome to the Unique Meal App!", "green")

    while True:
        clear_terminal()

        # logout("Goodbye!", "yellow")
        if not current_user:
            startup_menu()
            continue

        if current_user.type == CONSULTANT:
            ...
        elif current_user.type == ADMIN:
            ...
        elif current_user.type == SUPER_ADMIN:
            super_admin_menu()
        else:
            logout("Invalid user type!", "red")


def startup_menu():
    options = ["Login", "Exit"]
    option_index = single_select("Main Menu", options, allow_back=False)

    if option_index == 0:
        clear_terminal()
        login()
    elif option_index == 1:
        # we don't have to close db here, it will be done in the final block
        exit(0)


def login():
    global current_user
    username = input("Username: ")
    password = password_input("Password: ")

    current_user = get_user(username, password)
    if current_user:
        set_toast(f"Welcome {current_user.username}!", "green")
    else:
        set_toast("Invalid username or password!", "red")


def logout(toast_message: str, toast_color: str) -> None:
    global current_user
    current_user = None
    set_toast(toast_message, toast_color)
    clear_terminal()
    time.sleep(0.5)  # to ensure the user sees the goodbye message
    set_toast("Welcome to the Unique Meal App!", "green")


def super_admin_menu() -> None:
    options = ["View all Users", "Register new consultant", "Exit"]
    option_index = single_select("Main Menu", options, allow_back=False)

    if option_index == 0:
        clear_terminal()
        view_all_users()
    elif option_index == 1:
        clear_terminal()
        register_new_consultant()
    elif option_index == 2:
        logout("Goodbye!", "yellow")
    else:
        # this should never happen since the select only returns a number. but
        set_toast("Invalid option!", "red")


def view_all_users() -> None:
    users = get_all_users()

    options = [
        f"{user.username} ({user.first_name} {user.last_name}) "
        f"{'Consultant' if user.type == CONSULTANT else 'Admin' if user.type == ADMIN else 'Super Admin'}"
        for user in users
    ]
    single_select("All Users - (Username, Full Name, Type)", options)


def register_new_consultant() -> None:
    first_name = input("First name: ")
    last_name = input("Last name: ")
    username = input("Username: ")
    password = password_input("Password: ")

    validator = Validator()
    if not all([validator.is_valid_name(first_name), validator.is_valid_name(last_name),
                validator.is_valid_username(username), validator.is_valid_password(password)]):
        # limits shown errors to the last two, otherwise the toast is getting really ugly
        errors = validator.get_errors()[-3:]
        set_toast("\n".join(errors), "red")
        return

    create_user(username, password, CONSULTANT, first_name, last_name)

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
        close_database()
        # ensures that the database connection is always closed
        # even if an exception occurs
