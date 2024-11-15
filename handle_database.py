
from datetime import datetime
import sqlite3
import math
from werkzeug.security import generate_password_hash, check_password_hash

def create_database(con, cur):
    """
    Creates a database if it is not created already.
    :param con: Connection to the database
    :param cur: Makes queries to the database possible
    :return: Returns to the call function
    """

    # Create the 'user' table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,                          -- Unique identifier for each user
        username TEXT NOT NULL UNIQUE,                                      -- Username for the user, must be unique
        password TEXT NOT NULL,                                             -- Password for the user's account
        email TEXT NOT NULL UNIQUE,                                         -- User's email address (optional)
        role TEXT CHECK(role IN ('user', 'shopkeeper', 'admin')) NOT NULL,  -- Role of the user (user, shopkeeper, admin)
        aura_points INTEGER DEFAULT 0,                                      -- Points representing the user's contributions or reputation
        last_login DATETIME,                                                -- Timestamp of the user's last login
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP                    -- When the user account was created
    )''')

    # Create the 'shop' table
    cur.execute('''
    CREATE TABLE IF NOT EXISTS shop (
        shop_id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique identifier for each shop
        store_name TEXT NOT NULL,                   -- Name of the store
        store_chain TEXT,                           -- Store chain the shop belongs to (e.g., Lidl, K-Market)
        location_address TEXT,                      -- Physical address of the shop
        location_gps TEXT                           -- GPS coordinates of the shop location
    )''')

    # Create the 'works_for' table to track which shopkeepers work for which
    # shops
    cur.execute('''
    CREATE TABLE IF NOT EXISTS works_for (
        user_id INTEGER,                                                                    -- User ID of the shopkeeper
        shop_id INTEGER,                                                                    -- Shop ID of the shop they manage
        PRIMARY KEY (user_id, shop_id),                                                     -- Composite key to ensure no duplicates
        FOREIGN KEY (user_id) REFERENCES user(user_id),                                     -- Links to the 'user' table (must be a shopkeeper)
        FOREIGN KEY (shop_id) REFERENCES shop(shop_id)                                     -- Links to the 'shop' table
    )''')

    # Create the 'product' table with version tracking
    cur.execute('''
    CREATE TABLE IF NOT EXISTS product (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,           -- Unique identifier for each product version
        product_name TEXT NOT NULL,                             -- Name of the product (e.g., "Milk 1L")
        weight_g INTEGER,                                       -- Weight of the product in grams (optional)
        volume_l REAL,                                          -- Volume of the product in liters (optional)
        barcode TEXT,                                           -- Barcode of the product (not unique to allow multiple versions)
        category TEXT,                                          -- Category of the product (e.g., "Dairy", "Snacks")
        gluten_free BOOLEAN,                                    -- Is the food gluten free (True, False)
        esg_score TEXT,                                         -- Environmental, Social, and Governance (ESG) score for the product
        co2_footprint TEXT,                                     -- CO2 footprint for the product
        brand TEXT,                                             -- Brand of the product (e.g., "Valio")
        sub_brand TEXT,                                         -- Sub-brand of the product (e.g., "Valio Olo")
        parent_company TEXT,                                    -- Parent company of the brand (e.g., "Unilever")
        information_links TEXT,                                 -- Links to additional product information (e.g., website)
        user_created INTEGER,                                   -- The ID of the user who created this product version
        creation_date DATETIME DEFAULT CURRENT_TIMESTAMP,       -- When this product version was created
        FOREIGN KEY (user_created) REFERENCES user(user_id)     -- Links to the 'user' table
    )''')

    # Create the 'price' table to track product prices at shops
    cur.execute('''
    CREATE TABLE IF NOT EXISTS price (
        price_id INTEGER PRIMARY KEY AUTOINCREMENT,                 -- Unique identifier for each price entry
        product_id INTEGER NOT NULL,                                -- Product ID for which this price applies
        shop_id INTEGER NOT NULL,                                   -- Shop ID where the product is sold
        price REAL NOT NULL,                                        -- Price of the product at the shop
        discount_price REAL,                                        -- Discounted price, if any (optional)
        waste_discount_percentage REAL,                             -- Percentage discount due to expiration or waste reduction
        waste_quantity TEXT CHECK(waste_quantity IN ('few', 'some', 'many')), -- Approximate number of waste products
        report_date DATETIME DEFAULT CURRENT_TIMESTAMP,             -- When this price entry was reported/created
        discount_valid_from DATETIME,                               -- When discount price becomes valid
        discount_valid_to DATETIME,                                 -- When discount price expires
        waste_valid_to DATETIME,                                    -- When waste discount expires (Valid from report_date)
        user_created INTEGER,                                       -- The user who defined or reported this price
        FOREIGN KEY (product_id) REFERENCES product(product_id),    -- Links to the 'product' table
        FOREIGN KEY (shop_id) REFERENCES shop(shop_id),             -- Links to the 'shop' table
        FOREIGN KEY (user_created) REFERENCES user(user_id)         -- Links to the 'user' table
    )''')

    # Add an index for product barcodes to allow multiple versions
    # of the same product
    cur.execute('CREATE INDEX IF NOT EXISTS idx_product_barcode ON '
                'product(barcode);')

    # Commit the changes to save the schema creation
    con.commit()



def add_user(con, cur, username, password, email, role):
    """
    Adds a new user to the user table with hashed password.
    """
    try:
        hashed_password = generate_password_hash(password)
        cur.execute('''
        INSERT INTO user (username, password, email, role, creation_date)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (username, hashed_password, email, role))
        con.commit()
        print(f"User '{username}' with role '{role}' added successfully.")
        return True
    except sqlite3.Error as e:
        print(f"Error adding user: {e}")
        return False


