
import sqlite3
import requests
import shlex
from datetime import datetime
import requests

# --------------------------------------------------------------------------- #
# Initialization:
    
def initialize_database(conn, c):
    # Create table for users
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    role TEXT CHECK(role IN ('user', 'shopkeep', 'admin')) NOT NULL,
                    dietary_limitations TEXT,
                    allergies TEXT,
                    aura INTEGER DEFAULT 0,
                    email TEXT,
                    date_of_last_login TEXT,
                    date_of_creation TEXT
                )''')
    conn.commit()

    # Create table for products
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    size TEXT,
                    ean_code TEXT UNIQUE,
                    category TEXT,
                    dietary_info TEXT,
                    description TEXT,
                    image_link TEXT,
                    nutritional_info TEXT,
                    nutritional_score TEXT,
                    environmental_score TEXT,
                    esg_score TEXT,
                    co2_footprint TEXT,
                    additional_links TEXT
                )''')

    # Create table for shops
    c.execute('''CREATE TABLE IF NOT EXISTS shops (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location_gps TEXT,
                    address TEXT
                )''')

    # Create table for prices and discounts
    c.execute('''CREATE TABLE IF NOT EXISTS shop_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    shop_id INTEGER,
                    price REAL NOT NULL,
                    discount_status TEXT,
                    expiry_discount_status TEXT,
                    batch_size TEXT,
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    FOREIGN KEY (shop_id) REFERENCES shops(id)
                )''')


def clear_table_if_exists(conn, c, table_name):
    # Check if the table exists
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if c.fetchone() is not None:
        c.execute(f'DELETE FROM {table_name}')
        conn.commit()


def clear_tables(conn, c):
    clear_table_if_exists(conn, c, 'users')
    clear_table_if_exists(conn, c, 'products')
    clear_table_if_exists(conn, c, 'shops')
    clear_table_if_exists(conn, c, 'shop_prices')

# --------------------------------------------------------------------------- #
# Add to tables:
    
def add_user(conn, c, username, role, dietary_limitations=None, allergies=None, email=None):
    # Set the current date as the account creation date
    date_of_creation = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    default_aura = 0

    c.execute('''INSERT INTO users (username, role, dietary_limitations, allergies, aura, email, date_of_last_login, date_of_creation)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (username, role, dietary_limitations, allergies, default_aura, email, date_of_creation, date_of_creation))
    conn.commit()


def add_shop(conn, c, name, location_gps=None, address=None):
    c.execute('INSERT INTO shops (name, location_gps, address) VALUES (?, ?, ?)', 
              (name, location_gps, address))
    conn.commit()
    
    
def add_product(conn, c, ean_code, name, size, category, dietary_info=None, description=None, image_link=None, nutritional_info=None, nutritional_score=None, environmental_score=None, esg_score=None, co2_footprint=None, additional_links=None):
    c.execute('''INSERT INTO products (name, size, ean_code, category, dietary_info, description, image_link, nutritional_info, nutritional_score, environmental_score, esg_score, co2_footprint, additional_links)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (name, size, ean_code, category, dietary_info, description, image_link, nutritional_info, nutritional_score, environmental_score, esg_score, co2_footprint, additional_links))
    conn.commit()


def add_shop_price(conn, c, product_id, shop_id, price, discount_status=None, expiry_discount_status=None, batch_size=None):
    c.execute('INSERT INTO shop_prices (product_id, shop_id, price, discount_status, expiry_discount_status, batch_size) VALUES (?, ?, ?, ?, ?, ?)', 
              (product_id, shop_id, price, discount_status, expiry_discount_status, batch_size))
    conn.commit()

# --------------------------------------------------------------------------- #
# Search tables:
    
def product_exists_in_db(conn, c, ean_code):
    c.execute('SELECT * FROM products WHERE ean_code = ?', (ean_code,))
    return c.fetchone()
    

# --------------------------------------------------------------------------- #
# Search database:
    
