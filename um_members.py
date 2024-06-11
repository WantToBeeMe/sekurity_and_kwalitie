import time
from backend import get_current_user, setup_database, close_database, Database, logout_user
from component_library import (paginated_single_select, password_input, set_toast, clear_terminal, set_multiple_toasts,
                               COLOR_ENABLED, COLOR_CODES, column_based_single_select)
from classes import UserType, Member, User
from validation import CITY_LIST, GENDER_LIST
from encryption import compare_passwords


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
        elif current_user.type == UserType.ADMIN or current_user.type == UserType.SUPER_ADMIN:
            admin_menu()
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
    else:
         set_toast("Invalid option!", "red")



def consultant_menu():
    red = COLOR_CODES['red'] if COLOR_ENABLED else ''
    reset = COLOR_CODES['end'] if COLOR_ENABLED else ''
    options = [f"{red}Logout{reset}", "Reset my password", "View member"]
    option_index = column_based_single_select("Main Menu", options)

    if option_index == 0:  # logout
        logout("Goodbye!", "yellow")
    elif option_index == 1:  # edit password
        edit_my_password()
    elif option_index == 2:  # add / update / search members
        members_index_page()
    else:
        set_toast("Invalid option!", "red")


def admin_menu():
    red = COLOR_CODES['red'] if COLOR_ENABLED else ''
    reset = COLOR_CODES['end'] if COLOR_ENABLED else ''
    # always since these dont obee with the laws of the COLOR_ENABLED flag >:)
    always_green =  COLOR_CODES['green']
    always_red = COLOR_CODES['red']
    always_reset =  COLOR_CODES['end']

    db = Database()
    log_notice =  f"{always_green}No new risks{always_reset}"
    if db.log_risk_detected():
        log_notice = f"{always_red}Unread Risk detected!{always_reset}"

    options = [f"{red}Logout{reset}", "Reset my password", "View member", "View users",
               "Make a backup", "Restore a backup", f"View logs: {log_notice}"]
    # editing and deleting can maybe be combined
    option_index = column_based_single_select("Main Menu", options)

    if option_index == 0:  # logout
        logout("Goodbye!", "yellow")
    elif option_index == 1:  # edit password
        edit_my_password()
    elif option_index == 2:  # add / update / delete / search -> members
        members_index_page()
    elif option_index == 3:  # view / add / update / delete / reset-password -> users (consultants and admins)
        # this method itself will make sure admins and super_admins get there designated options
        users_index_page()
    elif option_index == 4:  # make a backup
        create_backup()
    elif option_index == 5:  # restore a backup
        restore_backup()
    elif option_index == 6:  # view logs
        view_logs()
    else:
        set_toast("Invalid option!", "red")


# =================== #
#    MEMBER RELATED   #
# =================== #

