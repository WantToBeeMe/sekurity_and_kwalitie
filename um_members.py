import time
from database import (get_current_user, setup_database, close_database, Database, logout_user,
                      get_logs, log_risk_detected)
from component_library import (paginated_single_select, password_input, set_toast, clear_terminal, set_multiple_toasts,
                               COLOR_ENABLED, COLOR_CODES, column_based_single_select)
from classes import UserType
from user_validation import CITY_LIST, GENDER_LIST


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
    red = COLOR_CODES['red'] if COLOR_ENABLED else ''
    reset = COLOR_CODES['end'] if COLOR_ENABLED else ''
    options = ["Login", f"{red}Exit{reset}"]

    option_index = column_based_single_select("Main Menu", options, column_count=1)

    if option_index == 0:
        login()
    elif option_index == 1:
        # we don't have to close db here, it will be done in the final block
        exit(0)


def consultant_menu():
    red = COLOR_CODES['red'] if COLOR_ENABLED else ''
    reset = COLOR_CODES['end'] if COLOR_ENABLED else ''
    options = [f"{red}Logout{reset}", "Edit my password", "Add new member", "Edit a member", "Search for a member"]
    option_index = column_based_single_select("Main Menu", options)

    if option_index == 0:  # logout
        logout("Goodbye!", "yellow")
    elif option_index == 1:  # edit password
        edit_my_password()
    elif option_index == 2:  # add new member
        add_new_member()
    elif option_index == 3:  # update a member
        set_toast("not implemented [update a member]", "blue")
    elif option_index == 4:  # search for a member
        set_toast("not implemented [search for a member]", "blue")
    else:
        set_toast("Invalid option!", "red")


def admin_menu():
    red = COLOR_CODES['red'] if COLOR_ENABLED else ''
    reset = COLOR_CODES['end'] if COLOR_ENABLED else ''
    log_star = f"{COLOR_CODES['red' if log_risk_detected() else 'green']}*{reset}" if COLOR_ENABLED else ''
    options = [f"{red}Logout{reset}", "Edit my password", "Add new member", "Edit a member", "Delete a member",
               "Search for a member",  # note that the consultant can NOT delete a member
               "View all users", "Register new consultant", "Edit a consultant", "Delete a consultant",
               "Reset a consultant's password", "Make a backup", "Restore a backup", f"View logs {log_star}"]
    # editing and deleting can maybe be combined
    option_index = column_based_single_select("Main Menu", options)

    if option_index == 0:  # logout
        logout("Goodbye!", "yellow")
    elif option_index == 1:  # edit password
        edit_my_password()
    elif option_index == 2:  # add new member
        add_new_member()
    elif option_index == 3:  # update a member
        set_toast("not implemented [update a member]", "blue")
    elif option_index == 4:  # delete a member
        set_toast("not implemented [delete a member]", "blue")
    elif option_index == 5:  # search for a member
        set_toast("not implemented [search for a member]", "blue")
    elif option_index == 6:  # view all users
        view_all_users()
    elif option_index == 7:  # register new consultant
        register_new_user(UserType.CONSULTANT)
    elif option_index == 8:  # edit a consultant
        set_toast("not implemented [edit a consultant]", "blue")
    elif option_index == 9:  # delete a consultant
        set_toast("not implemented [delete a consultant]", "blue")
    elif option_index == 10:  # reset a consultant's password
        set_toast("not implemented [reset a consultant's password]", "blue")
    elif option_index == 11:  # make a backup
        set_toast("not implemented [make a backup]", "blue")
    elif option_index == 12:  # restore a backup
        set_toast("not implemented [restore a backup]", "blue")
    elif option_index == 13:  # view logs
        view_logs()
    else:
        set_toast("Invalid option!", "red")


def super_admin_menu() -> None:
    red = COLOR_CODES['red'] if COLOR_ENABLED else ''
    reset = COLOR_CODES['end'] if COLOR_ENABLED else ''
    log_star = f"{COLOR_CODES['red' if log_risk_detected() else 'green']}*{reset}" if COLOR_ENABLED else ''
    options = [f"{red}Logout{reset}", "Edit my password", "Add new member", "Edit a member", "Delete a member",
               "Search for a member",  # note that the consultant can NOT delete a member
               "View all users", "Register new consultant", "Edit a consultant", "Delete a consultant",
               "Reset a consultant's password", "Register new admin", "Edit an admin", "Delete an admin",
               "Reset an admins password",
               "Make a backup", "Restore a backup", f"View logs {log_star}"]
    # editing and deleting can maybe be combined
    option_index = column_based_single_select("Main Menu", options)

    if option_index == 0:  # logout
        logout("Goodbye!", "yellow")
    elif option_index == 1:  # edit my password
        edit_my_password()
    elif option_index == 2:  # add new member
        add_new_member()
    elif option_index == 3:  # update a member
        set_toast("not implemented [update a member]", "blue")
    elif option_index == 4:  # delete a member
        set_toast("not implemented [delete a member]", "blue")
    elif option_index == 5:  # search for a member
        set_toast("not implemented [search for a member]", "blue")
    elif option_index == 6:  # view all users
        view_all_users()
    elif option_index == 7:  # register new consultant
        register_new_user(UserType.CONSULTANT)
    elif option_index == 8:  # edit a consultant
        set_toast("not implemented [edit a consultant]", "blue")
    elif option_index == 9:  # delete a consultant
        set_toast("not implemented [delete a consultant]", "blue")
    elif option_index == 10:  # reset a consultant's password
        set_toast("not implemented [reset a consultant's password]", "blue")
    elif option_index == 11:  # register new admin
        register_new_user(UserType.ADMIN)
    elif option_index == 12:  # edit an admin
        set_toast("not implemented [edit an admin]", "blue")
    elif option_index == 13:  # delete an admin
        set_toast("not implemented [delete an admin]", "blue")
    elif option_index == 14:  # reset an admins password
        set_toast("not implemented [reset an admins password]", "blue")
    elif option_index == 15:  # make a backup
        set_toast("not implemented [make a backup]", "blue")
    elif option_index == 16:  # restore a backup
        set_toast("not implemented [restore a backup]", "blue")
    elif option_index == 17:  # view logs
        view_logs()
    else:
        set_toast("Invalid option!", "red")