def fetch_product_from_openfoodfacts(ean_code):
    url = f"https://fi.openfoodfacts.org/api/v0/product/{ean_code}.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the status is 4xx or 5xx
        product_data = response.json()
        
        # Check if product exists in the response
        if product_data.get('status') == 1:
            product = product_data.get('product', {})
            
            # Extract relevant information with fallbacks to 'Unknown'
            name = product.get("product_name", "Unknown")
            size = product.get("quantity", "Unknown")
            category = product.get("categories", "Unknown").split(',')[0]  # Take the first category
            dietary_info = product.get("ingredients_text", "Unknown")
            description = product.get("generic_name", name)  # Fallback to product name if no description
            image_link = product.get("image_url", None)
            nutritional_score = product.get("nutriscore_grade", "Unknown")
            environmental_score = product.get("ecoscore_grade", "Unknown")
            
            # Generate the console command string
            console_command = f'p "{ean_code}" "{name}" "{size}" "{category}" "{dietary_info}" "{description}" "{nutritional_score}" "{environmental_score}" "{image_link}"'
            return console_command
        else:
            print(f"Product with EAN {ean_code} not found in OpenFoodFacts.")
            return None
        
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    
    return None


# --------------------------------------------------------------------------- #
# Handle commands:
    


# --------------------------------------------------------------------------- #
# Print tables:

def print_users(conn, c):
    c.execute('SELECT * FROM users')
    users = c.fetchall()
    for user in users:
        print(user)


def print_products(conn, c):
    c.execute('SELECT * FROM products')
    products = c.fetchall()
    for product in products:
        print(product)


def print_shops_and_discounts(conn, c):
    c.execute('''SELECT shops.name, shops.address, shop_prices.price, shop_prices.discount_status, shop_prices.expiry_discount_status
                 FROM shop_prices
                 JOIN shops ON shop_prices.shop_id = shops.id''')
    results = c.fetchall()
    for result in results:
        print(result)


# --------------------------------------------------------------------------- #

def list_columns(conn, c, table_name):
    c.execute(f'PRAGMA table_info({table_name})')
    columns = c.fetchall()
    
    print(f"Columns in table '{table_name}':")
    for column in columns:
        print(f"Column name: {column[1]}, Type: {column[2]}")

# Function to display help text
def display_help():
    help_text = """
    Available Commands:
    -------------------
    
    1. Add a product (p):
       - Command: p [ean_code] [name] [size] [category] [dietary_info] [description] [esg_score] [co2_footprint] [additional_links]
       - With flags:
         -ean [EAN code]
         -name [Product Name]
         -size [Product Size]
         -category [Category]
         -dietary [Dietary Information]
         -desc [Description]
         -esg [ESG Score]
         -co2 [CO2 Footprint]
         -links [Additional Information Links]
       - Example without flags:
         a "6408430340521" "Valio Cheese" "500g" "Cheese" "Contains milk" "A fine cheese" "A" "Low" "http://example.com/more-info"
       - Example with flags:
         a -ean "6408430340521" -name "Valio Cheese" -size "500g" -category "Cheese" -esg "A" -co2 "Low" -links "http://example.com/more-info"

    2. Add a user (u):
       - Command: u [username] [role] [dietary_limitations] [allergies] [email] [date_of_last_login]
       - With flags:
         -username [Username]
         -role [Role: user/shopkeep/admin]
         -dietary [Dietary Limitations]
         -allergies [Allergies]
         -email [Email Address]
         -lastlogin [Date of Last Login: YYYY-MM-DD HH:MM:SS]
       - Example without flags:
         u "john_doe" "user" "61.4741,23.8044" "vegetarian" "peanut" 100 "john@example.com" "2023-10-16 14:30:00"
       - Example with flags:
         u -username "john_doe" -role "user" -email "john@example.com" -lastlogin "2023-10-16 14:30:00"

    3. Add a shop (s):
       - Command: s [shop_name] [gps_location] [address]
       - With flags:
         -name [Shop Name]
         -gps [GPS Location]
         -address [Address]
       - Example without flags:
         s "K-Market Duo" "61.4741,23.8044" "Duo Shopping Center, Tampere"
       - Example with flags:
         s -name "K-Market Duo" -gps "61.4741,23.8044" -address "Duo Shopping Center, Tampere"

    4. Add a discount (d):
       - Command: d [ean_code] [shop_name] [price] [discount_status] [expiry_discount_status] [batch_size]
       - With flags:
         -ean [EAN Code]
         -shop [Shop Name]
         -price [Price]
         -discount [Discount Status]
         -expiry [Expiry Discount Status]
         -batch [Batch Size]
       - Example without flags:
         d "6408430340521" "K-Market Duo" 3.50 "10% discount" "Valid for two weeks" "Many"
       - Example with flags:
         d -ean "6408430340521" -shop "K-Market Duo" -price 3.50 -discount "10% discount" -expiry "Valid for two weeks" -batch "Many"

    5. General:
       - h or help: Display this help text.
       - q, exit or quit: Exit the application.

    Notes:
    - When not using flags, the input order must be strictly followed.
    - Fields that are not required can be skipped by leaving them blank.
    """
    print(help_text)

