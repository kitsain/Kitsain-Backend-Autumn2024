from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, text
from datetime import datetime
from sqlalchemy import desc
from flask import session
from routes.products import add_product, remove_product, update_product, get_products, search_discount
from routes.shops import add_shop, remove_shop
from routes.filtering import filter_shops, filter_products
from routes.users import modify_user, add_user, remove_user, modify_shopkeepers
import sqlite3
from models import db, Product, Shop, User, Price
from werkzeug.security import generate_password_hash, check_password_hash

import database_functions as dbf

app = Flask(__name__)
app.secret_key = 'asdhfauisdhfuhi'  # Required for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///commerce_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    #db.drop_all()
    #db.create_all()
    # dbf.add_user("admin", "admin", "admin@email.com", "admin")
    
    if request.method == 'POST':
        username = request.form.get('username')  # Gets the username
        password = request.form.get('password')  # Gets the password
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            # Set session variables or perform login actions
            return redirect(url_for('index'))
    
    return render_template('login.html')


@app.route('/email', methods=['GET', 'POST'])
def email():
    if request.method == 'POST':
        email = request.form.get('email')
        # print(email)

        emailagain = request.form.get('emailagain')
        # print(emailagain)

        print("Email: ", email)

        con = sqlite3.connect("commerce_data.db")
        cur = con.cursor()
        cur.execute('SELECT * FROM user WHERE email = ?', (email,))
        user = cur.fetchone()

        if user: 
            print("Käyttäjä löytyi!")
            print("Käyttäjä: ", user)

        if not user: 
            print("Käyttäjä: ", user)
            print("Sähköposti: ", email)
            print("Käyttäjää ei löytynyt")

        if email != emailagain:
            # print("The email fields are not equal")
            flash("Error: The email fields were not equal", category="error")
            session['email'] = email
            session['emailagain'] = emailagain
            return redirect(url_for('email'))
        

        password = "uudempi_salasana"

        cur.execute('UPDATE user SET password = ? WHERE email = ?', (generate_password_hash(password), email)
)
        con.commit()
        con.close()

        # session.pop('email', None)
        # session.pop('emailagain', None)
        return render_template("passwordSetConfirmation.html")
    
    email = session.get('email', '')
    emailagain = session.get('emailagain', '')
    return render_template("newPassword.html", email=email, emailagain=emailagain)

@app.route('/forgot_password')
def forgot_password():
    return render_template('newPassword.html')

def add_hardcoded_user():
    with app.app_context():
        db.create_all()  # Ensures tables are created

        # Create a hard-coded user
        hardcoded_user = User(
            username="hardcoded_user",
            password=generate_password_hash("securepassword123"),  # You should hash the password
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

@app.route('/products_page')
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


# routes.products

@app.route('/add_product', methods=['POST'])
def add_product_method():
    # Check access rights
    if dbf.confirm_access() == None:
        return redirect(url_for('login'))
        
    return add_product()

@app.route('/remove_product/<int:product_id>', methods=['POST'])
def remove_product_method(product_id):
    # Check access rights
    if dbf.confirm_access() != "admin":
        return redirect(url_for('login'))
    
    return remove_product(product_id)

@app.route('/update_product', methods=['POST'])
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
    add_hardcoded_user()
    app.run(debug=False)
