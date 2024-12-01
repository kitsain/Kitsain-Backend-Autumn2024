from flask import Flask, json, render_template, request, redirect, url_for, flash, jsonify, session
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
from get_data import fetch_product_from_OFF
import sqlite3
from models import db, Product, Shop, User, Price, Aurapoints, WorksFor
from sqlalchemy.sql import func, extract
from pprint import pprint

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

@app.route('/change_password', methods=['POST'])
def change_password():
        
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        flash("User not found", "error")
        return redirect(url_for('login'))

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not dbf.check_password_hash(user.password, current_password):
        flash("Current password is incorrect", "error")
        return redirect(url_for('my_profile_page'))

    # Validate new password
    if len(new_password) < 10:
        flash("New password must be at least 10 characters long", "error")
        return redirect(url_for('my_profile_page'))

    if new_password != confirm_password:
        flash("New password and confirmation do not match", "error")
        return redirect(url_for('my_profile_page'))

    if not any(char.isupper() for char in new_password):
        flash("New password must contain at least one uppercase letter", "error")
        return redirect(url_for('my_profile_page'))

    if not any(char.isdigit() for char in new_password):
        flash("New password must contain at least one number", "error")
        return redirect(url_for('my_profile_page'))

    if not any(char in "!@#$%^&*()-_+=[]{}|\\:;\"'<>,.?/~`" for char in new_password):
        flash("New password must contain at least one special character", "error")
        return redirect(url_for('my_profile_page'))

    # Update the password
    print("USER RIVILLÄ 143", user)
    user.password = dbf.generate_password_hash(new_password)
    db.session.commit()

    flash("Password changed successfully", category="success")
    return redirect('my_profile_page')

