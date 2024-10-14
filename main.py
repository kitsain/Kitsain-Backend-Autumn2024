import sqlite3
import datetime


def create_database(con, cur):

    cur.execute("CREATE TABLE IF NOT EXISTS food_waste ("
                "barcode INTEGER PRIMARY KEY,"
                "food TEXT NOT NULL,"
                "expiry_date INTEGER)")
    con.commit()


def add_food(con, cur, barcode, food, expiry_date):

    cur.execute("INSERT INTO food_waste VALUES (?, ?, ?)",
                (barcode, food, expiry_date))
    con.commit()


def remove_food(con, cur, barcode):

    cur.execute("DELETE FROM food_waste WHERE barcode = ?", (barcode,))
    con.commit()


def view_foods(con, cur, list_of_barcodes):

    cur.execute("SELECT * FROM food_waste")
    waste_data = cur.fetchall()

    for barcode_tuple in waste_data:
        barcode = barcode_tuple[0]
        if barcode not in barcode_tuple:
            list_of_barcodes.append(barcode)

    if waste_data:
        print("Foods in the database:")
        for waste in waste_data:
            expiry_date_str = waste[2]
            expiry_date_obj = datetime.datetime.strptime(expiry_date_str,
                                                         "%Y-%m-%d %H:%M:%S")
            formatted_expiry_date = expiry_date_obj.strftime("%d.%m.%Y")

            print(f"Barcode: {waste[0]} | Food: {waste[1]} | Expiry Date:"
                  f" {formatted_expiry_date}")

    else:
        print("No foods in the database!")
    con.commit()


def main():

    con = sqlite3.connect("food_waste.db")
    cur = con.cursor()

    create_database(con, cur)

    list_of_barcodes = []

    view_foods(con, cur, list_of_barcodes)

    try:
        while True:
            choice = input("Add (a), remove (r), view (v) or quit (q): ")
            if choice == 'a' or choice == 'A':
                get_food = input("Add barcode, food and expiry date divided by "
                                 "space and food put into \" \": ")
                try:
                    parts = get_food.split()

                    barcode = parts[0]
                    food = ' '.join(parts[1:-1])
                    expiry_date = parts[-1]

                    barcode_to_int = int(barcode)

                    if barcode_to_int in list_of_barcodes:
                        print(f"Barcode {barcode} already used! Choose another "
                              f"barcode.")
                        continue

                    else:
                        expiry_date = expiry_date.strip()
                        expiry_date_obj = datetime.datetime.strptime(
                            expiry_date, "%d.%m.%Y")

                        add_food(con, cur, barcode, food, expiry_date_obj)
                        list_of_barcodes.append(barcode_to_int)

                except ValueError:
                    print("Please provide the food details in the correct "
                          "format: barcode \"food\" expiry_date")
                    continue

            elif choice == 'r' or choice == 'R':
                get_food_barcode = input("Input food barcode you wish to "
                                         "remove: ")
                try:
                    barcode_to_int = int(get_food_barcode)

                    if barcode_to_int in list_of_barcodes:
                        remove_food(con, cur, get_food_barcode)
                        list_of_barcodes.remove(barcode_to_int)

                    else:
                        print(f"Barcode {barcode_to_int} was not found!")
                        continue

                except ValueError:
                    print("Please provide the food barcode in the correct "
                          "format: ")
                    continue

            elif choice == 'v' or choice == 'V':
                view_foods(con, cur, list_of_barcodes)

            elif choice == 'q' or choice == 'Q':
                break

            else:
                print("Invalid choice, please try again.")

    finally:
        con.close()


if __name__ == "__main__":
    main()
