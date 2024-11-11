from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from datetime import datetime
from sqlalchemy import desc
from flask import session
import random
from models import db, Product, Shop, User, Price, WorksFor

app = Flask(__name__)
app.secret_key = 'asdhfauisdhfuhi'  # Required for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_waste_new.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')  # Gets the username
        password = request.form.get('password')  # Gets the password
        
        # Check if username and password match "admin"
        if username == "admin" and password == "admin":
            session['user_id'] = 1  # Example user ID for admin
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password. Please try again.", "error")
    
    return render_template('login.html')


@app.route('/email', methods=['GET', 'POST'])
def email():
    if request.method == 'POST':
        email = request.form.get('email')
        # print(email)

        emailagain = request.form.get('emailagain')
        # print(emailagain)

        if email != emailagain:
            # print("The email fields are not equal")
            flash("Error: The email fields were not equal", category="error")
            return render_template("newPassword.html")

    print("Hello world!")
    return render_template("passwordSetConfirmation.html")

@app.route('/forgot_password')
def forgot_password():
    return render_template('newPassword.html')

@app.route('/index')
def index():
    # Retrieve the five latest products, assuming Product has a 'created_at' or 'added_date' field
    products = (Product).query.order_by(desc(Product. creation_date)).limit(2).all()
    shops = Shop.query.all()
    users = User.query.all()
    shopkeepers_data = {shop.shop_id: [wf.user.username for wf in shop.works_for] for shop in shops}
    return render_template('index.html', products=products, shops=shops, shopkeepers_data=shopkeepers_data, users=users)


@app.route('/add_product', methods=['POST'])
def add_product():
    product_name = request.form.get('product_name')
    shop = request.form.get('shop')
    price = request.form.get('price')
    discount_price = request.form.get('discount_price')
    waste_discount = request.form.get('waste_discount')
    expiration_date = request.form.get('expiration_date')
    user_id = request.form.get('user_id')  
    product_id = generate_unique_user_id()
    
    if not product_name or not shop or not price or not discount_price:
        print("Please provide the product name, shop, and price.", "product")
        return redirect(url_for('products_page'))

    try:
        existing_shop = Shop.query.filter_by(store_name=shop).first()
        if not existing_shop:
            print(f"Shop '{shop}' not found. Please add it first.", "product")
            return redirect(url_for('products_page'))

        new_product = Product(
            product_id = product_id,
            product_name=product_name,
            user_created=user_id,
            creation_date=datetime.now()
        )

        db.session.add(new_product)
        db.session.commit()


        valid_to_date = datetime.strptime(expiration_date, '%Y-%m-%d') if expiration_date else None
        new_price = Price(
            product_id=new_product.product_id,
            shop_id=existing_shop.shop_id,
            price=float(price),
            discount_price=float(discount_price),
            valid_to_date = valid_to_date,
            waste_discount_percentage=float(waste_discount) if waste_discount else None,
            user_created=user_id
        )

        db.session.add(new_price)
        db.session.commit()

        print(f"Product \"{product_name}\" added successfully to \"{shop}\".", "product")
    except ValueError:
        print("Please provide valid data. Ensure the price and waste discount are numbers.", "product")
    except Exception as e:
        db.session.rollback()  # Rollback any changes if there's an error
        print(f"Database error: {e}", "product")

    return redirect(url_for('products_page'))


