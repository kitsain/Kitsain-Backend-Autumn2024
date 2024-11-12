import datetime
import shlex
import get_data
import handle_database


def adding(con, cur, user_id, list_of_barcodes=None):
    """
    Tries to add the input food to the database. If food with given barcode
    is found from OpenFoodFact, it is added to the database with the
    information provided by OpenFoodFact. Otherwise, food is added to the
    database with information provided by the user. If food is input in
    incorrect form, exception is raised.
    :param user_id:
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

        # NEEDS TO BE MODIFIED!!
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

def print_help():
    print("""
    Notes:
    ------
    - Command parameters containing spaces (e.g. long names) should be given 
    inside quotes
    - Optional unknown command parameters should be given as NULL
    
    Available Commands:
    -------------------
    ap [product_name] [weight_g] [volume_l] [barcode] [category] [esg_score] 
    [co2_footprint] [brand] [sub_brand] [parent_company] [information_links] 
    [gluten_free]
        - Add a product to the product table.
    rp [barcode]
        - Remove the latest version of a product by barcode (admin only).
    ac [product_id] [shop_id] [price] [discount_price] 
    [waste_discount_percentage] [valid_from_date] [valid_to_date]
        - Add a price entry.
    rc [price_id] [shop_id]
        - Remove a price entry by price_id (admin or shopkeeper).
    as [store_name] [store_chain] [location_address] [location_gps]
        - Add a new shop.
    rs [shop_id]
        - Remove a shop by shop_id.
    ask [shop_id]
        - Assign current user as shopkeeper to a shop.
    rsk [shop_id]
        - Remove current user as shopkeeper from a shop.
        
    print users
        - Print all users and their information.
    print shops
        - Print all shops and assigned shopkeepers.
    print foods
        - View all latest versions of products.
    print prices
        - Print all latest prices for each product at each shop.
        
    h or help
        - Show this help text.
    q, quit or exit
        - Exit program.
    """)

def user_actions(con, cur, user_id):

    while True:
        try:
            user_input = input("\nEnter command: ").strip()
            if not user_input:
                continue
            
            # Tokenize user input
            tokens = shlex.split(user_input)
            command = tokens[0]
            args = [arg if arg != "NULL" else None for arg in tokens[1:]]
            
            # Route to appropriate function based on command
            if command == "ap":
                if len(args) == 12:
                    handle_database.add_product(con, cur, user_id, *args)
                else:
                    print("Error: 'ap' requires 13 arguments. Use 'help' to "
                          "see the correct format.")
            
            elif command == "rp":
                if len(args) == 1:
                    handle_database.remove_latest_product_version(con, cur,
                                                                  user_id,
                                                                  *args)
                else:
                    print("Error: 'rp' requires 1 argument.")
            
            elif command == "ac":
                if len(args) == 7:
                    handle_database.add_price(con, cur, user_id, *args)
                else:
                    print("Error: 'ac' requires 7 arguments.")
            
            elif command == "rc":
                if len(args) == 2:
                    handle_database.remove_price(con, cur, user_id, *args)
                else:
                    print("Error: 'rc' requires 2 arguments.")
            
            elif command == "as":
                if len(args) == 4:
                    handle_database.create_shop(con, cur, user_id, *args)
                else:
                    print("Error: 'as' requires 4 arguments.")
            
            elif command == "rs":
                if len(args) == 1:
                    handle_database.remove_shop(con, cur, *args)
                else:
                    print("Error: 'rs' requires 1 argument.")
            
            elif command == "ask":
                if len(args) == 1:
                    handle_database.add_shopkeeper_to_shop(con, cur, user_id,
                                                           *args)
                else:
                    print("Error: 'ask' requires 1 argument (shop_id).")
            
            elif command == "rsk":
                if len(args) == 1:
                    handle_database.remove_shopkeeper_from_shop(con, cur,
                                                                user_id, *args)
                else:
                    print("Error: 'rsk' requires 1 argument (shop_id).")
            
            elif command == "print":
                if args == ["users"]:
                    handle_database.print_users(cur)
                elif args == ["shops"]:
                    handle_database.print_shops(cur)
                elif args == ["products"]:
                    handle_database.print_products(cur)
                elif args == ["prices"]:
                    handle_database.print_prices(cur)
                else:
                    print("""
    Unknown command. Available printing options are:
        'users': Print whole user table.
        'shops': Print whole shop and shopkeeper table.
        'products': Print latest product information.
        'prices': Print latest price information.
        
        Type 'h' or 'help' for all available commands.
                            """)
            
            elif command in ("h", "help"):
                print_help()
            
            elif command in ("q", "quit", "exit"):
                print("Quitting application...")
                break
            
            else:
                print("Unknown command. Type 'h' or 'help' for available "
                      "commands.")
                
        except Exception as e:
            print("Exception while parsing input: " + repr(e))