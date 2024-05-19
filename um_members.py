import sqlite3
from user_interface import single_select


# IMPORTANT:
#   all the code below is just purely for showing a bit around sql lite.
#   its super duper beta and pretty much everything has to change. 

def setup_database() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    db = sqlite3.connect('mydatabase.db')
    c = db.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')

    return db, c


def main() -> None:
    db, c = setup_database()

    def create_user():
        username = input("Enter username: ")
        password = input("Enter password: ")
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        db.commit()
        print("User created successfully!")

    def view_users():
        c.execute("SELECT * FROM users")
        users = c.fetchall()
        if users:
            for user in users:
                print(f"ID: {user[0]}, Username: {user[1]}, Password: {user[2]}")
        else:
            print("No users found.")

    def delete_user():
        user_id = input("Enter the ID of the user to delete: ")
        c.execute("DELETE FROM users WHERE id=?",
                  (user_id,))  # the comma is required for single values in a tuple. leave it
        db.commit()
        print("User deleted successfully!")

    while True:
        options = ["Create User", "View Users", "Delete User"]
        choice = single_select("User Management System", options)

        if choice == -1:
            break

        if choice == 0:
            create_user()
        elif choice == 1:
            view_users()
        elif choice == 2:
            delete_user()

    db.close()


def single_select_test():
    options = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o"]
    choice = single_select(
        "User Management System", options, True,
        (
            "want to test the sql stuff, go the the last line of um_members and switch the comment there, \n this is "
            "just a single_select test",
            'yellow'))
    if choice == -1:
        print("you chose: Back")
    else:
        print(f"you chose: {options[choice]}")


if __name__ == "__main__":
    single_select_test()
    # main()