@app.route('/remove_product/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    product_to_remove = Product.query.filter_by(product_id=product_id).first()

    if product_to_remove:
        try:
            Price.query.filter_by(product_id=product_id).delete()

            db.session.delete(product_to_remove)
            db.session.commit()

            print(f'Product "{product_to_remove.product_name}" has been removed successfully.', "product")
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred while trying to remove the product: {e}", "product")
    else:
        print("Product not found. It may have already been removed.", "product")

    return redirect(url_for('products_page'))


@app.route('/remove_shop/<int:shop_id>', methods=['POST'])
def remove_shop(shop_id):
    shop_to_remove = Shop.query.filter_by(shop_id=shop_id).first()
    
    if shop_to_remove:
        # Get the shopkeeper(s) associated with this shop
        shopkeepers = WorksFor.query.filter_by(shop_id=shop_id).all()
        
        # Remove the shop
        db.session.delete(shop_to_remove)
        db.session.commit()  # Commit the deletion

        # Check each shopkeeper
        for works_for in shopkeepers:
            # Check if the shopkeeper has any other shops
            other_shops = WorksFor.query.filter_by(user_id=works_for.user_id).all()
            if not other_shops:  # If no other shops, remove their shopkeeper status
                shopkeeper = User.query.filter_by(user_id=works_for.user_id).first()
                if shopkeeper:
                    db.session.delete(shopkeeper)  # Delete the shopkeeper
                    # Alternatively, you could just update their role to something else
                    # shopkeeper.role = 'user'  # Change the role if you don't want to delete
                    # db.session.add(shopkeeper)
        
        db.session.commit()  # Commit changes to delete shopkeeper if applicable
    
    return redirect(url_for('shops_page'))


@app.route('/add_shop', methods=['POST'])
def add_shop():
    shop_id = generate_unique_user_id()
    shop_name = request.form.get('store_name')
    shop_chain = request.form.get('chain')
    shop_location = request.form.get('location_address')
    shopkeepers = request.form.get('shopkeepers')  

    if not shop_name or not shop_chain or not shop_location:
        flash("Please provide all required shop details.", "shop")
        return redirect(url_for('shops_page'))

    try:
        # Set creation_date to now
        creation_date = datetime.now().date()  # Get the current date

        new_shop = Shop(
            shop_id = shop_id,
            store_name=shop_name,
            store_chain=shop_chain,
            location_address=shop_location,
            user_created=1,  # Adjust as needed
            creation_date=creation_date
        )

        db.session.add(new_shop)
        db.session.commit()  # Commit to get the new shop ID

        if shopkeepers:
            shopkeeper_names = [name.strip() for name in shopkeepers.split(',')]
            for shopkeeper_name in shopkeeper_names:
                shopkeeper = User.query.filter_by(username=shopkeeper_name).first()
                
                if not shopkeeper:
                    # Create new shopkeeper if not found
                    shopkeeper = User(
                        username=shopkeeper_name,
                        password='default',  # Set a secure password as needed
                        role='shopkeeper',
                        aura_points=0
                    )
                    db.session.add(shopkeeper)  # Add the new shopkeeper to the db.session
                    db.session.commit()  # Commit here to flush the new user ID

                # Now add the relationship
                works_for = WorksFor(user_id=shopkeeper.user_id, shop_id=new_shop.shop_id)
                db.session.add(works_for)
        
        db.session.commit()
        print("Shop added successfully!", "shop")
    except (ValueError, IndexError):
        print("Error processing the provided details. Please ensure all fields are filled out correctly.", "shop")
    except Exception as e:
        print(f"Database error: {e}", "shop")
        db.session.rollback()

    return redirect(url_for('shops_page'))


@app.route('/modify_shopkeepers/<int:shop_id>', methods=['GET', 'POST'])
def modify_shopkeepers(shop_id):
    if not shop_id:
        flash("Shop ID is required.", "error")
        return redirect(url_for('modify_shopkeepers'))
    shop = Shop.query.get(shop_id)
    if not shop:
        flash("Shop not found", "error")
        return redirect(url_for('modify_shopkeepers'))

    # Fetch all users for shopkeeper options
    users = User.query.all()
    current_shopkeepers = [wf.user for wf in shop.works_for]

    if request.method == 'POST':
        # Logic for adding/removing shopkeepers
        action = request.form.get("action")
        user_id = request.form.get("user_id")

        if action == "add":
            # Add user as shopkeeper if not already assigned
            if not WorksFor.query.filter_by(shop_id=shop_id, user_id=user_id).first():
                new_shopkeeper = WorksFor(shop_id=shop_id, user_id=user_id)
                db.session.add(new_shopkeeper)
                db.session.commit()
                flash("Shopkeeper added successfully", "success")
        elif action == "remove":
            # Remove the shopkeeper if exists
            existing_shopkeeper = WorksFor.query.filter_by(shop_id=shop_id, user_id=user_id).first()
            if existing_shopkeeper:
                db.session.delete(existing_shopkeeper)
                db.session.commit()
                flash("Shopkeeper removed successfully", "success")

        return redirect(url_for('modify_shopkeepers', shop_id=shop_id))

    return render_template('modify_shopkeepers.html', shop=shop, users=users, current_shopkeepers=current_shopkeepers)


@app.route('/add_user', methods=['POST'])
def add_user():
    get_user = request.form.get('user_info')

    if not get_user:
        flash("Please provide the user details.", "user")
        return redirect(url_for('users_page'))

    try:
        parts = get_user.split(',')
        username = parts[0]
        role = parts[1]
        user_id = generate_unique_user_id()
        aura_points = 0
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash(f"Username {username} already used! Choose another username.", "user")
            return redirect(url_for('users_page'))

        new_user = User(
            user_id=user_id,
            username=username,
            role=role,
            password="default", #TODO
            aura_points=aura_points,
        )

        db.session.add(new_user)
        db.session.commit()

        flash(f"User \"{username}\" added successfully", "user")
    except (ValueError, IndexError):
        flash("Please provide the user details in the correct format: username role", "user")
    except Exception as e:
        flash(f"Database error: {e}", "user")

    return redirect(url_for('users_page'))


@app.route('/modify_users/<int:user_id>', methods=['GET', 'POST'])
def modify_user(user_id):
    if not user_id:
        flash("User ID is required.", "error")
        return redirect(url_for('modify_user.html'))
    
    user = User.query.get(user_id)
    if not user:
        flash("User not found", "error")
        return redirect(url_for('modify_user.html'))

    # Pass the user object to the template
    return render_template('modify_user.html', user=user)

@app.route('/remove_user/<int:user_id>', methods=['GET', 'POST'])
def remove_user(user_id):
    user_to_remove = User.query.filter_by(user_id=user_id).first()
    if user_to_remove:
        db.session.delete(user_to_remove)
        db.session.commit()
    return redirect(url_for('users_page'))


def generate_unique_user_id():
    while True:
        # Generate a random ID within a larger range
        user_id = random.randint(1000, 999999)
        # Check if this ID already exists in the database
        if not db.session.query(User).filter_by(user_id=user_id).first():
            return user_id

@app.route('/products_page')
def products_page():
    products = db.session.query(Product).outerjoin(Price).outerjoin(Shop).all()
    return render_template('products_page.html', products=products)

@app.route('/shops_page')
def shops_page():
    shops = (Shop).query.all() 
    shopkeepers_data = {shop.shop_id: [wf.user.username for wf in shop.works_for] for shop in shops}
    return render_template('shops_page.html', shops = shops, shopkeepers_data=shopkeepers_data)

@app.route('/users_page')
def users_page():
    users = (User).query.all()
    shops = (Shop).query.all()  
    products = (Product).query.all()
    shopkeepers_data = {shop.shop_id: [wf.user.username for wf in shop.works_for] for shop in shops} 
    return render_template('users_page.html', products=products, shops=shops, shopkeepers_data=shopkeepers_data, users=users)

@app.route('/update_product', methods=['POST'])
def update_product():
    data = request.get_json()  # Get the JSON data from the request

    # Extract data from the request
    product_id = data.get('product_id')
    product_name = data.get('product_name')
    shop = data.get('shop')
    price = data.get('price')
    waste_discount = data.get('waste_discount')
    expiration_date = data.get('expiration_date')

    # Logic to update the product in your database
    # Example: use SQLAlchemy to update the product record

    success = update_product_in_db(product_id, product_name, shop, price, waste_discount, expiration_date)

    if success:
        return jsonify({"message": "Succeeded to update product."}), 200
    else:
        return jsonify({"message": "Failed to update product."}), 500


def update_product_in_db(product_id, product_name, shop, price, waste_discount, expiration_date):
    product = Product.query.get(product_id)
    
    if not product:
        return False  # Product not found

    # Update the product's attributes
    product.product_name = product_name
    product.shop = shop  
    product.price = price
    product.waste_discount_percentage = waste_discount
    product.valid_to_date = expiration_date 
    
    try:
        db.session.commit()  # Save changes to the database
        return True  # Successfully updated
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"Error updating product: {e}")
        return False