def remove_user(con, cur, user_id, requester_id):
    """
    Removes a user from the user table. Only admins or the user themselves can
    remove a user.
    
    Parameters:
    - con: SQLite connection object
    - cur: SQLite cursor object
    - user_id: ID of the user to be removed
    - requester_id: ID of the user making the removal request
    """
    
    # Check if the requester is an admin or if the requester is the user being
    # removed
    cur.execute('SELECT role FROM user WHERE user_id = ?', (requester_id,))
    requester_role = cur.fetchone()
    
    if requester_role and (requester_role[0] == 'admin' or requester_id ==
                           user_id):
        # Proceed with removing the user
        try:
            cur.execute('DELETE FROM user WHERE user_id = ?', (user_id,))
            con.commit()
            print(f"User with ID {user_id} has been removed.")
        
        except sqlite3.Error as e:
            print(f"Error removing user: {e}")
    else:
        print("Permission denied. Only admins or the user themselves can "
              "remove this user.")


def authenticate_user(cur, username, password):
    """
    Authenticates a user by comparing the provided password with the hashed password in the database.
    """
    try:
        cur.execute('SELECT user_id, password FROM user WHERE username = ?', (username,))
        result = cur.fetchone()
        if result:
            user_id, stored_password = result
            if check_password_hash(stored_password, password):
                # Update last login:
                cur.execute('''
                    UPDATE user
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                return user_id  # Successful authentication
            else:
                return -2  # Incorrect password
        else:
            return -1  # Username not found
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return -1


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
    

def print_users(cur):
    """
    Prints all users and their information from the user table.
    
    Parameters:
    - cur: SQLite cursor object
    """
    
    try:
        cur.execute('''
        SELECT user_id, username, role, email, aura_points, last_login, 
        creation_date
        FROM user
        ORDER BY user_id
        ''')
        
        rows = cur.fetchall()
        
        if rows:
            print("All Users:")
            for row in rows:
                print(f"User ID: {row[0]}")
                print(f"Username: {row[1]}")
                print(f"Role: {row[2]}")
                print(f"Email: {row[3]}")
                print(f"Aura Points: {row[4]}")
                print(f"Last Login: {row[5]}")
                print(f"Creation Date: {row[6]}")
                print("-" * 40)
        else:
            print("No users found in the database.")
    
    except sqlite3.Error as e:
        print(f"Error fetching users: {e}")
        



# Note: Products are not updated in the table; new versions override previous
# version given a later creation date
def add_product(con, cur, user_id, product_name, weight_g, volume_l,
                barcode, category, esg_score, co2_footprint, brand, sub_brand,
                parent_company, information_links, gluten_free):
    """
    Adds a new product to the product table.
    
    Parameters:
    - con: SQLite connection object
    - cur: SQLite cursor object
    - user_id: ID of the user who created the product entry
    - product_name: Name of the product
    - weight_g: Weight of the product in grams (optional)
    - volume_l: Volume of the product in liters (optional)
    - barcode: Product barcode (should be unique or the same for different
    versions)
    - category: Category of the product (e.g., Dairy, Snacks)
    - esg_score: ESG score for the product (optional)
    - co2_footprint: CO2 footprint for the product (optional)
    - brand: Brand of the product
    - sub_brand: Sub-brand of the product (optional)
    - parent_company: Parent company of the product (optional)
    - information_links: Links to additional product information (optional)
    - gluten_free: Boolean indicating if the product is gluten-free
    """

    # get_data.fetch_product_from_OFF(barcode)

    try:
        cur.execute('''
        INSERT INTO product (
            product_name, weight_g, volume_l, barcode, category, esg_score, 
            co2_footprint, 
            brand, sub_brand, parent_company, information_links, user_created, 
            gluten_free
        ) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (product_name, weight_g, volume_l, barcode, category, esg_score,
              co2_footprint,
              brand, sub_brand, parent_company, information_links, user_id,
              gluten_free))
        
        # Commit the changes to the database
        con.commit()
        
        print(f"Product '{product_name}' added successfully.")
    
    except sqlite3.IntegrityError as e:
        print(f"Error: {e}")


