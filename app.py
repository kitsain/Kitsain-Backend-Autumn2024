from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, text
from datetime import datetime
from sqlalchemy import desc
from flask import session
import hashlib
import secrets
import time
from routes.products import add_product_from_html, remove_product, update_product, get_products, search_discount, add_product_detail, edit_product_detail
from routes.shops import add_shop, remove_shop
from routes.filtering import filter_shops, filter_products
from routes.users import modify_user, add_user, remove_user, modify_shopkeepers
import sqlite3
from models import db, Product, Shop, User, Price

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

@app.route('/update_password', methods=['GET', 'POST'])
def update_password():

    if request.method == 'POST': 
        current_password_field = request.form.get('current_password')
        new_password_field = request.form.get('new_password')
        new_password_again_field = request.form.get('new_password_again')

        hashed_current_password_field = hashlib.sha256(current_password_field.encode()).hexdigest()

        con = sqlite3.connect("commerce_data.db")
        cur = con.cursor()

        # if hashed_current_password_field != 

        cur.execute("""
        SELECT password
        FROM user
        WHERE password = ?
    """, (hashed_current_password_field,))
        password_saved_in_the_database = cur.fetchone()

        if hashed_current_password_field != password_saved_in_the_database:
            flash("The current password your entered was wrong. Please try again.")
            return render_template('my_profile_page.html')
        
        else:
            print("Salasana oli sama!")

@app.route('/login', methods=['GET', 'POST'])
def login():
    db.drop_all()
    db.create_all()
    dbf.add_user("admin", "admin", "admin@email.com", "admin")
    
    if request.method == 'POST':
        username = request.form.get('username')  # Gets the username
        password = request.form.get('password')  # Gets the password
        
        if dbf.authenticate_user(username, password):
            return redirect(url_for('index'))
    
    return render_template('login.html')


@app.route('/email', methods=['GET', 'POST'])
def email():
    if request.method == 'POST':

        email = request.form.get('email')
        emailagain = request.form.get('emailagain')

        print("Email: ", email)

        con = sqlite3.connect("commerce_data.db")
        cur = con.cursor()
        cur.execute('SELECT * FROM user WHERE email = ?', (email,))
        user = cur.fetchone()

        if email != emailagain:
            flash("Error: The email fields were not equal", category="error")
            session['email'] = email
            session['emailagain'] = emailagain
            return redirect(url_for('email'))

        if not user: 
            print("Käyttäjä: ", user)
            print("Sähköposti: ", email)
            print("Käyttäjää ei löytynyt")
            flash("Email not found in the system", category="error")
            return redirect(url_for('email'))
        
        reset_token = secrets.token_urlsafe(32)
        session['reset_token'] = reset_token

        hashed_token = hashlib.sha256(reset_token.encode()).hexdigest()
        expiration_time = int(time.time()) + EXPIRATION_LIMIT_IN_SECONDS

        # Save token to the database (simple example using session)
        # In production, consider a separate table for tokens with expiration
        cur.execute('UPDATE user SET reset_token = ?, reset_token_expiry = ? WHERE email = ?', (hashed_token, expiration_time, email))

        # Send email
        reset_link = url_for('reset_password', token=reset_token, _external=True)
        msg = Message("Kitsain password reset request",
                      sender="your_email@example.com",
                      recipients=[email])
        msg.body = f"Hello!\n\nThank you for using Kitsain. You can reset your password with the following link: {reset_link} \n\nPlease note that the preceding link expires after 1 hour and cannot be reused for resetting the password.\n\nSincerely,\nKitsain"
        mail.send(msg)

        # session.pop('email', None)
        # session.pop('emailagain', None)
        con.commit()
        con.close()
        return render_template("passwordSetConfirmation.html")
    
    email = session.get('email', '')
    emailagain = session.get('emailagain', '')
    return render_template("newPassword.html", email=email, emailagain=emailagain)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):

    hashed_token = hashlib.sha256(token.encode()).hexdigest()
    print("Hashed token: ", hashed_token)

    conn = sqlite3.connect('commerce_data.db')
    cur = conn.cursor()

    if request.method == 'GET': 
        
        cur.execute("""
        SELECT reset_token_expiry
        FROM user
        WHERE reset_token = ?
    """, (hashed_token,))
        result = cur.fetchone()

        # Jos koko tokenia ei löydy ylipäätään, se on vanhentunut
        if not result: 
            return render_template('resetLinkExpired.html', token=token)
        
        expiration_time = result[0]
        current_time = int(time.time())

        if current_time > expiration_time: 
            return render_template('resetLinkExpired.html', token=token)

    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('newpassword')

        if token is None:
            print("Token puuttuu!")
            raise ValueError("Token cannot be None")
        
        else: 
            print("Päästiin Token-tarkituksesta ohi!")

        if len(new_password) < MIN_PASSWORD_LENGHT:
            flash("Error: New password is too short (min 10 chars)")
            return render_template('resetPassword.html', token=token)

        elif new_password != confirm_password:
            flash("Error: The password fields were not equal", category="error")
            return render_template('resetPassword.html', token=token)
        
        has_capital = any(char.isupper() for char in new_password)

        if not has_capital: 
            flash("Error: Your password must have at least one capital letter.")
            return render_template('resetPassword.html', token=token)
        
        special_characters = "!@#$%^&*()-_+=[]{}|\\:;\"'<>,.?/~`"

        has_special = any(char in special_characters for char in new_password)

        if not has_special: 
            flash("Error: Your password must have at least one special character.")
            return render_template('resetPassword.html', token=token)
        
        has_numbers = any(char.isdigit() for char in new_password)

        if not has_numbers:
            flash("Error: Your password must have at least one number.")
            return render_template('resetPassword.html', token=token)
        
        print("New passwordin arvo: ", new_password)
        print("Confirm passwordin arvo: ", confirm_password)

        # Update password in the database (example with SQLite)
        try:
            conn = sqlite3.connect('commerce_data.db')
            cur = conn.cursor()
            cur.execute("""
                UPDATE user
                SET password = ?
                WHERE reset_token = ?
            """, (dbf.generate_password_hash(new_password), hashed_token))
            conn.commit()
            cur.execute("""
                UPDATE user
                SET reset_token = NULL
                WHERE reset_token = ?
            """, (hashed_token,))
            conn.commit()
            conn.close()

            session.pop(new_password, None)
            session.pop(confirm_password, None)

        except sqlite3.IntegrityError as e:
            print(f"Database error: {e}")
            return "Database error occurred", 500

        return render_template('passwordSetSuccessfully.html')

    return render_template('resetPassword.html', token=token)

