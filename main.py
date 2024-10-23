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



def main():

    con = sqlite3.connect("food_waste_new.db")
    cur = con.cursor()

    handle_database.create_database(con, cur)

    user_id = 0
    
    while user_id < 1:
        username = input("Enter username: ")
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


if __name__ == "__main__":
    main()
