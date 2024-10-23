import datetime
import get_data
import handle_database


def adding(con, cur, user_id):
    """
    Tries to add the input food to the database. If food with given barcode
    is found from OpenFoodFact, it is added to the database with the
    information provided by OpenFoodFact. Otherwise, food is added to the
    database with information provided by the user. If food is input in
    incorrect form, exception is raised.
    :param con: Connection to the database
    :param cur: Makes queries to the database possible
    :param list_of_barcodes: Contains the used barcodes
    :return: Return to the call function
    """

    get_food = input("Add barcode, food and expiry date divided by space: ")
    try:
        parts = get_food.split()

        barcode = parts[0]
        food = ' '.join(parts[1:-1])
        expiry_date = parts[-1]

        barcode_to_int = int(barcode)

        if barcode_to_int in list_of_barcodes:
            print(f"Barcode {barcode} already used! Choose another "
                  f"barcode.")

        else:
            ecoscore_grade, ecoscore_score, name_en, keywords, status = \
                get_data.get_eco_score(barcode)

            if ecoscore_grade != 'Eco score not found' \
                    and name_en != 'Name not found':

                food = name_en

            expiry_date = expiry_date.strip()
            expiry_date_obj = datetime.datetime.strptime(
                expiry_date, "%d.%m.%Y")
            
            gluten_free = get_data.get_gluten_free(barcode)

            handle_database.add_food(con, cur, barcode, food,
                                     expiry_date_obj, ecoscore_grade,
                                     ecoscore_score, gluten_free, keywords)
            list_of_barcodes.append(barcode_to_int)

            if status == 'product not found':
                print(f"A product \"{food}\" wasn't found from OpenFoodFact "
                      f"with given barcode \"{barcode}\". The given food will "
                      f"be added to the \ndatabase with the information you "
                      f"provided.")
                return

            print(f"A product \"{food}\" was found from OpenFoodFact with "
                  f"given barcode \"{barcode}\" and will be added to the"
                  f" \ndatabase with the information found from OpenFoodFact.")

    except ValueError:
        print("Please provide the food details in the correct "
              "format: barcode food expiry_date")


def removal(con, cur, list_of_barcodes):
    """
    Removes food with input barcode from the database. If food is input in
    incorrect form, exception is raised.
    :param con: Connection to the database
    :param cur: Makes queries to the database possible
    :param list_of_barcodes: Contains the used barcodes
    :return: Returns to the call function
    """

    get_food_barcode = input("Input food barcode you wish to "
                             "remove: ")
    try:
        barcode_to_int = int(get_food_barcode)

        if barcode_to_int in list_of_barcodes:
            handle_database.remove_food(con, cur, get_food_barcode)
            list_of_barcodes.remove(barcode_to_int)

        else:
            print(f"Barcode {barcode_to_int} was not found!")

    except ValueError:
        print("Please provide the food barcode in the correct "
              "format: ")


def user_actions(con, cur, list_of_barcodes):
    """
    Asks user what they want to do.
    :param con: Connection to the database
    :param cur: Makes queries to the database possible
    :param list_of_barcodes: Contains the used barcodes
    :return: Returns to the call function
    """

    while True:
        choice = input("Add (a), remove (r), view (v) or quit (q): ")

        if choice == 'a' or choice == 'A':
            adding(con, cur, list_of_barcodes)

        elif choice == 'r' or choice == 'R':
            removal(con, cur, list_of_barcodes)

        elif choice == 'v' or choice == 'V':
            handle_database.view_foods(con, cur, list_of_barcodes)

        elif choice == 'q' or choice == 'Q':
            break

        else:
            print("Invalid choice, please try again.")
