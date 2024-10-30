from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import get_data
import uuid
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_waste_new.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    role = db.Column(db.String, nullable=False, check_constraint="role IN ('user', 'shopkeeper', 'admin')")
    aura_points = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime, default=db.func.current_timestamp())
    creation_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    shops = db.relationship('Shop', backref='creator', lazy=True)
    products_created = db.relationship('Product', backref='creator', lazy=True)
    prices_created = db.relationship('Price', backref='creator', lazy=True)


class Shop(db.Model):
    __tablename__ = 'shop'
    shop_id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String, nullable=False)
    store_chain = db.Column(db.String)
    location_address = db.Column(db.String)
    location_gps = db.Column(db.String)
    user_created = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    creation_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    prices = db.relationship('Price', backref='shop', lazy=True)


class WorksFor(db.Model):
    __tablename__ = 'works_for'
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.shop_id'), primary_key=True)

    # Relationships
    user = db.relationship('User', backref=db.backref("works_for", cascade="all, delete-orphan"))
    shop = db.relationship('Shop', backref=db.backref("works_for", cascade="all, delete-orphan"))


class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String, nullable=False)
    weight_g = db.Column(db.Integer)
    volume_l = db.Column(db.Float)
    barcode = db.Column(db.String)
    category = db.Column(db.String)
    gluten_free = db.Column(db.Boolean)
    esg_score = db.Column(db.String)
    co2_footprint = db.Column(db.String)
    brand = db.Column(db.String)
    sub_brand = db.Column(db.String)
    parent_company = db.Column(db.String)
    information_links = db.Column(db.String)
    user_created = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    creation_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    prices = db.relationship('Price', backref='product', lazy=True)


class Price(db.Model):
    __tablename__ = 'price'
    price_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.shop_id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float)
    waste_discount_percentage = db.Column(db.Float)
    report_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    valid_from_date = db.Column(db.DateTime)
    valid_to_date = db.Column(db.DateTime)
    user_created = db.Column(db.Integer, db.ForeignKey('user.user_id'))



@app.route('/')
def index():
    products = (Product).query.all()  # Fetch all products from the database
    shops = Shop.query.all()
    users = User.query.all()
    shopkeepers_data = {shop.shop_id: [wf.user.username for wf in shop.works_for] for shop in shops}
    return render_template('index.html', products=products, shops=shops, shopkeepers_data=shopkeepers_data, users=users)


@app.route('/add_product', methods=['POST'])
def add_product():
    get_food = request.form.get('food_details')

    if not get_food:
        flash("Please provide the food details.", "product")
        return redirect(url_for('index'))

    try:
        parts = get_food.split(',')
        barcode = parts[0]
        product_name = ' '.join(parts[1:-1])
        creation_date = parts[-1]
        user_id = 1  # TODO: Replace with actual user ID logic
        gluten_free = get_data.get_gluten_free(barcode)  

        # Validate barcode
        existing_product = Product.query.filter_by(barcode=barcode).first()
        if existing_product:
            flash(f"Barcode {barcode} already used! Choose another barcode.", "product")
            return redirect(url_for('index'))

        # Parse creation date
        creation_date_obj = datetime.strptime(creation_date, "%d.%m.%Y")
        new_product = Product(
            barcode=barcode,
            product_name=product_name,
            creation_date=creation_date_obj,
            gluten_free=gluten_free,
            user_created=user_id  # Set user_created here
        )

        db.session.add(new_product)
        db.session.commit()

        flash(f"Product \"{product_name}\" added successfully with barcode \"{barcode}\".", "product")
    except (ValueError, IndexError):
        flash("Please provide the food details in the correct format: barcode food creation_date", "product")
    except Exception as e:
        flash(f"Database error: {e}", "product")

    return redirect(url_for('index'))


@app.route('/remove_product/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    product_to_remove = Product.query.filter_by(product_id=product_id).first()
    if product_to_remove:
        db.session.delete(product_to_remove)
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/remove_shop/<int:shop_id>', methods=['POST'])
def remove_shop(shop_id):
    shop_to_remove = Shop.query.filter_by(shop_id=shop_id).first()
    if shop_to_remove:
        db.session.delete(shop_to_remove)
        db.session.commit()
    return redirect(url_for('index'))


@app.route('/add_shop', methods=['POST'])
def add_shop():
    get_shop = request.form.get('shop_details')

    if not get_shop:
        flash("Please provide the shop details.", "shop")
        return redirect(url_for('index'))

    try:
        parts = get_shop.split(',')
        shop_name = parts[0]
        shop_chain = parts[1]
        shop_location = parts[2]
        user_id = 1


        new_shop = Shop(
            store_name=shop_name,
            store_chain=shop_chain,
            location_address=shop_location,
            user_created=user_id  # Set user_created here
        )

        db.session.add(new_shop)
        db.session.commit()

        flash(f"Shop added successfully", "shop")
    except (ValueError, IndexError):
        flash("Please provide the food details in the correct format: barcode food creation_date", "shop")
    except Exception as e:
        flash(f"Database error: {e}", "shop")

    return redirect(url_for('index'))

@app.route('/modify_shopkeepers/<int:shop_id>', methods=['GET', 'POST'])
def modify_shopkeepers(shop_id):
    if not shop_id:
        flash("Shop ID is required.", "error")
        return redirect(url_for('index'))
    shop = Shop.query.get(shop_id)
    if not shop:
        flash("Shop not found", "error")
        return redirect(url_for('index'))

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
        return redirect(url_for('index'))

    try:
        parts = get_user.split(',')
        username = parts[0]
        role = parts[1]
        user_id = generate_unique_user_id()
        aura_points = 0
        
        # Validate barcode
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash(f"Username {username} already used! Choose another username.", "user")
            return redirect(url_for('index'))

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

    return redirect(url_for('index'))

@app.route('/modify_users/<int:user_id>', methods=['GET', 'POST'])
def modify_user(user_id):
    if not user_id:
        flash("User ID is required.", "error")
        return redirect(url_for('index'))
    
    user = User.query.get(user_id)
    if not user:
        flash("User not found", "error")
        return redirect(url_for('index'))

    # Pass the user object to the template
    return render_template('modify_user.html', user=user)

@app.route('/remove_user/<int:user_id>', methods=['GET', 'POST'])
def remove_user(user_id):
    user_to_remove = User.query.filter_by(user_id=user_id).first()
    if user_to_remove:
        db.session.delete(user_to_remove)
        db.session.commit()
    return redirect(url_for('index'))


def generate_unique_user_id():
    while True:
        # Generate a random ID within a larger range
        user_id = random.randint(1000, 999999)
        # Check if this ID already exists in the database
        if not db.session.query(User).filter_by(user_id=user_id).first():
            return user_id


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
