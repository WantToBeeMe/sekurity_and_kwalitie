import time
from database import get_current_user, setup_database, close_database, Database, logout_user
from component_library import single_select, password_input, set_toast, clear_terminal, set_multiple_toasts
from classes import UserType


def main():
    setup_database()
    set_toast("Welcome to the Unique Meal App!", "green")

    while True:
        clear_terminal()
        current_user = get_current_user()
        if not current_user:
            startup_menu()
        elif current_user.type == UserType.CONSULTANT:
            consultant_menu()
        elif current_user.type == UserType.ADMIN:
            admin_menu()
        elif current_user.type == UserType.SUPER_ADMIN:
            super_admin_menu()
        else:
            logout("Invalid user type!", "red")


# =================== #
#        MENUS        #
# =================== #

def startup_menu():
    options = ["Login", "Exit"]
    option_index = single_select("Main Menu", options, allow_back=False)

    if option_index == 0:
        clear_terminal()
        login()
    elif option_index == 1:
        # we don't have to close db here, it will be done in the final block
        exit(0)


def consultant_menu():
    options = ["Add members","Logout"]
    option_index = single_select("Main Menu", options, allow_back=False)
    if option_index == 1:
        logout("Goodbye!", "yellow")
    else:
        set_toast("Invalid option!", "red")

def admin_menu():
    options = ["Add members","Logout"]
    option_index = single_select("Main Menu", options, allow_back=False)
    if option_index == 1:
        logout("Goodbye!", "yellow")
    else:
        set_toast("Invalid option!", "red")

def super_admin_menu() -> None:
    options = ["View all Users", "Register new consultant", "Logout"]
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


# =================== #
#   THE OTHER STUFF   #
# =================== #

def login():
    username = input("Username: ")
    password = password_input("Password: ")
    # we don't have to validate the input since if the input is not allowed,
    # then it's not in the db anyway and will return a invalid login anyway
    db = Database()
    current_user = db.login_user(username, password)
    if current_user:
        set_toast(f"Welcome {current_user.username}!", "green")
    else:
        set_multiple_toasts(db.get_errors(), "red")


def logout(toast_message: str, toast_color: str) -> None:
    logout_user()  # resetting current user in the database context/module
    set_toast(toast_message, toast_color)
    clear_terminal()
    time.sleep(0.5)  # to ensure the user sees the goodbye message
    set_toast("Welcome to the Unique Meal App!", "green")


def view_all_users() -> None:
    db = Database()
    users = db.get_all_users()
    if users is None:
        set_multiple_toasts(db.get_errors(), "red")
        return

    options = [
        f"{user.username} ({user.first_name} {user.last_name}) {user.get_role_name()} "
        for user in users
    ]
    single_select("All Users - (Username, Full Name, Type)", options, item_interactable=False)


def register_new_consultant() -> None:
    first_name = input("First name: ")
    last_name = input("Last name: ")
    username = input("Username: ")
    password = password_input("Password: ")

    db = Database()
    db.create_consultant(username, password, first_name, last_name)
    if any(db.get_errors()):
        set_multiple_toasts(db.get_errors(), "red")
    else:
        set_toast(f"Consultant registered successfully! ({username})", "green")


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
