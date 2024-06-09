import os  # all usages -> checking name of os ; clearing console
import sys  # all usages -> reading single key press ; writing stdout ; flushing stdout
import math

# IMPORTANT:
#   This file can be considered the components' library. It contains all the reusable code snippets
#   that are used to create nice user interfaces. if this where to be a real web application, then a user could
#   modify the interface to submit other data that is invalid.
#   So you should still validate the data coming out of these methods

if __name__ == "__main__":
    raise SystemExit("This file is not meant to be run directly. Please run the main script called um_members.py")

COLOR_ENABLED = True
CLEAR_TERMINAL_ENABLED = True
COLOR_CODES = {
    'gray': '\033[90m', 'red': '\033[91m',
    'green': '\033[92m', 'yellow': '\033[93m',
    'blue': '\033[94m', 'magenta': '\033[95m',
    'cyan': '\033[96m', 'white': '\033[97m',
    'end': '\033[0m'
}

ASSUMED_PAGE_WIDTH = 90
# this variable does not force any string to be 80 characters long, so any longer string will still be displayed
# however, if something has to be calculated based on the width of the page, then this is the assumed width

_toast: list[tuple[str, str]] = [("", 'white')]


def set_all_toasts(messages: list[tuple[str, str]]) -> None:
    """
    sets multiple toast messages that will be displayed at the top of the screen once the screen is cleared again
    :param messages:  a list of tuples with the message and the color of the message
    """
    global _toast
    _toast = messages


def set_multiple_toasts(messages: list[str], color: str = 'gray') -> None:
    """
    sets multiple toast messages that will be displayed at the top of the screen once the screen is cleared again
    :param messages:  the messages to display
    :param color:  the color of the message (gray, red, green, yellow, blue, magenta, cyan, white)
    """
    # limits shown errors to the last three, otherwise the toast is getting really ugly. no real other reason
    global _toast
    _toast = [(m, color) for m in messages]


def set_toast(message: str, color: str = 'gray') -> None:
    """
    sets the toast message that will be displayed at the top of the screen once the screen is cleared again
    :param message:  the message to display
    :param color:  the color of the message (gray, red, green, yellow, blue, magenta, cyan, white)
    """
    global _toast
    _toast = [(message, color)]


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

    color_code = COLOR_CODES.get(color.lower(), '')
    print(f"{color_code}{text}{COLOR_CODES['end']}")


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

    print('=' * ASSUMED_PAGE_WIDTH)
    for t in _toast[-4:]:
        print_colored(*t)
    print('=' * ASSUMED_PAGE_WIDTH)


def column_based_single_select(title: str, options: list[str], column_count: int = 2,
                               persist_toast: bool = False) -> int:
    """
    this method will display a menu to the user with a list of options that the user can choose from.
    it will automatically put the options in columns.
    :param title:  the title of the menu
    :param options:  a list of strings that the user can choose from
    :param column_count:  the amount of columns that the options should be displayed in
    :param persist_toast:  if the toast you created before this single select should persist at refresh
    :return:  the index of the item in the list that the user selected or if the user selected back, it returns -1
    """

    persisted_toasts: list[tuple[str, str]] = _toast.copy() if persist_toast else []
    width_per_column = ASSUMED_PAGE_WIDTH // column_count
    amount_of_rows = math.ceil(len(options) / column_count)

    stringified_options = [f"[{index + 1}] {opt}" for index, opt in enumerate(options)]

    skip_first_iteration_clear = True
    while True:
        if skip_first_iteration_clear:
            skip_first_iteration_clear = False
        else:
            clear_terminal()
        print(title)

        for row_index in range(amount_of_rows):
            current_row: list[str] = []
            for column_index in range(column_count):
                index = row_index + column_index * amount_of_rows
                if index >= len(options):
                    break
                selected_option = stringified_options[index]
                total_option_width = width_per_column
                # in this loop there is a color correction. (since these are characters and thus have a with.
                # but they won't be displayed so are not actually a width, therefore we need to correct for that)
                for color_code in COLOR_CODES.values():
                    # no check needed here for COLOR_ENABLED, since then there should not even be color here
                    total_option_width += selected_option.count(color_code) * color_code.__len__()
                current_row.append(selected_option.ljust(total_option_width)[:total_option_width])
            print(''.join(current_row))

        choice = input("\nMake a choice by entering its corresponding character: ").lower()
        if choice.isdigit():
            choice_index = int(choice)
            real_index = choice_index - 1
            if 0 <= real_index < len(options):
                set_toast("")
                return real_index

        toast = persisted_toasts.copy()
        toast.append((f"Invalid input '{choice}'", 'red'))
        set_all_toasts(toast)


def paginated_single_select(title: str, options: list[str], allow_back: bool = True,
                            item_interactable: bool = True, persist_toast: bool = False) -> int:
    """
    this method will display a menu to the user with a list of options that the user can choose from.
    it will automatically handle pages if those are needed.
    :param item_interactable: if the user is allowed to select an item from the list
     (if True, will force to allow_back=True)
    :param title:  the title of the menu
    :param options:  a list of strings that the user can choose from
    :param allow_back:  if the user should be able to go back
    :param persist_toast:  if the toast you created before this single select should persist at refresh
    :return:  the index of the item in the list that the user selected or if the user selected back, it returns -1
    """
    if not item_interactable:
        allow_back = True  # if the items are not selectable, then the user should be able to go back

    persisted_toasts: list[tuple[str, str]] = _toast.copy() if persist_toast else []

    def set_select_toast(message: str, color: str = 'white'):
        toasts = persisted_toasts.copy()
        if message or not toasts:
            toasts.append((message, color))
        set_all_toasts(toasts)

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
            if item_interactable:
                print(f"[{index + 1}] {opt}")
            else:
                print(opt)

        print("")
        if total_pages > 1:
            print(f"page {page + 1}/{total_pages}")
            if page > 0:
                print("[P] Previous Page")
            else:
                print_colored("[P] Previous Page", 'gray', True)
                # if colors are enabled, we can print they option, but grayed out
                # however, if not, we should not print it at all (since we don't want to suggest there is)
            if page < total_pages - 1:
                print("[N] Next Page")
            else:
                print_colored("[N] Next Page", 'gray', True)
        if allow_back:
            print("[B] Back")

        choice = input("\nMake a choice by entering its corresponding character: ").lower()
        set_select_toast("")
        if allow_back and (choice == 'b' or choice == 'back'):
            set_toast("")
            return -1
        elif choice.isdigit():
            choice_index = int(choice)
            real_index = choice_index - 1 + start_index
            # we check if the choice index is on this page
            # we check if the real index is in the list
            if 0 < choice_index <= max_per_page and real_index < len(options):
                if item_interactable:
                    return real_index
                set_select_toast("The items in the list cant be interacted with.", 'red')
                continue

        elif choice == 'p' or choice == 'previous':
            if page <= 0:
                set_select_toast("You are already on the first page, you cant go back any further", 'yellow')
            else:
                page -= 1
            continue
        elif choice == 'n' or choice == 'next':
            if page >= total_pages - 1:
                set_select_toast("You are already on the last page, you cant go forward any further", 'yellow')
            else:
                page += 1
            continue

        set_select_toast(f"Invalid input '{choice}'", 'red')


def password_input(prompt: str) -> str:
    """
    this method is like a normal input, however, it will hide the password that the user is typing.
    :param prompt: the prompt to display to the user
    :return: the password that the user entered
    """

    # if "PYCHARM_HOSTED" in os.environ or "PYCHARM" in os.environ:
    #     # if you are in PyCharm virtual terminal, we can't use the hide password feature
    #     return input(prompt)

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
