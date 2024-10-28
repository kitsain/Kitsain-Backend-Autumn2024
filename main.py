import handle_database
import actions
import sqlite3


def authenticate_user(cur, username, password):
    """
    Authenticates a user based on the provided username and password.
    
    Parameters:
    - cur: SQLite cursor object
    - username: The username provided by the user
    - password: The password provided by the user (in plain text)
    
    Returns:
    - user_id if authentication is successful
    - -1 if the username is not found
    - -2 if the password is incorrect
    """
    
    try:
        # Check if the username exists in the database
        cur.execute('SELECT user_id, password FROM user WHERE username = ?', (username,))
        result = cur.fetchone()
        
        if result:
            user_id, stored_password = result
            # Compare the provided password with the stored password
            if password == stored_password:
                return user_id  # Successful authentication
            else:
                return -2  # Incorrect password
        else:
            return -1  # Username not found

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return -1  # In case of any database error, return -1 (as if user not found)


def username_exists(cur, username):
    """
    Checks if a username already exists in the user table.
    
    Parameters:
    - cur: SQLite cursor object
    - username: The username to check
    
    Returns:
    - True if the username exists
    - False if the username does not exist
    """
    
    try:
        # Query the user table to check if the username exists
        cur.execute('SELECT 1 FROM user WHERE username = ?', (username,))
        result = cur.fetchone()
        
        # Return True if a row was found, False otherwise
        return result is not None

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False


def main():

    con = sqlite3.connect("food_waste_new.db")
    cur = con.cursor()

    handle_database.create_database(con, cur)

    user_id = 0
    
    while user_id < 1:
        username = input("\nEnter username: ")
        
        # Username doesn't exist:
        if username_exists(cur, username) == False:
            ans = ''
            while ans != 'y' and ans != 'Y' and ans != 'n' and ans != 'N':
                ans = input(f"Username '{username}' does not exist\nCreate new user? [y/n]:")
            
            if ans == 'y' or ans == 'Y':
                password = input("Enter new password: ")
                email = input("Enter your email: ")
                role = input("Enter role ['user', 'shopkeeper', 'admin']: ")
                
                if handle_database.add_user(con, cur, username, password, email, role):
                    print(f"User '{username}' added successfully!\nPlease login with your username and password.")
                else:
                    print("Failed to add new user. Please try again later.")
        
        # Username exists:
        else:
            password = input("Enter password: ")
            
            user_id = authenticate_user(cur, username, password)
            
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
