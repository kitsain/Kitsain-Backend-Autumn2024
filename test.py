from flask import Flask, json, render_template, request, redirect, url_for, flash, jsonify, session
from flask_mail import Mail, Message
from sqlalchemy import desc
from flask import session
import hashlib
import secrets
import time
from routes.products import add_product_from_html, remove_product, update_product,search_discount, add_product_detail, edit_product_detail
from routes.shops import add_shop, remove_shop
from routes.filtering import filter_shops, filter_products
from routes.users import modify_user, add_user, remove_user, modify_shopkeepers
from get_data import fetch_product_from_OFF
from models import db, Product, Shop, User, Price, Aurapoints, WorksFor
from werkzeug.security import generate_password_hash, check_password_hash
import database_functions as dbf

app = Flask(__name__)
app.secret_key = 'asdhfauisdhfuhi'  # Required for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///commerce_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''

mail = Mail(app)

# Global constants
MIN_PASSWORD_LENGHT = 10

# Salasanalinkki vanhenee tunnin päästä
EXPIRATION_LIMIT_IN_SECONDS = 3600

db.init_app(app)

def add_user(username, password, email, role):
    try:
        hashed_password = generate_password_hash(password)
        user = User(username=username, password=hashed_password, email=email, role=role)
        db.session.add(user)
        db.session.commit()
        print(f"User '{username}' with role '{role}' added successfully.")
        return True
    except Exception as e:
        print(f"Error adding user: {e}")
        db.session.rollback()
        return False

def add_aurapoints(user_id, points, points_current_month, points_last_month, reason=None):
    try:
        aurapoints = Aurapoints(user_id=user_id, points=points, points_current_month=points_current_month, 
                                points_last_month=points_last_month, reason=reason)
        db.session.add(aurapoints)
        db.session.commit()
        print(f"Aurapoints for user ID {user_id} added successfully.")
        return True
    except Exception as e:
        print(f"Error adding aurapoints: {e}")
        db.session.rollback()
        return False

def add_shop(store_name, location_address, user_created):
    try:
        shop = Shop(store_name=store_name, location_address=location_address, user_created=user_created)
        db.session.add(shop)
        db.session.commit()
        print(f"Shop '{store_name}' added successfully.")
        return True
    except Exception as e:
        print(f"Error adding shop: {e}")
        db.session.rollback()
        return False

def add_works_for(user_id, shop_id):
    try:
        works_for = WorksFor(user_id=user_id, shop_id=shop_id)
        db.session.add(works_for)
        db.session.commit()
        print(f"User ID {user_id} works for shop ID {shop_id}.")
        return True
    except Exception as e:
        print(f"Error adding works_for: {e}")
        db.session.rollback()
        return False

def add_product(product_name, weight_g, volume_l, barcode, category, gluten_free, esg_score, co2_footprint, brand, user_created):
    try:
        product = Product(product_name=product_name, weight_g=weight_g, volume_l=volume_l, barcode=barcode, 
                          category=category, gluten_free=gluten_free, esg_score=esg_score, co2_footprint=co2_footprint,
                          brand=brand, user_created=user_created)
        db.session.add(product)
        db.session.commit()
        print(f"Product '{product_name}' added successfully.")
        return True
    except Exception as e:
        print(f"Error adding product: {e}")
        db.session.rollback()
        return False

def add_price(product_id, shop_id, price, discount_price=None, waste_discount_percentage=None, waste_quantity=None):
    try:
        price_entry = Price(product_id=product_id, shop_id=shop_id, price=price, 
                            discount_price=discount_price, waste_discount_percentage=waste_discount_percentage, 
                            waste_quantity=waste_quantity)
        db.session.add(price_entry)
        db.session.commit()
        print(f"Price for product ID {product_id} in shop ID {shop_id} added successfully.")
        return True
    except Exception as e:
        print(f"Error adding price: {e}")
        db.session.rollback()
        return False


with app.app_context():
    # Create all tables
    db.create_all()

    # Add test data
    if not User.query.first():
        add_user('john', 'password123', 'john.doe@example.com', 'user')
        add_user('jane_', 'password456', 'jane.smith@example.com', 'shopkeeper')
        add_user('auser', 'adminpass', 'auser@example.com', 'admin')

        add_user('admin', 'admin', 'admin@example.com', 'admin')
        add_user('user', 'user', 'user@example.com', 'user')

        add_user('jane_2', '12', 'jane2.smith@example.com', 'user')
        add_user('auser2', '13', 'auser2@example.com', 'user')
        add_user('john3', '14', 'john3.doe@example.com', 'user')
        add_user('jane_3', '15', 'jane3.smith@example.com', 'shopkeeper')
        add_user('auser3', '16', 'auser3@example.com', 'shopkeeper')
        add_user('john4', '17', 'john4.doe@example.com', 'shopkeeper')
        add_user('jane_4', '18', 'jane4.smith@example.com', 'user')
        add_user('auser4', '19', 'auser4@example.com', 'user')
        print("Testikäyttäjät lisätty.")
    else:
        print("Testidata on jo olemassa, ei lisätä uudelleen.")
    
    if not Aurapoints.query.first():
        add_aurapoints(1, 100, 50, 40)
        add_aurapoints(1, 110, 50, 40)

        add_aurapoints(2, 200, 10, 100)
        add_aurapoints(2, 200, 10, 100)

        add_aurapoints(3, 100, 50, 40)

        add_aurapoints(4, 200, 120, 100)
        add_aurapoints(4, 250, 120, 100)
        add_aurapoints(4, 280, 120, 100)
        print("Testipisteet lisätty käyttäjille.")
    else:
        print("Testidata on jo olemassa, ei lisätä uudelleen.")


    if not Shop.query.first():
        add_shop('TechStore', '123 Tech St, City', 2)
        add_shop('GroceryMart', '456 Grocery Ave, Town', 1)
        print("Testikaupat lisätty.")
    else:
        print("Testidata on jo olemassa, ei lisätä uudelleen.")


    if not WorksFor.query.first():

        add_works_for(2, 1)  # Jane works at TechStore
        print("Testityöskentelee lisätty.")
    else:
        print("Testidata on jo olemassa, ei lisätä uudelleen.")

    if not Product.query.first():

        add_product('Organic Apple', 150, 0.2, '1234567890123', 'Fruit', True, 'A', 'Low', 'GreenFarms', 1)
        add_product('Laptop Model X', 2000, 0.002, '9876543210987', 'Electronics', False, 'B', 'High', 'TechCorp', 2)
        print("Testituote lisätty.")
    else:
        print("Testidata on jo olemassa, ei lisätä uudelleen.")

    if not Price.query.first():

        add_price(1, 1, 1.99, waste_quantity='Few')
        add_price(2, 2, 1499.99, discount_price=1399.99)
        print("Testihinta lisätty.")
    else:
        print("Testidata on jo olemassa, ei lisätä uudelleen.")

    # Start Flask app
    app.run(debug=True)