import os  # we only use this for clearing the console

if __name__ == "__main__":
    raise SystemExit("This file is not meant to be run directly. Please run the main script.")

COLOR_ENABLED = True
CLEAR_ENABLED = True
# IMPORTANT:
#   All the code here is just an idea. I have many questions about the interface.
#   So I will leave it at this for now untill i have answers.

def clear_console():
    print("\033c", end="")
    if CLEAR_ENABLED:
        os.system('cls' if os.name == 'nt' else 'clear')
    else:
        print("\n" * 100)

def print_colored(text, color):
    if not COLOR_ENABLED:
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


# this method returns the index of the item in the list that the user selected
# or if the user selected back, it returns -1
def single_select(title: str, options: list[str], allow_back: bool = True, toast: tuple[str, str] = None) -> int:
    max_per_page = 9
    page = 0
    total_pages = (len(options) + (max_per_page - 1)) // max_per_page

    while True:
        start_index = page * max_per_page
        end_index = min(start_index + max_per_page, len(options))

        clear_console()
        if toast:
            print_colored(toast[0], toast[1])
        print(title)

        for index, opt in enumerate(options[start_index:end_index]):
            print(f"{index + 1}. {opt}")

        print("")
        if total_pages > 1:
            print(f"page {page + 1}/{total_pages}")
            if page > 0:
                print("P. Previous Page")
            elif COLOR_ENABLED:
                print_colored("P. Previous Page", 'gray')
            if page < total_pages - 1:
                print("N. Next Page")
            elif COLOR_ENABLED:
                print_colored("N. Next Page", 'gray')
        if allow_back: print("B. Back")

        choice = input("\nMake a choice by entering its corresponding character: ").lower()

        toast = None
        if allow_back and (choice == 'b' or choice == 'back'):
            return -1
        elif choice.isdigit():
            choice_index = int(choice)
            real_index = choice_index - 1 + start_index
            # we check if the choice index is on this page
            # we check if the real index is in the list
            if choice_index > 0 and choice_index <= max_per_page and real_index < len(options):
                return real_index

        elif choice == 'p' or choice == 'previous':
            if page <= 0:
                toast = ("You cant go back any further", 'yellow')
            else:
                page -= 1
            continue
        elif choice == 'n' or choice == 'next':
            if page >= total_pages - 1:
                toast = ("You cant go forward any further", 'yellow')
            else:
                page += 1
            continue

        toast = (f"Invalid input '{choice}'", 'red')