def remove_latest_product_version(con, cur, user_id, barcode):
    """
    Deletes the latest version of a product based on the barcode if the user is
    an admin.
    
    Parameters:
    - con: SQLite connection object
    - cur: SQLite cursor object
    - barcode: Barcode of the product
    - user_id: ID of the user attempting to delete the product (must be an
    admin)
    """
    
    # Check if the user is an admin
    cur.execute('SELECT role FROM user WHERE user_id = ?', (user_id,))
    user_role = cur.fetchone()
    
    if user_role and user_role[0] == 'admin':
        # User is an admin, proceed with deletion
        try:
            # Find the latest version of the product based on barcode and
            # creation date
            cur.execute('''
            SELECT product_id FROM product
            WHERE barcode = ?
            ORDER BY creation_date DESC
            LIMIT 1
            ''', (barcode,))
            product_to_delete = cur.fetchone()
            
            if product_to_delete:
                # Delete the product with the latest creation date for the given
                # barcode
                cur.execute('DELETE FROM product WHERE product_id = ?',
                            (product_to_delete[0],))
                con.commit()
                
                print(f"Latest version of product with barcode {barcode} "
                      f"has been deleted.")
            else:
                print(f"No product found with barcode {barcode}.")
        
        except sqlite3.Error as e:
            print(f"Error: {e}")
    
    else:
        print("Permission denied. Only admin users can delete products.")


def print_products(cur):
    """
    Lists the latest versions of each product based on the barcode and
    creation_date.
    
    Parameters:
    - cur: SQLite cursor object
    """
    
    query = '''
    SELECT 
        product_name, 
        weight_g, 
        volume_l, 
        barcode, 
        category, 
        esg_score, 
        co2_footprint, 
        brand, 
        sub_brand, 
        parent_company, 
        information_links, 
        gluten_free, 
        creation_date 
    FROM product
    WHERE (barcode, creation_date) IN (
        SELECT barcode, MAX(creation_date) 
        FROM product 
        GROUP BY barcode
    )
    ORDER BY creation_date DESC
    '''
    
    cur.execute(query)
    rows = cur.fetchall()
    
    if rows:
        print("Latest versions of all products:")
        for row in rows:
            print(f"Product Name: {row[0]}")
            print(f"Weight (g): {row[1]}")
            print(f"Volume (L): {row[2]}")
            print(f"Barcode: {row[3]}")
            print(f"Category: {row[4]}")
            print(f"ESG Score: {row[5]}")
            print(f"CO2 Footprint: {row[6]}")
            print(f"Brand: {row[7]}")
            print(f"Sub-brand: {row[8]}")
            print(f"Parent Company: {row[9]}")
            print(f"Information Links: {row[10]}")
            print(f"Gluten Free: {row[11]}")
            print(f"Creation Date: {row[12]}")
            print("-" * 40)
    else:
        print("No products found.")