@app.route('/get_products', methods=['GET'])
def get_products():
    try:
        # Query all products along with their associated prices and shops using outer joins
        products = db.session.query(Product).outerjoin(Price).outerjoin(Shop).all()
        
        # Prepare a list to hold the product data
        products_list = []
        for product in products:
            prices_list = []
            for price in product.prices:  # Assuming Product has a relationship with Price
                prices_list.append({
                    'price': price.price,
                    'store_name': price.shop.store_name if price.shop else 'N/A',
                    'waste_discount_percentage': price.waste_discount_percentage,
                    'valid_to_date': price.valid_to_date if price.valid_to_date else 'N/A'
                })
            
            products_list.append({
                'product_id': product.product_id,
                'product_name': product.product_name,
                'prices': prices_list
            })

        # Print the products list (for debugging purposes)
        print(products_list)
        
        # Render the products_page.html and pass the products_list to the template
        return render_template('products_page.html', products=products_list)
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500
    

@app.route('/filter_shops', methods=['GET', 'POST'])
def filter_shops():
    store_name = ''
    location_address = ''
    chain = ''
    shopkeepers = ''
    
    if request.method == 'POST':
        # Get values from the form
        store_name = request.form.get('store_name', '')
        location_address = request.form.get('location_address', '')
        chain = request.form.get('chain', '')
        shopkeepers = request.form.get('shopkeepers', '')

        # Your filtering logic here...
        query = Shop.query
        
        if store_name:
            query = query.filter(Shop.store_name.ilike(f'%{store_name}%'))
        
        if location_address:
            query = query.filter(Shop.location_address.ilike(f'%{location_address}%'))
        
        if chain:
            query = query.filter(Shop.store_chain.ilike(f'%{chain}%'))
        
        if shopkeepers:
            query = query.join(WorksFor).join(User).filter(User.username.ilike(f'%{shopkeepers}%'))

        filtered_shops = query.all()
        shopkeepers_data = {shop.shop_id: [wf.user.username for wf in shop.works_for] for shop in filtered_shops}

        # Render the shops page with the filtered results and the input values
        return render_template('shops_page.html', shops=filtered_shops, shopkeepers_data=shopkeepers_data, 
                               store_name=store_name, location_address=location_address, 
                               chain=chain, shopkeepers=shopkeepers)

    # If it's a GET request, just render the shops page without filters
    return render_template('shops_page.html')


