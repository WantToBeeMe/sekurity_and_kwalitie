import sqlite3

# IMPORTANT:
#   all the code below is just purely for showing a bit around sql lite.
#   its super duper beta and pretty much everything has to change. 

db = sqlite3.connect('mydatabase.db')
c = db.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')

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
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    db.commit()
    print("User deleted successfully!")

while True:
    print("\nUser Management System")
    print("1. Create User")
    print("2. View Users")
    print("3. Delete User")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ")

    if choice == '1':
        create_user()
    elif choice == '2':
        view_users()
    elif choice == '3':
        delete_user()
    elif choice == '4':
        break
    else:
        print("Invalid choice. Please try again.")

db.close()