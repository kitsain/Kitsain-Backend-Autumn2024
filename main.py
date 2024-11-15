import handle_database
import actions
import sqlite3


def main():

    con = sqlite3.connect("commerce_data.db")
    cur = con.cursor()

    handle_database.create_database(con, cur)

    user_id = 0
    
    while user_id < 1:
        username = input("\nEnter username: ")
        
        # Username doesn't exist:
        if not handle_database.username_exists(cur, username):
            ans = ''
            while ans != 'y' and ans != 'Y' and ans != 'n' and ans != 'N':
                ans = input(f"Username '{username}' does not exist\nCreate "
                            f"new user? [y/n]: ")
            
            if ans == 'y' or ans == 'Y':
                password = input("Enter new password: ")
                email = input("Enter your email: ")
                role = input("Enter role ['user', 'shopkeeper', 'admin']: ")

                if handle_database.add_user(con, cur, username, password, email, role):
                    print(f"User '{username}' added successfully!\nPlease log in with your username and password.")
                else:
                    print("Failed to add new user. Please try again later.")
        
        # Username exists:
        else:
            password = input("Enter password: ")
            
            user_id = handle_database.authenticate_user(cur, username, password)
            
            if user_id == -1:
                print("Username not found!")
            if user_id == -2:
                print("Incorrect password!")

    try:
        actions.user_actions(con, cur, user_id)

    finally:
        con.close()
        
    print("Application closed successfully!")


if __name__ == "__main__":
    main()