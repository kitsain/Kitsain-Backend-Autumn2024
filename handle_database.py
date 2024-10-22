import format


def create_database(con, cur):
    """
    Creates a database if it is not created already.
    :param con: Connection to the database
    :param cur: Makes queries to the database possible
    :return: Returns to the call function
    """

    cur.execute("CREATE TABLE IF NOT EXISTS food_waste ("
                "barcode INTEGER PRIMARY KEY,"
                "food TEXT NOT NULL,"
                "expiry_date INTEGER,"
                "ecoscore_grade TEXT,"
                "ecoscore_score INTEGER,"
                "gluten_free BOOLEAN,"
                "keywords TEXT)")
    con.commit()


def add_food(con, cur, barcode, food, expiry_date, ecoscore_grade,
             ecoscore_score, gluten_free, keywords):
    """
    Adds food to the database.
    :param con: Connection to the database
    :param cur: Makes queries to the database possible
    :param barcode: Barcode to identify products
    :param food: Food name
    :param expiry_date: The day the food expires
    :param ecoscore_grade: Ecoscore as a letter
    :param ecoscore_score: Ecoscore as a number
    :param gluten_free: is product gluten free
    :param keywords: Details about the food
    :return: Returns to the call function
    """

    cur.execute("INSERT INTO food_waste VALUES (?, ?, ?, ?, ?, ?, ?)",
                (barcode, food, expiry_date, ecoscore_grade, ecoscore_score, gluten_free,
                 keywords))
    con.commit()


def remove_food(con, cur, barcode):
    """
    Removes food from the database.
    :param con: Connection to the database
    :param cur: Makes queries to the database possible
    :param barcode:
    :return: Returns to the call function
    """

    cur.execute("DELETE FROM food_waste WHERE barcode = ?", (barcode,))
    con.commit()


def view_foods(con, cur, list_of_barcodes):
    """
    Shows the content of the database.
    :param con: Connection to the database
    :param cur: Makes queries to the database possible
    :param list_of_barcodes:
    :return: Returns to the call function
    """

    cur.execute("SELECT * FROM food_waste")
    waste_data = cur.fetchall()

    for barcode_tuple in waste_data:
        barcode = barcode_tuple[0]
        if barcode not in list_of_barcodes:
            list_of_barcodes.append(barcode)

    if waste_data:
        format.print_foods_data(waste_data)

    else:
        print("No foods in the database!")
    con.commit()