# Helper function to detect if a token contains a flag (e.g., -ean)
def is_flag(token):
    return token.startswith('-')

# Function to handle commands with or without flags
def handle_console_command(conn, c, command):
    tokens = shlex.split(command)
    if not tokens:
        print("Invalid command.")
        return

    cmd = tokens[0]
    args = tokens[1:]  # Everything after the command

    if cmd == "p":  # Adding a product
        if len(args) == 1 and args[0].startswith('-ean'):
            ean_code = args[0].split(" ")[1].strip('"')
            
            # Try to fetch product information from OpenFoodFacts
            product_info = fetch_product_from_openfoodfacts(ean_code)
            
            if product_info:
                # Use the fetched data to create the product
                print(f">>> Automatically fetched product info: {product_info}")
                add_product(
                    conn,
                    c,
                    product_info["ean_code"],
                    product_info["name"],
                    product_info["size"],
                    product_info["category"],
                    product_info["dietary_info"],
                    product_info["description"],
                    product_info["image_link"],
                    product_info["nutritional_score"],
                    product_info["environmental_score"]
                )
                print(f"Product {product_info['name']} (EAN {ean_code}) added to the database.")
            else:
                print(f"Product with EAN {ean_code} not found. Please provide the product details manually.")
        
        else:
            # Default order: ean_code, name, size, category, dietary_info, description, esg_score, co2_footprint, additional_links
            ean_code, name, size, category, dietary_info, description = None, None, None, None, None, None
            esg_score, co2_footprint, additional_links = None, None, None
    
            if len(args) == 1 and args[0].startswith('-ean'):
                ean_code = args[0].split(" ")[1].strip('"')
                
                # Try to fetch product information from OpenFoodFacts
                product_info = fetch_product_from_openfoodfacts(ean_code)
    
            if any(is_flag(token) for token in args):
                # Parse flags
                for token in args:
                    if token.startswith('-ean'):
                        ean_code = token.split(" ")[1].strip('"')
                    elif token.startswith('-name'):
                        name = token.split(" ")[1].strip('"')
                    elif token.startswith('-size'):
                        size = token.split(" ")[1].strip('"')
                    elif token.startswith('-category'):
                        category = token.split(" ")[1].strip('"')
                    elif token.startswith('-dietary'):
                        dietary_info = token.split(" ")[1].strip('"')
                    elif token.startswith('-desc'):
                        description = token.split(" ")[1].strip('"')
                    elif token.startswith('-esg'):
                        esg_score = token.split(" ")[1].strip('"')
                    elif token.startswith('-co2'):
                        co2_footprint = token.split(" ")[1].strip('"')
                    elif token.startswith('-links'):
                        additional_links = token.split(" ")[1].strip('"')
            else:
                # Assume the information follows the default order
                input_data = args + [None] * (9 - len(args))  # Fill missing fields with None
                ean_code, name, size, category, dietary_info, description, esg_score, co2_footprint, additional_links = input_data[:9]
    
            if not ean_code or not name or not size or not category:
                print("Missing mandatory product information. Provide at least ean_code, name, size, and category.")
                return
    
            # Add the product to the database
            add_product(conn, c, ean_code, name, size, category, dietary_info, description, None, None, None, None, esg_score, co2_footprint, additional_links)
            print(f"Product {name} (EAN {ean_code}) added to the database.")

    elif cmd == "u":  # Adding a user
        username, role, dietary_limitations, allergies, email = None, None, None, None, None

        if any(is_flag(token) for token in args):
            # Parse flags
            for token in args:
                if token.startswith('-username'):
                    username = token.split(" ")[1].strip('"')
                elif token.startswith('-role'):
                    role = token.split(" ")[1].strip('"')
                elif token.startswith('-dietary'):
                    dietary_limitations = token.split(" ")[1].strip('"')
                elif token.startswith('-allergies'):
                    allergies = token.split(" ")[1].strip('"')
                elif token.startswith('-email'):
                    email = token.split(" ")[1].strip('"')
        else:
            # Assume the information follows the default order
            input_data = args + [None] * (5 - len(args))  # Fill missing fields with None
            username, role, dietary_limitations, allergies, email = input_data[:5]

        if not username or not role:
            print("Missing mandatory user information. Provide at least username and role.")
            return

        # Add user to the database
        add_user(conn, c, username, role, dietary_limitations, allergies, email)
        print(f"User {username} with role {role} added to the database.")

    elif cmd == "s":  # Adding a shop
        # Default order: shop_name, gps_location, address
        shop_name, gps_location, address = None, None, None

        if any(is_flag(token) for token in args):
            # Parse flags
            for token in args:
                if token.startswith('-name'):
                    shop_name = token.split(" ")[1].strip('"')
                elif token.startswith('-gps'):
                    gps_location = token.split(" ")[1].strip('"')
                elif token.startswith('-address'):
                    address = token.split(" ")[1].strip('"')
        else:
            # Assume the information follows the default order
            input_data = args + [None] * (3 - len(args))  # Fill missing fields with None
            shop_name, gps_location, address = input_data[:3]

        if not shop_name:
            print("Missing mandatory shop information. Provide at least shop name.")
            return

        # Add shop to the database
        add_shop(conn, c, shop_name, gps_location, address)
        print(f"Shop {shop_name} added to the database.")

    elif cmd == "d":  # Adding a discount
        # Default order: ean_code, shop_name, price, discount_status, expiry_discount_status, batch_size
        product_ean, shop_name, price, discount_status, expiry_discount_status, batch_size = None, None, None, None, None, None

        if any(is_flag(token) for token in args):
            # Parse flags
            for token in args:
                if token.startswith('-ean'):
                    product_ean = token.split(" ")[1].strip('"')
                elif token.startswith('-shop'):
                    shop_name = token.split(" ")[1].strip('"')
                elif token.startswith('-price'):
                    price = float(token.split(" ")[1].strip('"'))
                elif token.startswith('-discount'):
                    discount_status = token.split(" ")[1].strip('"')
                elif token.startswith('-expiry'):
                    expiry_discount_status = token.split(" ")[1].strip('"')
                elif token.startswith('-batch'):
                    batch_size = token.split(" ")[1].strip('"')
        else:
            # Assume the information follows the default order
            input_data = args + [None] * (6 - len(args))  # Fill missing fields with None
            product_ean, shop_name, price, discount_status, expiry_discount_status, batch_size = input_data[:6]

        if not product_ean or not shop_name or not price:
            print("Missing mandatory discount information. Provide at least ean_code, shop_name, and price.")
            return

        # Get product and shop IDs
        c.execute('SELECT id FROM products WHERE ean_code = ?', (product_ean,))
        product_id = c.fetchone()
        if product_id is None:
            print(f"Product with EAN {product_ean} not found.")
            return

        c.execute('SELECT id FROM shops WHERE name = ?', (shop_name,))
        shop_id = c.fetchone()
        if shop_id is None:
            print(f"Shop {shop_name} not found.")
            return

        # Add discount to the database
        add_shop_price(conn, c, product_id[0], shop_id[0], price, discount_status, expiry_discount_status, batch_size)
        print(f"Discount for product {product_ean} added to shop {shop_name}.")


    elif cmd == "print":
        print("\n---- Users ----")
        print_users(conn, c)
        print("\n\n---- Products ----")
        print_products(conn, c)
        print("\n\n---- Shops and Discounts ----")
        print_shops_and_discounts(conn, c)
        print("\n\n")

    elif cmd == "h" or cmd == "help":
        display_help()

    else:
        print("Unknown command. Type 'h' or 'help' for more information.")

