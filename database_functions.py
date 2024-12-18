from models import db, User, Aurapoints
from werkzeug.security import generate_password_hash
from sqlalchemy.sql import func, extract
import plotly.graph_objects as go
import hashlib
import time
from flask import render_template

# GLOBAL CONSTANTS 

NOT_ALLOWED_ERROR = "Not allowed"

def hash_token(token):
    """
    Hashes the token using SHA256.
    """
    return hashlib.sha256(token.encode()).hexdigest()

def get_user_by_reset_token(hashed_token):
    """
    Fetches a user by their reset token.
    """
    return User.query.filter_by(reset_token=hashed_token).first()

def is_reset_token_expired(expiration_time):
    """
    Checks if a reset token is expired.
    """
    current_time = int(time.time())
    return current_time > expiration_time

def clear_reset_token(user):
    """
    Clears the reset token and expiration from the user.
    """
    try:
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error clearing reset token: {e}")
        db.session.rollback()
        return False

def add_user(username, password, email, role):
    """
    Adds a new user to the user table.
    """
    try:
        hashed_password = generate_password_hash(password)  # Hash the password
        user = User(username=username, password=hashed_password, email=email, role=role)
        db.session.add(user)
        db.session.commit()
        print(f"User '{username}' with role '{role}' added successfully.")
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        db.session.rollback()
        return False

def update_user_username(user_id, new_username):
    """
    Updates the username of a user with the given user_id.
    """
    try:
        user = User.query.get(user_id)
        if user:
            user.username = new_username
            db.session.commit()
            print(f"Username for user ID {user_id} updated successfully.")
            return True
        else:
            print(f"User with ID {user_id} not found.")
            return False
    except Exception as e:
        print(f"Error updating username for user ID {user_id}: {e}")
        db.session.rollback()
        return False

def update_user_email(user_id, new_email):
    """
    Updates the email of a user with the given user_id.
    """
    try:
        user = User.query.get(user_id)
        if user:
            user.email = new_email
            db.session.commit()
            print(f"Email for user ID {user_id} updated successfully.")
            return True
        else:
            print(f"User with ID {user_id} not found.")
            return False
    except Exception as e:
        print(f"Error updating email for user ID {user_id}: {e}")
        db.session.rollback()
        return False

def remove_user(user_id, requester_id):
    """
    Removes a user if the requester is an admin or the user themselves.
    """
    requester = User.query.get(requester_id)
    if requester and (requester.role == 'admin' or requester_id == user_id):
        try:
            user_to_delete = User.query.get(user_id)
            if user_to_delete:
                db.session.delete(user_to_delete)
                db.session.commit()
                print(f"User with ID {user_id} has been removed.")
            else:
                print("User not found.")
        except Exception as e:
            print(f"Error removing user: {e}")
            db.session.rollback()
    else:
        print("Permission denied. Only admins or the user themselves can remove this user.")


from flask import session, flash
from werkzeug.security import check_password_hash
from sqlalchemy.exc import SQLAlchemyError

def authenticate_user(username, password):
    """
    Authenticates a user based on the provided username and password.
    """
    print(f"{username}, {password}")
    try:
        user = User.query.filter_by(username=username).first()
        print(f"{user}")
        if user:
            if check_password_hash(user.password, password):
                # Update last login timestamp
                user.last_login = db.func.current_timestamp()
                db.session.commit()
                
                # Store user_id in session for persistent authentication
                session['user_id'] = user.user_id
                print(f"Logged in user ID stored in session: {session['user_id']}")
                return True
            else:
                flash("Incorrect password", "error")
                return False
        flash("Username not found", "error")
        return False
    except SQLAlchemyError as e:
        flash(f"Database error: {e}", "error")
        db.session.rollback()
    return False


# Logout function to clear user from session
def logout_user():
    session.pop('user_id', None)


def confirm_access():
    """
    Checks if the user is logged in and returns their role.
    
    Returns:
    - The user's role if logged in, or None if not logged in.
    """
    user_id = session.get('user_id')
    if user_id:
        # Query the database for the user's role
        user = User.query.get(user_id)
        if user:
            return user.role  # Return the user's role if found
    return None  # Return None if user is not logged in
    


def print_users():
    """
    Prints all users and their information from the user table.
    """
    users = User.query.order_by(User.user_id).all()
    if users:
        print("All Users:")
        for user in users:
            print(f"User ID: {user.user_id}")
            print(f"Username: {user.username}")
            print(f"Role: {user.role}")
            print(f"Email: {user.email}")
            print(f"Aura Points: {user.aura_points}")
            print(f"Last Login: {user.last_login}")
            print(f"Creation Date: {user.creation_date}")
            print("-" * 40)
    else:
        print("No users found in the database.")


