from flask import request, redirect, url_for, jsonify, render_template
from models import db, Product, Shop, Price, User
from datetime import datetime
import random

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
            product_id=product_id,
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
            valid_to_date=valid_to_date,
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

def generate_unique_user_id():
    while True:
        user_id = random.randint(1000, 999999)
        if not db.session.query(User).filter_by(user_id=user_id).first():
            return user_id

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