# Main loop to handle user input
if __name__ == "__main__":
    conn = sqlite3.connect('food_app.db')
    c = conn.cursor()

    clear_tables(conn, c)
    initialize_database(conn, c)
    
    while True:
        try:
            user_input = input("Enter command: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                break
            elif user_input.lower() in ["test"]:
                # Add some users
                handle_console_command(conn, c, 'u Admin admin')
                handle_console_command(conn, c, 'u "K-Market Duo Kauppias" shopkeep')
                handle_console_command(conn, c, 'u Mikko user mikko@email.com')
                handle_console_command(conn, c, 'u Minna user vegetarian minna@email.com')
                handle_console_command(conn, c, 'u Markku user vegan peanut markku@email.com')
                
                # Add some products
                handle_console_command(conn, c, 'p "6408430000548" "Valio Vapaan Lehmän Kevytmaito" "1.75L" "Milk" "Contains milk" "Free-range low-fat milk from Finland" "A" "Low CO2 impact" "https://www.valio.fi/tuotteet/vapaan-lehman-kevytmaito-1-75l/"')
                handle_console_command(conn, c, 'p "6416075931073" "Närpiön Vihannes Helmitomaatti" "500g" "Tomato" "Vegan" "Small, sweet cherry tomatoes, perfect for salads and snacks" "A" "Low" "https://example.com/helmitomaatti"')
                handle_console_command(conn, c, 'p "6410405333773" "Pirkka Parhaat Salame Napoli ilmakuivattu kestomakkara" "70g" "Cured Meat" "Contains pork" "Air-dried Italian salami with a rich, savory taste, perfect for antipasti or sandwiches" "B" "Moderate CO2 impact" "https://www.k-ruoka.fi/kauppa/tuote/pirkka-parhaat-salame-napoli-70g-6410405142757"')
                handle_console_command(conn, c, 'p "6408430338078" "Valio Tuorejuusto" "200g" "Cheese" "Contains milk" "Fresh, creamy cheese, perfect for spreading or cooking" "A" "Low CO2 impact" "https://example.com/tuorejuusto"')
                handle_console_command(conn, c, 'p "6410405236982" "Pirkka Parhaat Le Gruyère AOP" "200g" "Cheese" "Contains milk" "A classic Swiss Gruyère cheese with a rich, nutty flavor" "B" "Moderate CO2 impact" "https://example.com/gruyere"')
                handle_console_command(conn, c, 'p "6405506092254" "Perheleipuri Salonen Jussin Viipaloitu Moniviljaleipä" "500g" "Bread" "May contain traces of milk, eggs, sesame seeds, soy" "Sliced multigrain bread with rich flavor, stone-baked, additive-free" "A" "Low" "https://www.fiksuruoka.fi/product/20050/"')
                
                # Try add product through OpenFoodFacts
                result = fetch_product_from_openfoodfacts("5410041001204")
                if result:
                    handle_console_command(conn, c, f'{result}')
                
                # Add shops
                handle_console_command(conn, c, 's "K-Market Duo" "61.4741,23.8044" "Duo Shopping Center, Hervanta, Tampere, Finland"')
                handle_console_command(conn, c, 's "S-Market Duo" "61.4741,23.8044" "Duo Shopping Center, Hervanta, Tampere, Finland"')
                handle_console_command(conn, c, 's "Lidl Duo" "61.4741,23.8044" "Duo Shopping Center, Hervanta, Tampere, Finland"')
                
                # Add discounts and red label waste product pricing
                handle_console_command(conn, c, 'd "6408430000548" "K-Market Duo" 1.75 "Regular price" "No expiry discount" "Many"')
                handle_console_command(conn, c, 'd "6416075931073" "K-Market Duo" 2.99 "Regular price" "No expiry discount" "Many"')
                handle_console_command(conn, c, 'd "6416075931073" "S-Market Duo" 2.89 "Regular price" "No expiry discount" "Many"')
                handle_console_command(conn, c, 'd "6410405333773" "K-Market Duo" 3.99 "Regular price" "No expiry discount" "Many"')
                handle_console_command(conn, c, 'd "6408430338078" "K-Market Duo" 1.85 "Regular price" "No expiry discount" "Many"')
                handle_console_command(conn, c, 'd "6408430338078" "S-Market Duo" 1.80 "Regular price" "No expiry discount" "Many"')
                handle_console_command(conn, c, 'd "6410405236982" "K-Market Duo" 5.99 "Regular price" "No expiry discount" "Many"')
                
                handle_console_command(conn, c, 'print')
            else:
                handle_console_command(conn, c, user_input)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            
    conn.close()
    
    