@app.route('/update_profile_info', methods=['POST'])
def update_profile_info():
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in to update your profile", "error")
        return redirect(url_for('login'))

    new_email = request.form.get('email')
    new_username = request.form.get('username')

    if new_username:
        if dbf.update_user_username(user_id, new_username):
            flash("Username updated successfully", "success")
        else:
            flash("Error updating username", "error")
    else:
        flash("Username cannot be empty", "error")

    if new_email:
        if dbf.update_user_email(user_id, new_email):
            flash("Email updated successfully", "success")
        else:
            flash("Error updating email", "error")
    else:
        flash("Email cannot be empty", "error")

    return redirect(url_for('my_profile_page'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Uncomment these only to reset database:
    # db.drop_all()
    # db.create_all()
    # dbf.add_user("admin", "admin", "admin@email.com", "admin")
    
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

        user = User.query.filter_by(email=email).first()

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
        user.reset_token = hashed_token
        user.reset_token_expiration = expiration_time
        db.session.commit()

        # Send email
        reset_link = url_for('reset_password', token=reset_token, _external=True)
        msg = Message("Kitsain password reset request",
                      sender="your_email@example.com",
                      recipients=[email])
        msg.body = f"Hello!\n\nThank you for using Kitsain. You can reset your password with the following link: {reset_link} \n\nPlease note that the preceding link expires after 1 hour and cannot be reused for resetting the password.\n\nSincerely,\nKitsain"
        mail.send(msg)

        return render_template("passwordSetConfirmation.html")
    
    email = session.get('email', '')
    emailagain = session.get('emailagain', '')
    return render_template("newPassword.html", email=email, emailagain=emailagain)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):

    hashed_token = hashlib.sha256(token.encode()).hexdigest()
    print("Hashed token: ", hashed_token)

    user = User.query.filter_by(reset_token=hashed_token).first()

    if request.method == 'GET': 

        # Jos koko tokenia ei löydy ylipäätään, se on vanhentunut
        if not user: 
            return render_template('resetLinkExpired.html', token=token)
        
        expiration_time = user.reset_token_expiration
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

        if user: 
            user.password = dbf.generate_password_hash(new_password)
            user.reset_token = None
            db.session.commit()

            session.pop(new_password, None)
            session.pop(confirm_password, None)

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

    return render_template('index.html', products=products, shops=shops, shopkeepers_data=shopkeepers_data, users=users, get_product_image=get_product_image, results=None, query=None, closest_shops=None)

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
    return render_template('products_page.html', products=products, shops=shops, get_product_image=get_product_image)


def get_product_image(product):
    """
    Extract the product image URL from information_links or return None.
    """
    try:
        if isinstance(product, dict):
            information_links = product.get("information_links", None)
        else:
            information_links = getattr(product, "information_links", None)
        
        if isinstance(information_links, str):
            information_links = json.loads(information_links.replace("'", '"'))

        return information_links.get("product_image_url", None) if information_links else None
    except Exception as e:
        print(f"Error processing product information_links: {e}")
        return None



@app.route('/fetch_product_details/<barcode>', methods=['GET'])
def fetch_product_details(barcode):
    """
    Fetch product details from OpenFoodFacts and return as JSON response.
    """
    try:
        product_data = fetch_product_from_OFF(barcode)

        return jsonify(product_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/shops_page')
def shops_page():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
    
    shops = (Shop).query.all() 

    shopkeepers_data = {}

    if shops:
        for shop in shops:
            shopkeepers = User.query.join(WorksFor).filter(WorksFor.shop_id == shop.shop_id).all()
            shopkeepers_data[shop.shop_id] = [shopkeepers]


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
    if dbf.confirm_access() is None:
        return redirect(url_for('login'))

    user_id = session.get('user_id')  # Get the logged-in user's ID
    if not user_id:
        return redirect(url_for('login'))  # Redirect if no user is logged in

    user = User.query.get(user_id)  # Fetch user data from the database
    if not user:
        flash("User not found.", category="error")
        return redirect(url_for('login'))

    print(f"Käyttäjä löytyi: {user.username}, ID: {user_id}")

    # Fetch all users, shops and Aura statistics
    users = User.query.all()
    shops = Shop.query.all()
    shopkeepers_data = {shop.shop_id: [wf.user.username for wf in shop.works_for] for shop in shops}

    total_points = 0
    recently_added_points = 0
    current_month_points = 0
    last_month_points = 0
    graph_html = ""

    total_points, recently_added_points, current_month_points, last_month_points, graph_html = dbf.update_user_aura(user_id)
    
    difference_between_months = current_month_points - last_month_points

    stats = {
        'total_points': total_points,
        'recently_added_points': recently_added_points,
        'current_month_points': current_month_points,
        'difference_between_months': difference_between_months
    }

    print("STATS: ", stats)
    products = (
        Product.query.filter(Product.user_created == user_id)  
        .order_by(desc(Product.creation_date)) 
        .limit(3) 
        .all()
    )

    # Pass the user's data to the template
    return render_template(
        'my_profile_page.html',
        user=user,
        users=users,
        products=products,
        shops=shops,
        shopkeepers_data=shopkeepers_data,
        get_product_image=get_product_image,
        stats=stats,
        graph_html=graph_html
    )

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

CSV_FILE_PATH = 'routes/product_data.csv'

@app.route('/save_product_data', methods=['POST'])
def save_product_data():
    data = request.get_json()

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

    if not (barcode and product_name and shop and price):
        return jsonify({"message": "Missing required fields"}), 400

    product_data = [
        barcode,
        product_name,
        shop,
        price,
        discount_price or "",  
        discount_valid_from or "",
        discount_valid_to or "",
        waste_discount or "",
        expiration_date or "",
        product_amount or ""
    ]

    try:
        with open(CSV_FILE_PATH, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(product_data) 

        print("Product data saved to CSV.")
        
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
    
    return filter_products(get_product_image)

@app.route('/search_discounts', methods=['GET', 'POST'])
def search_discount_method():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
    
    return search_discount()

@app.route('/get_closest_shops', methods=['GET'])
def get_closest_shops():
    try:
        user_lat = float(request.args.get('lat'))
        user_lon = float(request.args.get('lon'))
        radius = float(request.args.get('radius', 10))  # Default radius to 10km
        n = 16  # Number of closest shops to fetch

        # Use the find_closest_shops function
        closest_shops = dbf.find_closest_shops(user_lat, user_lon, n)

        # Filter shops within the radius
        filtered_shops = [
            (shop_id, distance) for shop_id, distance in closest_shops if distance <= radius
        ]

        # Fetch shop details for the filtered shops
        shop_details = []
        for shop_id, distance in filtered_shops:
            shop = Shop.query.get(shop_id)
            if shop:
                shop_details.append({
                    'shop_id': shop.shop_id,
                    'store_name': shop.store_name,
                    'distance': distance
                })

        return jsonify(shop_details)
    except Exception as e:
        print(f"Error fetching closest shops: {e}")
        return jsonify({'error': 'Failed to fetch closest shops'}), 500


# @app.route('/aura_stats/<int:user_id>', methods=['GET'])
# def get_aura_stats(user_id):
#     # Get total points
#     total_points = (
#         db.session.query(func.sum(Aurapoints.points))
#         .filter(Aurapoints.user_id == user_id)
#         .scalar() or 0
#     )

#     # Get lastly added points
#     latest_addition_query = (
#         db.session.query(Aurapoints.points)
#         .filter(Aurapoints.user_id == user_id)
#         .order_by(Aurapoints.timestamp.desc())
#         .first()
#     )
#     recently_added_points = latest_addition_query[0] if latest_addition_query else 0

#     # Get current month's points
#     current_month_points = (
#         db.session.query(func.sum(Aurapoints.points))
#         .filter(Aurapoints.user_id == user_id)
#         .filter(extract('month', Aurapoints.timestamp) == datetime.now().month)
#         .scalar() or 0
#     )

#     # Get last month's points
#     last_month = (datetime.now().month - 1) or 12
#     last_month_points = (
#         db.session.query(func.sum(Aurapoints.points))
#         .filter(Aurapoints.user_id == user_id)
#         .filter(extract('month', Aurapoints.timestamp) == last_month)
#         .scalar() or 0
#     )

#     # Get difference between current month and last month
#     difference_between_months = current_month_points - last_month_points

#     # Return in JSON-format
#     return jsonify({
#         'total_points': total_points,
#         'recently_added_points': recently_added_points,
#         'current_month_points': current_month_points,
#         'last_month_points': last_month_points,
#         'difference_between_months': difference_between_months
#     })

@app.route('/check_aura_points')
def check_aura_points():
    try:
        points = Aurapoints.query.filter_by(user_id=1).all()  # Haetaan kaikki pisteet käyttäjältä ID:llä 1
        if points:
            points_data = ', '.join([str(point.points) for point in points])
            return f"Points for user 1: {points_data}"
        else:
            return "No points found for user 1"
    except Exception as e:
        return f"Error accessing the database: {e}"

if __name__ == '__main__':
    #add_hardcoded_user()
    app.run(debug=True)
    check_aura_points()