def create_shop(con, cur, user_id, store_name, store_chain, location_address,
                location_gps):
    """
    Creates a new shop in the database. No shopkeepers are assigned initially.
    
    Parameters:
    - con: SQLite connection object
    - cur: SQLite cursor object
    - user_id: ID of user that created the shop (for now this is not used for
    anything)
    - store_name: Name of the store (e.g., "K-Market Duo")
    - store_chain: The chain the store belongs to (optional, e.g., "K-Market")
    - location_address: The physical address of the shop
    - location_gps: The GPS coordinates of the shop (optional)
    """
    
    try:
        cur.execute('''
        INSERT INTO shop (store_name, store_chain, location_address, 
        location_gps)
        VALUES (?, ?, ?, ?)
        ''', (store_name, store_chain, location_address, location_gps))
        
        con.commit()
        print(f"Shop '{store_name}' created successfully.")
    
    except sqlite3.Error as e:
        print(f"Error: {e}")


def add_shopkeeper_to_shop(con, cur, user_id, shop_id):
    """
    Adds a shopkeeper to a shop. Only users with the 'shopkeeper' role can be
    added as shopkeepers.
    
    Parameters:
    - con: SQLite connection object
    - cur: SQLite cursor object
    - user_id: ID of the user to be added as shopkeeper
    - shop_id: ID of the shop
    """
    
    # Check if the user is a shopkeeper
    cur.execute('SELECT role FROM user WHERE user_id = ?', (user_id,))
    user_role = cur.fetchone()
    
    if user_role and user_role[0] == 'shopkeeper':
        # Proceed with adding the shopkeeper to the shop
        try:
            cur.execute('''
            INSERT INTO works_for (user_id, shop_id)
            VALUES (?, ?)
            ''', (user_id, shop_id))
            
            con.commit()
            print(f"User {user_id} has been added as a shopkeeper to shop "
                  f"{shop_id}.")
        
        except sqlite3.Error as e:
            print(f"Error: {e}")
    else:
        print(f"User {user_id} is not a shopkeeper and cannot be added "
              f"to a shop.")


def remove_shopkeeper_from_shop(con, cur, user_id, shop_id):
    """
    Removes a shopkeeper from a shop if they are currently assigned to it.
    
    Parameters:
    - con: SQLite connection object
    - cur: SQLite cursor object
    - user_id: ID of the shopkeeper to be removed
    - shop_id: ID of the shop
    """
    
    # Check if the user is a shopkeeper for this shop
    cur.execute('SELECT * FROM works_for WHERE user_id = ? AND shop_id = ?',
                (user_id, shop_id))
    shopkeeper_assignment = cur.fetchone()
    
    if shopkeeper_assignment:
        # Proceed with removing the shopkeeper from the shop
        try:
            cur.execute('DELETE FROM works_for WHERE user_id = ? AND '
                        'shop_id = ?', (user_id, shop_id))
            con.commit()
            print(f"User {user_id} has been removed as a shopkeeper "
                  f"from shop {shop_id}.")
        
        except sqlite3.Error as e:
            print(f"Error: {e}")
    else:
        print(f"User {user_id} is not currently assigned as a shopkeeper "
              f"to shop {shop_id}.")


def print_shops(cur):
    """
    Prints all shops and their information, including assigned shopkeepers.
    
    Parameters:
    - cur: SQLite cursor object
    """
    
    try:
        # Query to get shop details
        cur.execute('''
        SELECT s.shop_id, s.store_name, s.store_chain, s.location_address, 
        s.location_gps
        FROM shop s
        ORDER BY s.shop_id
        ''')
        
        shops = cur.fetchall()
        
        if shops:
            print("All Shops and Assigned Shopkeepers:")
            for shop in shops:
                (shop_id, store_name, store_chain, location_address,
                 location_gps) = shop
                
                print(f"Shop ID: {shop_id}")
                print(f"Store Name: {store_name}")
                print(f"Store Chain: {store_chain}")
                print(f"Location Address: {location_address}")
                print(f"Location GPS: {location_gps}")
                
                # Query to get shopkeepers for this shop
                cur.execute('''
                SELECT u.user_id, u.username
                FROM works_for wf
                JOIN user u ON wf.user_id = u.user_id
                WHERE wf.shop_id = ?
                ''', (shop_id,))
                
                shopkeepers = cur.fetchall()
                
                if shopkeepers:
                    print("Assigned Shopkeepers:")
                    for shopkeeper in shopkeepers:
                        print(f"  - Shopkeeper ID: {shopkeeper[0]}, "
                              f"Username: {shopkeeper[1]}")
                else:
                    print("  No shopkeepers assigned.")
                
                print("-" * 40)
        else:
            print("No shops found in the database.")
    
    except sqlite3.Error as e:
        print(f"Error fetching shops: {e}")
        
        