def members_index_page():
    end = COLOR_CODES['end'] if COLOR_ENABLED else ''
    green = COLOR_CODES['green'] if COLOR_ENABLED else ''
    yellow = COLOR_CODES['yellow'] if COLOR_ENABLED else ''
    tried_adding_member = False  # this flag only ensures that if adding a member failed. that it will not overwrite
    # the toast with "no results found" but instead will display the error message from the failed creation

    db = Database()
    members = db.get_all_members()
    if members is None:
        set_multiple_toasts(db.get_errors(), "red")
        return

    header = f"    {'ID':<11.11} {'Full Name':<30.30} {'Age':<4.4} {'Email':<30.30}"
    header += "\n" + ('-' * len(header))
    search_term = ''  # must be able to search on: id, first name, last name, address, email address and phone number
    while True:
        filtered_members = []
        for mem in members:
            matches_search = not search_term
            if search_term:
                matches_search = (search_term.lower() in str(mem.id) or
                                  search_term.lower() in (mem.first_name + " " + mem.last_name).lower() or
                                  search_term.lower() in (mem.street_name + " " + mem.house_number).lower() or
                                  search_term.lower() in mem.email.lower() or
                                  search_term.lower() in mem.zip_code.lower() or
                                  search_term.lower() in mem.phone.lower() or
                                  search_term.lower() in mem.city.lower())

            if matches_search:
                filtered_members.append(mem)

        options = []
        for mem in filtered_members:
            real_name = f"{mem.first_name} {mem.last_name}"
            options.append(f"{str(mem.id):<11.11} {real_name:<30.30} {str(mem.age):<4.4} {mem.email:<30.30}")

        if not options and not tried_adding_member:
            set_toast("No results found!", "red")
        clear_terminal()
        page_result = paginated_single_select(header, options, persist_toast=True, persisted_options={
            'B': "Back",
            "S": f"{yellow}Search{end}",
            "A": f"{green}Add new member{end}",
        })

        tried_adding_member = False
        search_term = ''
        if page_result == -1:
            return
        elif page_result >= 0:
            made_changes = _member_details(filtered_members[page_result])
            # the page does not return here. So we make use of the stack
            # to go back in to this loop after the _view_member function returns
            if made_changes:
                # this boolean is nothing more than a bit of optimization. so it won't do a query if noting changed
                members = db.get_all_members()
        elif page_result == -2:
            clear_terminal()
            search_term = input("Search term: ")
            if search_term:
                set_toast(f"Searching for '{search_term}'", "yellow")
        elif page_result == -3:
            tried_adding_member = True
            success = _add_member()
            if success:
                # this boolean is nothing more than a bit of optimization. so it won't do a query if noting changed
                members = db.get_all_members()


def _member_details(member: Member) -> bool:
    """
    :return: returns True if the member has been updated or deleted. otherwise return false
    """
    end = COLOR_CODES['end'] if COLOR_ENABLED else ''
    yellow = COLOR_CODES['yellow'] if COLOR_ENABLED else ''
    red = COLOR_CODES['red'] if COLOR_ENABLED else ''
    set_toast("")
    clear_terminal()
    print(f"ID: {member.id}")
    print(f"Name: {member.first_name} {member.last_name}")
    print(f"Age: {member.age}")
    print(f"Gender: {member.gender}")
    print(f"Weight: {member.weight}")
    print(f"Address: {member.street_name} {member.house_number}, {member.zip_code} {member.city}")
    print(f"Email: {member.email}")
    print(f"Phone: {member.phone}")

    allowed_to_delete = get_current_user().type == UserType.SUPER_ADMIN or get_current_user().type == UserType.ADMIN
    # note that his boolean only ensures that the option is shown (or not)
    # however, there is also an extra authorization check for all queries. including this delete query
    # meaning that even if someone would get through our cool interface,
    # they would still not be able to delete a member if not authorized

    print(f"\n[E] {yellow}Edit member{end}")
    if allowed_to_delete:
        print(f"[D] {red}Delete member{end}")

    chose = input("\nChose an option or press any key to go back: ")
    if chose.lower() == "e" or chose.lower() == "edit":
        return _edit_member(member)
    if allowed_to_delete and (chose.lower() == "d" or chose.lower() == "delete"):
        return _delete_member(member)
    return False


