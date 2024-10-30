from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import get_data

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_waste_new.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

class User(db.Model):
    __tablename__ = 'user'    
    user_id = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String, nullable=False, unique=True) 
    password = db.Column(db.String, nullable=False) 
    email = db.Column(db.String, nullable=False, unique=True) 
    role = db.Column(db.String, nullable=False)  
    creation_date = db.Column(db.DateTime, default=db.func.current_timestamp())  


@app.route('/')
def index():
    products = (Product).query.all()  # Fetch all products from the database
    return render_template('index.html', products=products)


@app.route('/add', methods=['POST'])
def add_product():
    get_food = request.form.get('food_details')

    if not get_food:
        flash("Please provide the food details.")
        return redirect(url_for('index'))

    try:
        parts = get_food.split()
        barcode = parts[0]
        product_name = ' '.join(parts[1:-1])
        creation_date = parts[-1]
        user_id = 1  # TODO: Replace with actual user ID logic
        gluten_free = get_data.get_gluten_free(barcode)  

        # Validate barcode
        existing_product = Product.query.filter_by(barcode=barcode).first()
        if existing_product:
            flash(f"Barcode {barcode} already used! Choose another barcode.")
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

        flash(f"Product \"{product_name}\" added successfully with barcode \"{barcode}\".")
    except (ValueError, IndexError):
        flash("Please provide the food details in the correct format: barcode food creation_date")
    except Exception as e:
        flash(f"Database error: {e}")

    return redirect(url_for('index'))


@app.route('/remove/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    product_to_remove = Product.query.get(product_id)
    if product_to_remove:
        db.session.delete(product_to_remove)
        db.session.commit()
    return redirect(url_for('index'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