@app.route('/forgot_password')
def forgot_password():
    return render_template('newPassword.html')

def add_hardcoded_user():
    with app.app_context():
        db.create_all()  # Ensures tables are created

        # Create a hard-coded user
        hardcoded_user = User(
            username="hardcoded_user",
            password="securepassword123",  # You should hash the password
            email="user@example.com",
            role="admin",
            aura_points=100,
        )

        # Add the user to the session
        db.session.add(hardcoded_user)

        # Commit the changes to the database
        try:
            db.session.commit()
            print("Hard-coded user added successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding hard-coded user: {e}")

# page rendering

@app.route('/index')
def index():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
    
    # Retrieve the five latest products, assuming Product has a 'created_at' or 'added_date' field
    products = (Product).query.order_by(desc(Product. creation_date)).limit(2).all()
    shops = Shop.query.all()
    users = User.query.all()
    shopkeepers_data = {shop.shop_id: [wf.user.username for wf in shop.works_for] for shop in shops}
    closest_shops = None

    return render_template('index.html', products=products, shops=shops, shopkeepers_data=shopkeepers_data, users=users, results=None, query=None, closest_shops=None)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/products_page', methods=['POST', 'GET'])
def products_page():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
    
    products = db.session.query(Product).outerjoin(Price).outerjoin(Shop).all()

    

    shops = Shop.query.all()
    return render_template('products_page.html', products=products, shops=shops)

@app.route('/shops_page')
def shops_page():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
    
    shops = (Shop).query.all() 
    shopkeepers_data = {shop.shop_id: [wf.user.username for wf in shop.works_for] for shop in shops}
    return render_template('shops_page.html', shops = shops, shopkeepers_data=shopkeepers_data)

@app.route('/users_page')
def users_page():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
    
    users = (User).query.all()
    shops = (Shop).query.all()  
    products = (Product).query.all()
    shopkeepers_data = {shop.shop_id: [wf.user.username for wf in shop.works_for] for shop in shops} 
    return render_template('users_page.html', products=products, shops=shops, shopkeepers_data=shopkeepers_data, users=users)


@app.route('/my_profile_page')
def my_profile_page():
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))

    user_id = session.get('user_id')  # Get the logged-in user's ID
    if not user_id:
        return redirect(url_for('login'))  # Redirect if no user is logged in

    user = User.query.get(user_id)  # Fetch user data from the database
    if not user:
        flash("User not found.", category="error")
        return redirect(url_for('login'))
    
    users = (User).query.all()
    shops = (Shop).query.all()
    shopkeepers_data = {shop.shop_id: [wf.user.username for wf in shop.works_for] for shop in shops}
    
    # Pass the user's data to the template
    return render_template('my_profile_page.html', user=user, users=users, shops=shops, shopkeepers_data=shopkeepers_data)