@app.route('/filter_products', methods=['GET', 'POST'])
def filter_products():
    products = []
    product_name = ''
    shop = ''
    price = ''
    waste_discount = ''
    expiration_date = ''
    
    if request.method == 'POST':
        # Get values from the form
        product_name = request.form.get('product_name', '')
        shop = request.form.get('shop', '')
        price = request.form.get('price', '')
        waste_discount = request.form.get('waste_discount', '')
        expiration_date = request.form.get('expiration_date', '')

        # Filtering logic
        query = Product.query.join(Price).join(Shop)  # Join Product with Price and Shop
        
        if product_name:
            query = query.filter(Product.product_name.ilike(f'%{product_name}%'))
        
        if shop:
            query = query.filter(Shop.store_name.ilike(f'%{shop}%'))  # Use the shop's name here

        if price:
            query = query.filter(Price.price <= float(price))  # Filter by Price model
        
        if waste_discount:
            query = query.filter(Price.waste_discount_percentage <= float(waste_discount))  # Adjusted to reference Price model
        
        if expiration_date:
            query = query.filter(Price.valid_to_date <= expiration_date)  # Adjust based on your requirements

        # Execute the query and get filtered products
        products = query.all()

    # Render the products page with the filtered results
    return render_template('products_page.html', products=products, 
                           product_name=product_name, shop=shop, 
                           price=price, waste_discount=waste_discount, 
                           expiration_date=expiration_date)



@app.route('/seach_discounts')
def search_discount():
    #TODO
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