from models import Product

def add_product(product_name, weight_g, volume_l, barcode, category, esg_score, co2_footprint, brand, sub_brand, parent_company, information_links, gluten_free):
    """
    Adds a new product to the product table.
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            print(NOT_ALLOWED_ERROR)
            return
            
        product = Product(
            product_name=product_name,
            weight_g=weight_g,
            volume_l=volume_l,
            barcode=barcode,
            category=category,
            esg_score=esg_score,
            co2_footprint=co2_footprint,
            brand=brand,
            sub_brand=sub_brand,
            parent_company=parent_company,
            information_links=information_links,
            user_created=user_id,
            gluten_free=gluten_free
        )
        db.session.add(product)
        db.session.commit()
        print(f"Product '{product_name}' added successfully.")
    except Exception as e:
        print(f"Error adding product: {e}")
        db.session.rollback()


def remove_latest_product_version(barcode):
    """
    Deletes the latest version of a product if the user is an admin.
    """
    user_id = session.get('user_id')
    if not user_id:
        print(NOT_ALLOWED_ERROR)
        return
    
    user = User.query.get(user_id)
    if user and user.role == 'admin':
        latest_product = Product.query.filter_by(barcode=barcode).order_by(Product.creation_date.desc()).first()
        if latest_product:
            db.session.delete(latest_product)
            db.session.commit()
            print(f"Latest version of product with barcode {barcode} has been deleted.")
        else:
            print(f"No product found with barcode {barcode}.")
    else:
        print("Permission denied. Only admin users can delete products.")


def print_products():
    """
    Lists the latest versions of each product.
    """
    products = db.session.query(Product).distinct(Product.barcode).order_by(Product.creation_date.desc()).all()
    if products:
        print("Latest versions of all products:")
        for product in products:
            print(f"Product Name: {product.product_name}")
            print(f"Weight (g): {product.weight_g}")
            print(f"Volume (L): {product.volume_l}")
            print(f"Barcode: {product.barcode}")
            print(f"Category: {product.category}")
            print(f"ESG Score: {product.esg_score}")
            print(f"CO2 Footprint: {product.co2_footprint}")
            print(f"Brand: {product.brand}")
            print(f"Sub-brand: {product.sub_brand}")
            print(f"Parent Company: {product.parent_company}")
            print(f"Information Links: {product.information_links}")
            print(f"Gluten Free: {product.gluten_free}")
            print(f"Creation Date: {product.creation_date}")
            print("-" * 40)
    else:
        print("No products found.")


from models import Shop

def create_shop(store_name, store_chain, location_address, location_gps):
    """
    Creates a new shop in the database.
    """
    try:
        shop = Shop(store_name=store_name, store_chain=store_chain, location_address=location_address, location_gps=location_gps)
        db.session.add(shop)
        db.session.commit()
        print(f"Shop '{store_name}' created successfully.")
        return shop.shop_id
    except Exception as e:
        print(f"Error creating shop: {e}")
        db.session.rollback()
        return None


from models import WorksFor

def add_shopkeeper_to_shop(user_id, shop_id):
    """
    Adds a shopkeeper to a shop if the user has a shopkeeper role.
    """
    user = User.query.get(user_id)
    if user and user.role == 'shopkeeper':
        assignment = WorksFor(user_id=user_id, shop_id=shop_id)
        db.session.add(assignment)
        db.session.commit()
        print(f"User {user_id} has been added as a shopkeeper to shop {shop_id}.")
    else:
        print(f"User {user_id} is not a shopkeeper and cannot be added to a shop.")


from models import db, WorksFor

def remove_shopkeeper_from_shop(user_id, shop_id):
    """
    Removes a shopkeeper from a shop if they are currently assigned to it.
    """
    assignment = WorksFor.query.filter_by(user_id=user_id, shop_id=shop_id).first()
    if assignment:
        try:
            db.session.delete(assignment)
            db.session.commit()
            print(f"User {user_id} has been removed as a shopkeeper from shop {shop_id}.")
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
    else:
        print(f"User {user_id} is not currently assigned as a shopkeeper to shop {shop_id}.")


from models import Shop, WorksFor, User

def print_shops():
    """
    Prints all shops and their information, including assigned shopkeepers.
    """
    shops = Shop.query.all()
    if shops:
        print("All Shops and Assigned Shopkeepers:")
        for shop in shops:
            print(f"Shop ID: {shop.shop_id}")
            print(f"Store Name: {shop.store_name}")
            print(f"Store Chain: {shop.store_chain}")
            print(f"Location Address: {shop.location_address}")
            print(f"Location GPS: {shop.location_gps}")
            
            # Query shopkeepers for this shop
            shopkeepers = User.query.join(WorksFor).filter(WorksFor.shop_id == shop.shop_id).all()
            
            if shopkeepers:
                print("Assigned Shopkeepers:")
                for shopkeeper in shopkeepers:
                    print(f"  - Shopkeeper ID: {shopkeeper.user_id}, Username: {shopkeeper.username}")
            else:
                print("  No shopkeepers assigned.")
                
            print("-" * 40)
    else:
        print("No shops found in the database.")


from models import Price

def add_price(product_id, shop_id, price, discount_price=None, waste_discount_percentage=None, 
              discount_valid_from=None, discount_valid_to=None, waste_valid_to=None, waste_quantity=None):
    """
    Adds a new price entry to the price table.
    """
    user_id = session.get('user_id')
    if not user_id:
        print(NOT_ALLOWED_ERROR)
        return
    
    if waste_quantity not in (None, 'Few', 'Moderate', 'Many'):
        print("Error: waste_quantity must be 'Few', 'Moderate', or 'Many'.")
        return

    try:
        new_price = Price(
            product_id=product_id,
            shop_id=shop_id,
            price=price,
            discount_price=discount_price,
            waste_discount_percentage=waste_discount_percentage,
            discount_valid_from=discount_valid_from,
            discount_valid_to=discount_valid_to,
            waste_valid_to=waste_valid_to,
            waste_quantity=waste_quantity,
            user_created=user_id
        )
        db.session.add(new_price)
        db.session.commit()
        print(f"Price for product {product_id} at shop {shop_id} added successfully.")
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()

def get_user_by_id(user_id):
    """
    Fetches a user by their ID.
    """
    return User.query.get(user_id)

def check_current_password(stored_password, input_password):
    """
    Verifies if the input password matches the stored password hash.
    """
    return check_password_hash(stored_password, input_password)

def validate_new_password(new_password, confirm_password):
    """
    Validates the new password against certain rules.
    Returns an error message if invalid, otherwise None.
    """
    MIN_PASSWORD_LENGTH = 10
    if new_password != confirm_password:
        return "New password and confirmation do not match"
    if len(new_password) < MIN_PASSWORD_LENGTH:
        return "New password must be at least 10 characters long"
    if not any(char.isupper() for char in new_password):
        return "New password must contain at least one uppercase letter"
    if not any(char.isdigit() for char in new_password):
        return "New password must contain at least one number"
    if not any(char in "!@#$%^&*()-_+=[]{}|\\:;\"'<>,.?/~`" for char in new_password):
        return "New password must contain at least one special character"
    return None

def update_user_password(user, new_password):
    """
    Updates the user's password in the database.
    Returns True on success, False otherwise.
    """
    try:
        user.password = generate_password_hash(new_password)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error updating password: {e}")
        db.session.rollback()
        return False

def remove_price(price_id, shop_id):
    """
    Removes a price entry if the user is an admin or a shopkeeper of the shop where the price is listed.
    """
    user_id = session.get('user_id')
    if not user_id:
        print(NOT_ALLOWED_ERROR)
        return
    
    user = User.query.get(user_id)
    if user and user.role == 'admin':
        # Admin can delete any price
        price = Price.query.get(price_id)
        if price:
            try:
                db.session.delete(price)
                db.session.commit()
                print(f"Price with ID {price_id} has been removed by admin.")
            except Exception as e:
                print(f"Error: {e}")
                db.session.rollback()
        else:
            print("Price not found.")
    else:
        # Check if the user is a shopkeeper for the given shop
        is_shopkeeper = WorksFor.query.filter_by(user_id=user_id, shop_id=shop_id).first()
        if is_shopkeeper:
            price = Price.query.get(price_id)
            if price:
                try:
                    db.session.delete(price)
                    db.session.commit()
                    print(f"Price with ID {price_id} has been removed by shopkeeper.")
                except Exception as e:
                    print(f"Error: {e}")
                    db.session.rollback()
            else:
                print("Price not found.")
        else:
            print("Permission denied. Only admins or shopkeepers of the shop can remove prices.")


from datetime import datetime

def get_current_price(product_id, shop_id):
    """
    Retrieves the current base price and effective discount price for a given product and shop.
    """
    current_time = datetime.now()

    # Retrieve the latest base price for the product at the shop
    latest_price_entry = Price.query.filter_by(product_id=product_id, shop_id=shop_id) \
                                    .order_by(Price.report_date.desc()) \
                                    .first()
    if not latest_price_entry:
        print("No base price found for the given product and shop.")
        return None, None

    base_price = latest_price_entry.price
    effective_discount_price = base_price

    # Retrieve active campaign discount price, if available
    campaign_discount_price = Price.query.filter(
        Price.product_id == product_id,
        Price.shop_id == shop_id,
        Price.discount_price != None,
        Price.discount_valid_from <= current_time,
        Price.discount_valid_to > current_time
    ).order_by(Price.report_date.desc()).first()

    if campaign_discount_price:
        effective_discount_price = campaign_discount_price.discount_price

    # Apply waste discount if available
    waste_discount = Price.query.filter(
        Price.product_id == product_id,
        Price.shop_id == shop_id,
        Price.waste_discount_percentage != None,
        Price.waste_valid_to > current_time
    ).order_by(Price.report_date.desc()).first()

    if waste_discount:
        effective_discount_price *= (1 - waste_discount.waste_discount_percentage / 100)

    return base_price, effective_discount_price


def print_prices():
    """
    Prints each product and its latest price information at each shop.
    """
    products = Product.query.all()

    if not products:
        print("No products found in the database.")
        return

    print("Products and Latest Prices at Each Shop:")

    for product in products:
        print(f"Product ID: {product.product_id}, Barcode: {product.barcode}, Brand: {product.brand}, Name: {product.product_name}")
        
        # Query prices for this product at each shop
        latest_prices = Price.query.filter_by(product_id=product.product_id) \
                                   .order_by(Price.report_date.desc()).all()

        if not latest_prices:
            print("  No price information available for this product.")
        else:
            for price in latest_prices:
                shop = Shop.query.get(price.shop_id)
                print(f"  Shop ID: {shop.shop_id}, Shop Name: {shop.store_name}")
                print(f"    Base Price: {price.price}")
                print(f"    Discount Price: {price.discount_price} (Valid from {price.discount_valid_from} to {price.discount_valid_to})" if price.discount_price else "    Discount Price: None")
                print(f"    Waste Discount Percentage: {price.waste_discount_percentage}% (Valid until {price.waste_valid_to})" if price.waste_discount_percentage else "    Waste Discount Percentage: None")
                print(f"    Report Date: {price.report_date}")
                print("-" * 40)

    print("End of product price listing.")

def update_user_aura(user_id):
    try:
        user = User.query.get(user_id)
        if user is None:
            print(f"User with ID {user_id} not found.")
            return

        # Query and get the results as list
        user_aurapoints = Aurapoints.query.filter_by(user_id=user.user_id).order_by(Aurapoints.timestamp.desc()).all()
        
        if len(user_aurapoints) == 0:
            print(f"No aura points found for user with ID {user_id}.")
            return 0, 0, 0, 0, ""

        difference = 0
        total_points = user_aurapoints[0].points
        print("POINTS " + str(total_points))

        # Make sure there are at least two values
        if len(user_aurapoints) > 1:
            second_last_aurapoint = user_aurapoints[1]
            difference = total_points - second_last_aurapoint.points
            print(f"Toiseksi viimeinen piste: {second_last_aurapoint.points}, Aikaleima: {second_last_aurapoint.timestamp}")
        else:
            print("Ei ole tarpeeksi lisättyjä pisteitä.")

        points_current_month = user_aurapoints[0].points_current_month
        points_last_month = user_aurapoints[0].points_last_month

        timestamps = [point.timestamp for point in user_aurapoints]
        points = [point.points for point in user_aurapoints]

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=timestamps, y=points, mode='lines+markers', name="Aura Points"))

        fig.update_layout(
            title=f"{user.username}'s Aura Points",
            xaxis_title="Time",
            yaxis_title="Points",
            xaxis_tickangle=45
        )

        # Render graph in HTML format
        graph_html = fig.to_html(full_html=False)

        return total_points, difference, points_current_month, points_last_month, graph_html

    except Exception as e:
        print(f"Error updating user aura points: {e}")
        db.session.rollback()
        return 0, 0, 0, 0, ""

import math

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

def find_closest_shops(user_lat, user_lon, n):
    """
    Finds the 'n' closest shops to a given GPS coordinate (user_lat, user_lon).
    """
    shops = Shop.query.all()
    shop_distances = []

    for shop in shops:
        try:
            shop_lat, shop_lon = map(float, shop.location_gps.split(','))
            distance = __haversine(user_lat, user_lon, shop_lat, shop_lon)
            shop_distances.append((shop.shop_id, distance))
        except (ValueError, TypeError):
            print(f"Invalid GPS format for shop ID {shop.shop_id}: {shop.location_gps}")

    shop_distances.sort(key=lambda x: x[1])
    return shop_distances[:n]


