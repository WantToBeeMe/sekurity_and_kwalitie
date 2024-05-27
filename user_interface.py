import os  # all usages -> checking name of os ; clearing console ; checking if host is PyCharm
import sys  # all usages -> reading single key press ; writing stdout ; flushing stdout

if __name__ == "__main__":
    raise SystemExit("This file is not meant to be run directly. Please run the main script.")

# note that you can change these booleans to False or True to hardcode the value. however, from my experience,
# I have only encountered trouble with PyCharms run terminal (regarding the clear terminal and password field)
#    (since PyCharms uses a virtual terminal. so he's not like the other kids)
COLOR_ENABLED = True
CLEAR_TERMINAL_ENABLED = not ("PYCHARM_HOSTED" in os.environ or "PYCHARM" in os.environ)
PASSWORD_HIDDEN_ENABLED = not ("PYCHARM_HOSTED" in os.environ or "PYCHARM" in os.environ)
# disable only PyCharm ->  not ("PYCHARM_HOSTED" in os.environ or "PYCHARM" in os.environ)


toast: tuple[str, str] = ("", 'white')


def set_toast(message: str, color: str = 'white') -> None:
    """
    sets the toast message that will be displayed at the top of the screen once the screen is cleared again
    :param message:  the message to display
    :param color:  the color of the message (gray, red, green, yellow, blue, magenta, cyan, white)
    """
    global toast
    toast = (message, color)


def print_colored(text, color, only_if_color: bool = False) -> None:
    """
    the text will be printed normally if the COLOR_ENABLED is False
    :param text:  the text to print
    :param color:  the color to print the text in (gray, red, green, yellow, blue, magenta, cyan, white)
    :param only_if_color:  if True, then it will only print this text if the colors are actually enabled.
        if they are not then it will not print anything
    """
    if not COLOR_ENABLED:
        if not only_if_color:
            print(text)
        return

    color_codes = {
        'gray': '\033[90m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m'
    }

    color_code = color_codes.get(color.lower(), '')
    reset_code = '\033[0m'
    print(f"{color_code}{text}{reset_code}")


def clear_terminal() -> None:
    """
    clears the console window using the os module
    if the CLEAR_TERMINAL_ENABLED is False, then it will print a few of new lines instead
    """
    if CLEAR_TERMINAL_ENABLED:
        print("\033c", end="")
        os.system('cls' if os.name == 'nt' else 'clear')
    else:
        print("\n" * 5)

    print("=====================================")
    print_colored(toast[0], toast[1])
    print("=====================================")


def single_select(title: str, options: list[str], allow_back: bool = True) -> int:
    """
    this method will display a menu to the user with a list of options that the user can choose from.
    it will automatically handle pages if those are needed.
    :param title:  the title of the menu
    :param options:  a list of strings that the user can choose from
    :param allow_back:  if the user should be able to go back
    :return:  the index of the item in the list that the user selected or if the user selected back, it returns -1
    """
    max_per_page = 9
    page = 0
    total_pages = (len(options) + (max_per_page - 1)) // max_per_page

    skip_first_iteration_clear = True
    while True:
        start_index = page * max_per_page
        end_index = min(start_index + max_per_page, len(options))

        if skip_first_iteration_clear:
            skip_first_iteration_clear = False
        else:
            clear_terminal()

        print(title)

        for index, opt in enumerate(options[start_index:end_index]):
            print(f"{index + 1}. {opt}")

        print("")
        if total_pages > 1:
            print(f"page {page + 1}/{total_pages}")
            if page > 0:
                print("P. Previous Page")
            else:
                print_colored("P. Previous Page", 'gray', True)
                # if colors are enabled, we can print they option, but grayed out
                # however, if not, we should not print it at all (since we don't want to suggest there is)
            if page < total_pages - 1:
                print("N. Next Page")
            else:
                print_colored("N. Next Page", 'gray', True)
        if allow_back:
            print("B. Back")

        choice = input("\nMake a choice by entering its corresponding character: ").lower()
        set_toast("")
        if allow_back and (choice == 'b' or choice == 'back'):
            return -1
        elif choice.isdigit():
            choice_index = int(choice)
            real_index = choice_index - 1 + start_index
            # we check if the choice index is on this page
            # we check if the real index is in the list
            if 0 < choice_index <= max_per_page and real_index < len(options):
                return real_index

        elif choice == 'p' or choice == 'previous':
            if page <= 0:
                set_toast("You cant go back any further", 'yellow')
            else:
                page -= 1
            continue
        elif choice == 'n' or choice == 'next':
            if page >= total_pages - 1:
                set_toast("You cant go forward any further", 'yellow')
            else:
                page += 1
            continue

        set_toast(f"Invalid input '{choice}'", 'red')


def password_input(prompt: str) -> str:
    """
    this method is like a normal input, however, it will hide the password that the user is typing.
    if the TERMINAL_CONTROL_ENABLED is False, then this hide feature is disabled (and so it becomes a normal input).
    This is because the terminal then does not support it
    :param prompt: the prompt to display to the user
    :return: the password that the user entered
    """
    if not PASSWORD_HIDDEN_ENABLED:
        return input(prompt)

    def read_single_keypress():
        if os.name == 'nt':
            import msvcrt
            return msvcrt.getch().decode('utf-8')
        else:
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

    print(prompt, end='', flush=True)
    password = ""
    while True:
        ch = read_single_keypress()
        if ch in ('\r', '\n'):  # Enter key
            print()  # Move to the next line
            break
        elif ch in ('\b', '\x7f'):  # Backspace key
            if len(password) > 0:
                password = password[:-1]
                # Move cursor back, overwrite with space, move cursor back again
                sys.stdout.write('\b \b')
                sys.stdout.flush()
        else:
            password += ch
            sys.stdout.write('*')
            sys.stdout.flush()
    return password