def add_price(con, cur, user_id, product_id, shop_id, price, discount_price=None, waste_discount_percentage=None, 
              discount_valid_from=None, discount_valid_to=None, waste_valid_to=None, waste_quantity=None):
    """
    Adds a new price entry to the price table.

    Parameters:
    - con: SQLite connection object
    - cur: SQLite cursor object
    - user_id: ID of the user creating the price entry
    - product_id: ID of the product being priced
    - shop_id: ID of the shop where the product is being sold
    - price: Base price of the product
    - discount_price: Discounted campaign price, if any (optional)
    - waste_discount_percentage: Percentage discount for waste reduction, if any (optional)
    - discount_valid_from: The date when the campaign discount becomes valid (optional)
    - discount_valid_to: The date when the campaign discount expires (optional)
    - waste_valid_to: The date when the waste discount expires (optional)
    - waste_quantity: Approximate quantity of waste products available ("few", "some", "many")
    """

    # Ensure waste_quantity value is one of the allowed options
    if waste_quantity not in (None, 'few', 'some', 'many'):
        print("Error: waste_quantity must be 'few', 'some', or 'many'.")
        return

    try:
        # Insert the new price entry
        cur.execute('''
            INSERT INTO price (
                product_id, shop_id, price, discount_price, waste_discount_percentage, report_date,
                discount_valid_from, discount_valid_to, waste_valid_to, waste_quantity, user_created
            )
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?)
        ''', (product_id, shop_id, price, discount_price, waste_discount_percentage, 
              discount_valid_from, discount_valid_to, waste_valid_to, waste_quantity, user_id))
        
        # Commit the transaction
        con.commit()
        print(f"Price for product {product_id} at shop {shop_id} added successfully.")
    
    except sqlite3.Error as e:
        print(f"Error: {e}")



def remove_price(con, cur, user_id, price_id, shop_id):
    """
    Removes a price entry if the user is an admin or a shopkeeper of the shop
    where the price is listed.
    
    Parameters:
    - con: SQLite connection object
    - cur: SQLite cursor object
    - user_id: ID of the user attempting to remove the price
    - price_id: ID of the price entry to be removed
    - shop_id: ID of the shop where the price is listed
    """
    
    # Check if the user is an admin or shopkeeper of the given shop
    cur.execute('SELECT role FROM user WHERE user_id = ?', (user_id,))
    user_role = cur.fetchone()
    
    if user_role and user_role[0] == 'admin':
        # User is an admin, they are allowed to delete the price
        try:
            cur.execute('DELETE FROM price WHERE price_id = ?', (price_id,))
            con.commit()
            print(f"Price with ID {price_id} has been removed by admin.")
        
        except sqlite3.Error as e:
            print(f"Error: {e}")
    
    else:
        # Check if the user is a shopkeeper for the given shop
        cur.execute('SELECT * FROM works_for WHERE user_id = ? AND shop_id = ?',
                    (user_id, shop_id))
        shopkeeper_assignment = cur.fetchone()
        
        if shopkeeper_assignment:
            # User is a shopkeeper for this shop, proceed with deletion
            try:
                cur.execute('DELETE FROM price WHERE price_id = ?', (price_id,))
                con.commit()
                print(f"Price with ID {price_id} has been removed"
                      f" by shopkeeper.")
            
            except sqlite3.Error as e:
                print(f"Error: {e}")
        else:
            print("Permission denied. Only admins or shopkeepers "
                  "of the shop can remove prices.")