def _edit_member(member: Member) -> bool:
    """
    :return: returns True if the member has been updated. otherwise it will return false
    """
    gray = COLOR_CODES['gray'] if COLOR_ENABLED else ''
    end = COLOR_CODES['end'] if COLOR_ENABLED else ''
    yellow = COLOR_CODES['yellow'] if COLOR_ENABLED else ''

    def currently(value: any) -> str:
        return f"{gray}currently: {str(value)}{end}"

    set_toast("step 1/4", "yellow")
    clear_terminal()
    print(f"Personal information: {yellow}leave empty to keep current value{end}")
    first_name = input(f"First name {currently(member.first_name)}: ")
    first_name = first_name if first_name else member.first_name
    last_name = input(f"Last name {currently(member.last_name)}: ")
    last_name = last_name if last_name else member.last_name
    age = input(f"Age {currently(member.age)}: ")
    age = age if age else str(member.age)
    weight = input(f"Weight {currently(member.weight)}: ")
    weight = weight if weight else str(member.weight)

    set_toast(f"step 2/4 {gray}{first_name} {last_name}", "yellow")
    clear_terminal()
    gender = GENDER_LIST[column_based_single_select(f"Gender: {currently(member.gender)}", GENDER_LIST,
                                                    persist_toast=True)]

    set_toast(f"step 3/4 {gray}{first_name} {last_name} ({gender})", "yellow")
    clear_terminal()
    print(f"Contact information:  {yellow}leave empty to keep current value{end}")

    email = input(f"Email {currently(member.email)}: ")
    email = email if email else member.email
    phone_number = input(f"Phone: +31-6- (only last 8 digits) {currently(member.phone)}:")
    phone_number = phone_number if phone_number else member.phone
    street = input(f"Street {currently(member.street_name)}: ")
    street = street if street else member.street_name
    house_number = input(f"House number {currently(member.house_number)}: ")
    house_number = house_number if house_number else member.house_number
    zip_code = input(f"Zip code {currently(member.zip_code)}: ")
    zip_code = zip_code if zip_code else member.zip_code

    set_toast(f"step 4/4 {gray}{first_name} {last_name} ({gender}) {email}/{phone_number}", "yellow")
    clear_terminal()
    city_name = CITY_LIST[column_based_single_select(f"City:  {currently(member.city)}", CITY_LIST, persist_toast=True)]

    db = Database()
    db.update_member(member.id, first_name, last_name, age, gender, weight, street,
                     house_number, zip_code, city_name, email, phone_number)

    if any(db.get_errors()):
        set_multiple_toasts(db.get_errors(), "red")
        return False
    else:
        set_toast(f"Member updated successfully! ({first_name} {last_name})", "green")
        return True


def _delete_member(member: Member) -> bool:
    """
    :return:  returns True if you successfully deleted a member. otherwise it will return false
    """
    set_toast("")
    while True:
        clear_terminal()
        print(f"Are you sure you want to delete {member.first_name} {member.last_name}?")
        print("[Y] Yes")
        print("[N] No")
        chose = input("Chose an option: ")
        if chose.lower() == "y" or chose.lower() == "yes":
            db = Database()
            db.delete_member(member.id)
            if any(db.get_errors()):
                set_multiple_toasts(db.get_errors(), "red")
            else:
                set_toast(f"{member.first_name} {member.last_name} deleted successfully!", "green")
                return True
        elif chose.lower() == "n" or chose.lower() == "no":
            set_toast("")
            return False
        set_toast("please enter 'y' or 'n'", "red")


def _add_member() -> bool:
    """
    :return: returns True if the member has been created. otherwise it will return false
    """
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
        return False
    else:
        set_toast(f"Member created successfully! ({first_name} {last_name})", "green")
        return True


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
    db.edit_my_password(old_password, new_password)
    if any(db.get_errors()):
        set_multiple_toasts(db.get_errors(), "red")
    else:
        set_toast("Password changed successfully!", "green")


def view_logs() -> None:
    db = Database()
    logs = db.get_logs()
    if any(db.get_errors()):
        set_multiple_toasts(db.get_errors(), "red")
        return

    red, green, end = (COLOR_CODES['red'], COLOR_CODES['green'], COLOR_CODES['end'] )
    white = gray = ''
    if COLOR_ENABLED:
         white, gray = ( COLOR_CODES['white'], COLOR_CODES['gray'] )
    header = f"{white}ID | yyyy-mm-dd hh:mm:ss | {'Username':<11}  {'Description':<30} suspicious{end}"
    header += "\n" + ('-' * len(header))

    if db.log_risk_detected():
        set_toast("Unread risk detected in logs!", "red")
    else:  # this flag was not a requirement, however, it is really easy to do and adds to the usability of the system
        set_toast("No unread risk detected in logs!", "green")

    humanized_logs = []
    for log in reversed(logs):  # we want to start from the most recent log
        suspicious_text = f"{red}Risk{end}" if log.suspicious == "True" else f"{green}Safe{end}"
        main_part = (f"{gray}{log.id.zfill(3)}{white}| {gray}{log.date} {log.time} {white}| "
                     f"{log.username:<11.11}  {log.description:<30}{suspicious_text:>4}{end}")
        if log.additional_info:
            main_part += f"\n   |{'':>21}| {gray}{log.additional_info}{end}"
        humanized_logs.append(main_part)

    clear_terminal()
    paginated_single_select(header, humanized_logs, item_interactable=False,
                            persist_toast=True, persisted_options={'B': "Back"})


