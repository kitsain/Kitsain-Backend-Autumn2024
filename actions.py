
import shlex
import handle_database


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
    ac [product_id] [shop_id] [price] [discount_price] [waste_discount_percentage] [discount_valid_from] [discount_valid_to] [waste_valid_to] [waste_quantity]
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
                if len(args) == 9:
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