# routes.products

@app.route('/add_product', methods=['POST'])
def add_product_method():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
        
    return add_product_from_html()

@app.route('/add_product_detail', methods=['POST'])
def add_product_detail_method():
        # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
        
    return add_product_detail()

@app.route('/edit_product_detail', methods=['POST', 'PUT'])
def edit_product_detail_method():
        # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
        
    return edit_product_detail()

@app.route('/remove_product/<int:product_id>', methods=['POST'])
def remove_product_method(product_id):
    # Check access rights
    if dbf.confirm_access() != "admin":
        return redirect(url_for('login'))
    
    return remove_product(product_id)

@app.route('/update_product', methods=['POST', 'PUT'])
def update_product_method():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
    
    return update_product()

@app.route('/get_products', methods=['GET'])
def get_products_method():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
    
    return get_products()

import csv
from flask import session, jsonify, request
import os

# Define the file path where the CSV will be saved
CSV_FILE_PATH = 'routes/product_data.csv'

@app.route('/save_product_data', methods=['POST'])
def save_product_data():
    data = request.get_json()

    print("DATA:", data)
    
    # Retrieve all the fields from the request
    barcode = data.get('barcode')
    product_name = data.get('product_name')
    shop = data.get('shop')
    price = data.get('price')
    discount_price = data.get('discount_price')
    discount_valid_from = data.get('discount_valid_from')
    discount_valid_to = data.get('discount_valid_to')
    waste_discount = data.get('waste_discount')
    expiration_date = data.get('expiration_date')
    product_amount = data.get('product_amount')

    # Check if all necessary data is provided
    if barcode and product_name and shop and price and discount_price and discount_valid_from and discount_valid_to and waste_discount and expiration_date and product_amount:
        try:
            # Append the product data to the CSV file without writing the header
            with open(CSV_FILE_PATH, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    barcode, product_name, shop, price, discount_price,
                    discount_valid_from, discount_valid_to, waste_discount,
                    expiration_date, product_amount
                ])  # Write the data row

            print("Product data saved to CSV.")
            
            # Return a JSON response with the product data
            return jsonify({
                "message": "Product data received and saved",
                "barcode": barcode,
                "product_name": product_name,
                "shop": shop,
                "price": price,
                "discount_price": discount_price,
                "discount_valid_from": discount_valid_from,
                "discount_valid_to": discount_valid_to,
                "waste_discount": waste_discount,
                "expiration_date": expiration_date,
                "product_amount": product_amount
            })
        
        except Exception as e:
            print(f"Error saving product data to CSV: {e}")
            return jsonify({"message": "Error saving data"}), 500
    
    else:
        return jsonify({"message": "Missing data"}), 400


# routes.shops

@app.route('/add_shop', methods=['POST'])
def add_shop_method():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
    
    return add_shop()

@app.route('/remove_shop/<int:shop_id>', methods=['POST'])
def remove_shop_method(shop_id):
    # Check access rights
    if dbf.confirm_access() != "admin":
        return redirect(url_for('login'))
    
    return remove_shop(shop_id)

# routes.users

@app.route('/add_user', methods=['POST'])
def add_user_method():
    return add_user()

@app.route('/modify_users/<int:user_id>', methods=['GET', 'POST'])
def modify_user_method(user_id):
    # Check access rights
    if dbf.confirm_access() != "admin":
        return redirect(url_for('login'))
    
    return modify_user(user_id)

@app.route('/remove_user/<int:user_id>', methods=['GET', 'POST'])
def remove_user_method(user_id):
    # Check access rights
    if dbf.confirm_access() != "admin":
        return redirect(url_for('login'))
    
    return remove_user(user_id)

@app.route('/modify_shopkeepers/<int:shop_id>', methods=['GET', 'POST'])
def modify_shopkeepers_method(shop_id):
    # Check access rights
    if dbf.confirm_access() != "admin":
        return redirect(url_for('login'))
    
    return modify_shopkeepers(shop_id)

# routes.filtering

@app.route('/filter_shops', methods=['GET', 'POST'])
def filter_shops_method():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
    
    return filter_shops

@app.route('/filter_products', methods=['GET', 'POST'])
def filter_products_method():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
    
    return filter_products()

@app.route('/search_discounts', methods=['GET', 'POST'])
def search_discount_method():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
    
    return search_discount()


if __name__ == '__main__':
    #add_hardcoded_user()
    app.run(debug=True)