def create_backup() -> None:
    db = Database()
    db.create_backup()
    if any(db.get_errors()):
        set_multiple_toasts(db.get_errors(), "red")
    else:
        set_toast("Backup created successfully!", "green")

def restore_backup() -> None:
    db = Database()
    backups = db.get_backups()
    if any(db.get_errors()):
        set_multiple_toasts(db.get_errors(), "red")
        return

    if not backups:
        set_toast("No backups found!", "red")
        return

    index = paginated_single_select("Select a backup to restore", backups, persist_toast=True, persisted_options={'B': "Back"})
    if index < 0:
        return

    db.apply_backup(backups[index])
    if any(db.get_errors()):
        set_multiple_toasts(db.get_errors(), "red")
    else:
        set_toast("Backup applied successfully!", "green")


# =================== #
#     USER STUFF      #
# =================== #

def users_index_page() -> None:
    green = COLOR_CODES['green'] if COLOR_ENABLED else ''
    end = COLOR_CODES['end'] if COLOR_ENABLED else ''
    db = Database()
    users = db.get_all_users()
    if users is None:
        set_multiple_toasts(db.get_errors(), "red")
        return

    # note that this is ofcourse not the security check. this is only our frontend not providing the option
    # however, even if a user would get around that and send the backend an add admin request,
    # it would still fail since there it will be authenticated
    persisted_options = {'B': "Back"}
    if get_current_user().type == UserType.SUPER_ADMIN:
        persisted_options["C"] = f"{green}Add new consultant{end}"
        persisted_options["A"] = f"{green}Add new admin{end}"
    elif get_current_user().type == UserType.ADMIN:
        persisted_options["C"] = f"{green}Add new consultant{end}"

    header = f"    {'Username':<12.12} {'Full Name':<30.30} {'Role':<11.11}"
    header += "\n" + ('-' * len(header))
    while True:
        options = []
        for user in users:
            real_name = f"{user.first_name} {user.last_name}"
            options.append(f"{user.username:<12.12} {real_name:<30.30} {user.get_role_name()}")

        clear_terminal()
        page_result = paginated_single_select(header, options, persist_toast=True, persisted_options=persisted_options)
        if page_result == -1:
            return
        elif page_result >= 0:
            made_changes = _user_details(users[page_result])
            # the page does not return here. So we make use of the stack
            # to go back in to this loop after the _view_member function returns
            if made_changes:
                # this boolean is nothing more than some optimization. so it won't do a query if noting changed
                users = db.get_all_users()
        elif (page_result == -2 and
              get_current_user().type == UserType.ADMIN or get_current_user().type == UserType.SUPER_ADMIN):

            success = _register_new_user(UserType.CONSULTANT)
            if success:
                # this boolean is nothing more than a bit of optimization. so it won't do a query if noting changed
                users = db.get_all_users()

        elif page_result == -3 and get_current_user().type == UserType.SUPER_ADMIN:
            success = _register_new_user(UserType.ADMIN)
            if success:
                # this boolean is nothing more than a bit of optimization. so it won't do a query if noting changed
                users = db.get_all_users()


def _user_details(user: User) -> bool:
    """
    :return:  returns True if the user has been updated or deleted. otherwise it will return false
    """
    end = COLOR_CODES['end'] if COLOR_ENABLED else ''
    yellow = COLOR_CODES['yellow'] if COLOR_ENABLED else ''
    red = COLOR_CODES['red'] if COLOR_ENABLED else ''
    set_toast("")
    clear_terminal()
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Name: {user.first_name} {user.last_name}")
    print(f"Role: {user.get_role_name()}")
    print(f"Registration date: {user.registration_date}")

    current_user = get_current_user()
    # editable if:
    # - Selected user can not be superAdmin
    # - Current user is superAdmin || (Selected user is consultant and Current user is admin)
    allowed_to_edit = user.type != UserType.SUPER_ADMIN and (
            current_user.type == UserType.SUPER_ADMIN or
            (user.type == UserType.CONSULTANT and current_user.type == UserType.ADMIN)
        )

    if allowed_to_edit:
        print(f"\n[E] {yellow}Edit user{end}")
        print(f"[R] {yellow}Reset password{end}")
        print(f"[D] {red}Delete user{end}")


    chose = input("\nChose an option or press any key to go back: ")
    if allowed_to_edit and (chose.lower() == "e" or chose.lower() == "edit"):
        return _edit_user(user)
    if allowed_to_edit and (chose.lower() == "r" or chose.lower() == "reset"):
        return _reset_users_password(user)
    if allowed_to_edit and (chose.lower() == "d" or chose.lower() == "delete"):
        return _delete_user(user)

    return False