def get_current_price(cur, product_id, shop_id):
    """
    Retrieves the current base price and effective discount price for a given product and shop.

    Parameters:
    - cur: SQLite cursor object
    - product_id: ID of the product
    - shop_id: ID of the shop where the product is sold

    Returns:
    - A tuple (base_price, effective_discount_price) where:
        - base_price is the regular price of the product at the shop
        - effective_discount_price is the discount price (if active), potentially combining
          campaign and waste discounts. Returns None if no discount is active.
    """
    # Retrieve the latest base price for the product at the shop
    cur.execute('''
    SELECT price
    FROM price
    WHERE product_id = ? AND shop_id = ?
    ORDER BY report_date DESC
    LIMIT 1
    ''', (product_id, shop_id))
    
    base_price = cur.fetchone()
    if not base_price:
        print("No base price found for the given product and shop.")
        return None, None

    base_price = base_price[0]
    effective_discount_price = None

    # Get current timestamp
    current_time = datetime.now()

    # Retrieve active campaign discount price, if available
    cur.execute('''
    SELECT discount_price
    FROM price
    WHERE product_id = ? AND shop_id = ?
      AND discount_price IS NOT NULL
      AND discount_valid_from <= ?
      AND discount_valid_to > ?
    ORDER BY report_date DESC
    LIMIT 1
    ''', (product_id, shop_id, current_time, current_time))
    
    campaign_discount_price = cur.fetchone()
    if campaign_discount_price:
        effective_discount_price = campaign_discount_price[0]
    else:
        effective_discount_price = base_price

    # Retrieve active waste discount percentage, if available
    cur.execute('''
    SELECT waste_discount_percentage
    FROM price
    WHERE product_id = ? AND shop_id = ?
      AND waste_discount_percentage IS NOT NULL
      AND waste_valid_to > ?
    ORDER BY report_date DESC
    LIMIT 1
    ''', (product_id, shop_id, current_time))
    
    waste_discount_percentage = cur.fetchone()

    # Apply waste discount to the effective discount price if applicable
    if waste_discount_percentage:
        waste_discount_percentage = waste_discount_percentage[0]
        effective_discount_price *= (1 - waste_discount_percentage / 100)

    # Return the base price and the effective discount price
    return base_price, effective_discount_price


def print_prices(cur):
    """
    Prints each product and its latest price information at each shop.
    Displays:
      - Product ID, barcode, brand, and name
      - For each shop with a price: shop ID, shop name, and latest price details
    """

    # Query to get all products with their details
    cur.execute('''
    SELECT product_id, barcode, brand, product_name
    FROM product
    ORDER BY product_id
    ''')

    products = cur.fetchall()

    if not products:
        print("No products found in the database.")
        return

    print("Products and Latest Prices at Each Shop:")

    # Loop through each product
    for product in products:
        product_id, barcode, brand, product_name = product
        print(f"Product ID: {product_id}, Barcode: {barcode}, Brand: {brand}, Name: {product_name}")

        # Query to get shops with price information for this product
        cur.execute('''
        SELECT 
            p.shop_id, 
            s.store_name, 
            p.price, 
            p.discount_price, 
            p.waste_discount_percentage, 
            p.report_date, 
            p.discount_valid_from, 
            p.discount_valid_to, 
            p.waste_valid_to
        FROM price p
        JOIN shop s ON p.shop_id = s.shop_id
        WHERE p.product_id = ?
        ORDER BY p.report_date DESC
        ''', (product_id,))

        prices = cur.fetchall()

        if not prices:
            print("  No price information available for this product.")
        else:
            # Loop through each shop price entry
            for price in prices:
                shop_id, store_name, base_price, discount_price, waste_discount_percentage, report_date, discount_valid_from, discount_valid_to, waste_valid_to = price
                
                print(f"  Shop ID: {shop_id}, Shop Name: {store_name}")
                print(f"    Base Price: {base_price}")
                if discount_price is not None:
                    print(f"    Discount Price: {discount_price} (Valid from {discount_valid_from} to {discount_valid_to})")
                else:
                    print("    Discount Price: None")
                
                if waste_discount_percentage is not None:
                    print(f"    Waste Discount Percentage: {waste_discount_percentage}% (Valid until {waste_valid_to})")
                else:
                    print("    Waste Discount Percentage: None")
                
                print(f"    Report Date: {report_date}")
                print("-" * 40)  # Separator for readability

    print("End of product price listing.")