# =================== #
#   THE OTHER STUFF   #
# =================== #


def login():
    clear_terminal()
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


def edit_my_password() -> None:
    clear_terminal()
    old_password = password_input("Old password: ")
    new_password = password_input("New password: ")
    confirm_password = password_input("Confirm new password: ")
    if new_password != confirm_password:
        set_toast("Passwords do not match!", "red")
        return

    db = Database()
    db.edit_password(old_password, new_password)
    if any(db.get_errors()):
        set_multiple_toasts(db.get_errors(), "red")
    else:
        set_toast("Password changed successfully!", "green")


def view_all_users() -> None:
    clear_terminal()
    db = Database()
    users = db.get_all_users()
    if users is None:
        set_multiple_toasts(db.get_errors(), "red")
        return

    options = [
        f"{user.username} ({user.first_name} {user.last_name}) {user.get_role_name()} "
        for user in users
    ]
    paginated_single_select("All Users - (Username, Full Name, Type)", options, item_interactable=False)


def view_logs() -> None:
    logs = get_logs()

    red = green = white = gray = end = ''
    if COLOR_ENABLED:
        red, green, white, gray, end = (
            COLOR_CODES['red'], COLOR_CODES['green'], COLOR_CODES['white'], COLOR_CODES['gray'], COLOR_CODES['end']
        )
    header = f"{white}ID | yyyy-mm-dd hh:mm:ss | {'Username':<11}  {'Description':<30} suspicious{end}"
    header += "\n"+('-' * len(header))

    if log_risk_detected():
        set_toast("Risk detected in logs!", "red")
    else:  # this flag was not a requirement, however, it is really easy to do and adds to the usability of the system
        set_toast("No risk detected in logs!", "green")

    humanized_logs = []
    for log in reversed(logs):  # we want to start from the most recent log
        suspicious_text =f"{red}Risk{end}" if log.suspicious == "True" else f"{green}Safe{end}"
        main_part = (f"{gray}{log.id.zfill(3)}{white}| {gray}{log.date} {log.time} {white}| "
                     f"{log.username:<11.11}  {log.description:<30}{suspicious_text:>4}{end}")
        if log.additional_info:
            main_part += f"\n   |{'':>21}| {gray}{log.additional_info}{end}"
        humanized_logs.append(main_part)

    clear_terminal()
    paginated_single_select(header, humanized_logs, item_interactable=False, persist_toast=True)

# =================== #
# ACCOUNT MANAGEMENT  #
# =================== #


def register_new_user(role: UserType) -> None:
    clear_terminal()
    first_name = input("First name: ")
    last_name = input("Last name: ")
    username = input("Username: ")
    password = password_input("Password: ")

    db = Database()
    if role == UserType.ADMIN:
        db.create_admin(username, password, first_name, last_name)
    elif role == UserType.CONSULTANT:
        db.create_consultant(username, password, first_name, last_name)
    else:
        return
    if any(db.get_errors()):
        set_multiple_toasts(db.get_errors(), "red")
    else:
        set_toast(f"Consultant registered successfully! ({username})", "green")


def add_new_member() -> None:
    gray = COLOR_CODES['gray'] if COLOR_ENABLED else ''

    set_toast("step 1/4", "yellow")
    clear_terminal()
    print("Personal information:")
    first_name = input("First name: ")
    last_name = input("Last name: ")
    age = input("Age: ")
    weight = input("Weight: ")

    set_toast(f"step 2/4 {gray}{first_name} {last_name}", "yellow")
    clear_terminal()
    gender = GENDER_LIST[column_based_single_select("Gender:", GENDER_LIST, persist_toast=True)]

    set_toast(f"step 3/4 {gray}{first_name} {last_name} ({gender})", "yellow")
    clear_terminal()
    print("Contact information: ")

    email = input("Email: ")
    phone_number = input("Phone: +31-6- (only last 8 digits):")
    street = input("Street: ")
    house_number = input("House number: ")
    zip_code = input("Zip code: ")

    set_toast(f"step 4/4 {gray}{first_name} {last_name} ({gender}) {email}/{phone_number}", "yellow")
    clear_terminal()
    city_name = CITY_LIST[column_based_single_select("City:", CITY_LIST, persist_toast=True)]

    db = Database()
    db.create_member(first_name, last_name, age, gender, weight, street,
                     house_number, zip_code, city_name, email, phone_number)

    if any(db.get_errors()):
        set_multiple_toasts(db.get_errors(), "red")
    else:
        set_toast(f"Member created successfully! ({first_name} {last_name})", "green")


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