def _edit_user(user: User) -> bool:
    gray = COLOR_CODES['gray'] if COLOR_ENABLED else ''
    end = COLOR_CODES['end'] if COLOR_ENABLED else ''
    yellow = COLOR_CODES['yellow'] if COLOR_ENABLED else ''
    def currently(value: any) -> str:
       return f"{gray}currently: {str(value)}{end}"

    clear_terminal()
    print(f"Updating {user.get_role_name()}: {yellow}leave empty to keep current value{end}")
    first_name = input(f"First name {currently(user.first_name)}: ")
    first_name = first_name if first_name else user.first_name
    last_name = input(f"Last name {currently(user.first_name)}: ")
    last_name = last_name if last_name else user.last_name
    username = input(f"Username {currently(user.username)}: ")
    username = username if username else user.username

    db = Database()
    if user.type == UserType.CONSULTANT:
        db.update_consultant( user.id, first_name, last_name, username)
    if user.type == UserType.ADMIN:
        db.update_admin( user.id, first_name, last_name, username)

    if any(db.get_errors()):
        set_multiple_toasts(db.get_errors(), "red")
        return False
    else:
        set_toast(f"User udated successfully! ({username})", "green")
        return True


def _delete_user(user: User) -> bool:
    while True:
        clear_terminal()
        print(f"Are you sure you want to delete {user.first_name} {user.last_name}?")
        print("[Y] Yes")
        print("[N] No")
        chose = input("Chose an option: ")
        if chose.lower() == "y" or chose.lower() == "yes":
            db = Database()
            if user.type == UserType.CONSULTANT:
                db.delete_consultant(user.id)
            elif user.type == UserType.ADMIN:
                db.delete_admin(user.id)

            if any(db.get_errors()):
                set_multiple_toasts(db.get_errors(), "red")
            else:
                set_toast(f"{user.first_name} {user.last_name} deleted successfully!", "green")
                return True
        elif chose.lower() == "n" or chose.lower() == "no":
            set_toast("")
            return False
        set_toast("please enter 'y' or 'n'", "red")



def _reset_users_password(user: User) -> bool:
    clear_terminal()
    set_toast('')
    your_password = password_input('Your password: ')
    db = Database()
    current_user = get_current_user()

    if not compare_passwords(your_password, current_user.password_hash):
        set_toast('Incorrect password!', 'red')
        return False

    new_password = password_input(f'New password for {user.username}: ')
    confirm_password = password_input('Confirm new password: ')
    if new_password != confirm_password:
        set_toast('Passwords do not match!', 'red')
        return False

    if user.type == UserType.CONSULTANT:
        db.reset_consultant_password(user.id, new_password)
    elif user.type == UserType.ADMIN:
        db.reset_admin_password(user.id, new_password)

    if any(db.get_errors()):
        set_multiple_toasts(db.get_errors(), 'red')
        return False
    else:
        set_toast('Password reset successfully!', 'green')
        return True


def _register_new_user(role: UserType) -> bool:
    set_toast("")
    clear_terminal()
    usertype = "Admin" if role == UserType.ADMIN else "Consultant"
    print(f"Creating new {usertype}:")
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
        return False
    if any(db.get_errors()):
        set_multiple_toasts(db.get_errors(), "red")
        return False
    else:
        set_toast(f"Consultant registered successfully! ({username})", "green")
        return True


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
