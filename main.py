import handle_database
import actions
import sqlite3


def main():

    con = sqlite3.connect("food_waste.db")
    cur = con.cursor()

    handle_database.create_database(con, cur)

    list_of_barcodes = []
    handle_database.view_foods(con, cur, list_of_barcodes)

    try:
        actions.user_actions(con, cur, list_of_barcodes)

    finally:
        con.close()


if __name__ == "__main__":
    main()