def update_user_aura(con, cur):
    """
    Updates the 'aura' score for all users based on the following rules:
    - +50 for being the first to create a new product
    - +20 for updating an existing product
    - +10 for creating or updating the normal price of a product
    - +30 for creating or updating the discount price of a product
    - +100 for creating or updating a waste_discount_percentage (if not the
    default 0%)
    """

    try:
        # Reset aura points for all users
        cur.execute('UPDATE user SET aura_points = 0')

        # Calculate aura for creating new products (+50 for the first creation)
        cur.execute('''
            SELECT user_created, COUNT(product_id) * 50
            FROM product
            GROUP BY user_created
        ''')
        new_product_creations = cur.fetchall()

        for user_id, aura_points in new_product_creations:
            cur.execute('UPDATE user SET aura_points = aura_points + '
                        '? WHERE user_id = ?', (aura_points, user_id))

        # Calculate aura for updating existing products (+20 for updates to
        # products)
        cur.execute('''
            SELECT user_created, COUNT(product_id) * 20
            FROM product
            WHERE creation_date < (
                SELECT MAX(creation_date)
                FROM product
                GROUP BY barcode
                HAVING COUNT(barcode) > 1
            )
            GROUP BY user_created
        ''')
        product_updates = cur.fetchall()

        for user_id, aura_points in product_updates:
            cur.execute('UPDATE user SET aura_points = aura_points + ? '
                        'WHERE user_id = ?', (aura_points, user_id))

        # Calculate aura for creating or updating the normal price
        # of a product (+10)
        cur.execute('''
            SELECT user_created, COUNT(price_id) * 10
            FROM price
            WHERE price IS NOT NULL
            GROUP BY user_created
        ''')
        normal_price_updates = cur.fetchall()

        for user_id, aura_points in normal_price_updates:
            cur.execute('UPDATE user SET aura_points = aura_points + ? '
                        'WHERE user_id = ?', (aura_points, user_id))

        # Calculate aura for creating or updating the discount price (+30)
        cur.execute('''
            SELECT user_created, COUNT(price_id) * 30
            FROM price
            WHERE discount_price IS NOT NULL
            GROUP BY user_created
        ''')
        discount_price_updates = cur.fetchall()

        for user_id, aura_points in discount_price_updates:
            cur.execute('UPDATE user SET aura_points = aura_points + ? '
                        'WHERE user_id = ?', (aura_points, user_id))

        # Calculate aura for creating or updating waste_discount_percentage
        # (+100 if waste_discount_percentage is not 0%)
        cur.execute('''
            SELECT user_created, COUNT(price_id) * 100
            FROM price
            WHERE waste_discount_percentage > 0
            GROUP BY user_created
        ''')
        waste_discount_updates = cur.fetchall()

        for user_id, aura_points in waste_discount_updates:
            cur.execute('UPDATE user SET aura_points = aura_points + ? '
                        'WHERE user_id = ?', (aura_points, user_id))

        # Commit the updates
        con.commit()

        print("User aura points have been successfully updated.")
    
    except sqlite3.Error as e:
        print(f"Error updating user aura points: {e}")






def __haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two sets of GPS coordinates.
    """
    R = 6371  # Radius of Earth in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c  # Distance in kilometers

def find_closest_shops(cur, user_lat, user_lon, n):
    """
    Finds the 'n' closest shops to a given GPS coordinate (user_lat, user_lon).
    
    Parameters:
    - cur: SQLite cursor object
    - user_lat: Latitude of the user's location, e.g. 61.4494483
    - user_lon: Longitude of the user's location, e.g. 23.8559905
    - n: Number of closest shops to find
    
    Returns:
    - A list of tuples containing the shop ID and distance (in kilometers) for the 'n' closest shops.
    """
    try:
        # Query to retrieve shop IDs and GPS coordinates
        cur.execute('SELECT shop_id, location_gps FROM shop')
        shops = cur.fetchall()
        
        # List to hold shops with calculated distances
        shop_distances = []

        for shop_id, location_gps in shops:
            if location_gps:
                try:
                    # Parse the latitude and longitude from the shop's location_gps field
                    shop_lat, shop_lon = map(float, location_gps.split(','))
                    
                    # Calculate the distance using the Haversine formula
                    distance = __haversine(user_lat, user_lon, shop_lat, shop_lon)
                    
                    # Append the shop and its distance
                    shop_distances.append((shop_id, distance))
                
                except ValueError:
                    print(f"Invalid GPS format for shop_id {shop_id}: {location_gps}")
        
        # Sort shops by distance and select the closest 'n'
        shop_distances.sort(key=lambda x: x[1])
        closest_shops = shop_distances[:n]

        return closest_shops

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []