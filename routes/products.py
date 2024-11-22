from flask import json, request, redirect, url_for, jsonify, render_template
from models import db, Product, Shop, Price, User
from datetime import datetime
import random
from sqlalchemy.orm.exc import NoResultFound
from database_functions import add_product, add_price
import csv
from flask import session, jsonify, request
import os

from flask import request, redirect, url_for, session

CSV_FILE_PATH = 'routes/product_data.csv'

def add_product_from_html():
    """
    Gathers product information from an HTML form and passes it to the main add_product function.
    """
    try:

        # Retrieve data from the form
        product_name = request.form.get('product_name')
        weight_g = request.form.get('weight_g')
        volume_l = request.form.get('volume_l')
        barcode = request.form.get('barcode')
        category = request.form.get('category')
        esg_score = request.form.get('esg_score')
        co2_footprint = request.form.get('co2_footprint')
        brand = request.form.get('brand')
        sub_brand = request.form.get('sub_brand')
        parent_company = request.form.get('parent_company')
        information_links = request.form.get('information_links')
        gluten_free = request.form.get('gluten_free') == 'on'  
        
        shop_id = request.form.get('shop')
        price = request.form.get('price')
        discount_price = request.form.get('discount_price')
        discount_valid_from = request.form.get('discount_valid_from')
        discount_valid_to = request.form.get('discount_valid_to')
        waste_discount = request.form.get('waste_discount')
        expiration_date = request.form.get('expiration_date')
        product_amount = request.form.get('product_amount')

        try:
            discount_valid_from = datetime.strptime(discount_valid_from, '%Y-%m-%d').date() if discount_valid_from else None
            discount_valid_to = datetime.strptime(discount_valid_to, '%Y-%m-%d').date() if discount_valid_to else None
            expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d').date() if expiration_date else None
        except ValueError as ve:
            print(f"Invalid date format: {ve}")
            return redirect(url_for('products_page'))

        # Retrieve user ID from session
        user_id = session.get('user_id')
        if not user_id:
            print("User not authenticated. Redirecting to login.")
            return redirect(url_for('login'))

        # Call the main add_product function
        add_product(
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
            gluten_free=gluten_free,
        )

        add_price(
            product_id=get_product_id_by_name(product_name),
            shop_id=shop_id,
            price=price,
            discount_price=discount_price,
            waste_discount_percentage=waste_discount,
            discount_valid_from=discount_valid_from,
            discount_valid_to=discount_valid_to,
            waste_valid_to=expiration_date,
            waste_quantity=product_amount
        )

        return redirect(url_for('products_page'))

    except Exception as e:
        print(f"Error gathering product info from HTML: {e}")
        return redirect(url_for('products_page'))
    

def add_product_detail():
    try:
        product_data = {}

        # Check if the CSV file exists
        if os.path.exists(CSV_FILE_PATH):
            with open(CSV_FILE_PATH, mode='r') as file:
                reader = csv.reader(file)
                # Loop through each row in the CSV
                for row in reader:
                    # Assuming the format is 'barcode, product_name, shop, price, ...'
                    if len(row) >= 10:  # Ensure the row contains all the expected columns
                        barcode = row[0]  # The barcode is in the first column
                        product_name = row[1]  # The product name is in the second column
                        shop = row[2]
                        price = row[3]
                        discount_price = row[4]
                        discount_valid_from = row[5]
                        discount_valid_to = row[6]
                        waste_discount = row[7]
                        expiration_date = row[8]
                        product_amount = row[9]
                        
                        # Store the read data in the dictionary
                        product_data['barcode'] = barcode
                        product_data['product_name'] = product_name
                        product_data['shop'] = shop
                        product_data['price'] = price
                        product_data['discount_price'] = discount_price
                        product_data['discount_valid_from'] = discount_valid_from
                        product_data['discount_valid_to'] = discount_valid_to
                        product_data['waste_discount'] = waste_discount
                        product_data['expiration_date'] = expiration_date
                        product_data['product_amount'] = product_amount

                        # Print the row to show it
                        print(f"Barcode: {barcode}, Product Name: {product_name}, Shop: {shop}, Price: {price}, Discount Price: {discount_price}, "
                              f"Discount Valid From: {discount_valid_from}, Discount Valid To: {discount_valid_to}, Waste Discount: {waste_discount}, "
                              f"Expiration Date: {expiration_date}, Product Amount: {product_amount}")

        # Finally, print the last product data collected
        print("Product data from CSV:", product_data)

        # Extract data from session (or use defaults if not found)
        barcode = product_data.get('barcode')
        product_name = product_data.get('product_name')
        shop = session.get('product_data', {}).get('shop', '')
        price = session.get('product_data', {}).get('price', '')
        discount_price = session.get('product_data', {}).get('discount_price', '')
        discount_valid_from = session.get('product_data', {}).get('discount_valid_from', '')
        discount_valid_to = session.get('product_data', {}).get('discount_valid_to', '')
        waste_discount = session.get('product_data', {}).get('waste_discount', '')
        expiration_date = session.get('product_data', {}).get('expiration_date', '')
        product_amount = session.get('product_data', {}).get('product_amount', '')

        # Open the CSV file in write mode to overwrite it (this clears it)
        with open(CSV_FILE_PATH, mode='w', newline='') as file:
            writer = csv.writer(file)
            
 
            #TODO: fill those values into database
            return redirect(url_for('products_page'))

    except Exception as e:
        print(f"Error adding product detail: {e}")
        return redirect(url_for('products_page'))


def get_product_id_by_name(product_name):
    """
    Retrieve the product_id based on the product_name from the Product model.
    """
    try:
        product = Product.query.filter_by(product_name=product_name).first()
        if product:
            return product.product_id
        else:
            print(f"No product found with name: {product_name}")
            return None
    except Exception as e:
        print(f"Error fetching product_id for product_name '{product_name}': {e}")
        return None


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
    

def search_discount():
    query = request.args.get('query', '')  
    products_with_shops = []
    products = []

    if query:
        products = Product.query.filter(Product.product_name.ilike(f"%{query}%")).all()  

        
        for product in products:
            shops = Shop.query.join(Price).filter(Price.product_id == product.product_id).all()
            for shop in shops:
                accuracy = calculate_accuracy(query, product.product_name)
                products_with_shops.append({
                    'product': product.product_name,
                    'shop': shop.store_name,
                    'accuracy': accuracy,
                    'location': shop.location_address
                })

        products_with_shops.sort(key=lambda x: x['accuracy'], reverse=True)
    else:
        products = Product.query.all()
        print(products)

    return render_template('index.html', results=products, query=query)

def calculate_accuracy(query, product_name):
    query_lower = query.lower()
    product_name_lower = product_name.lower()
    
    match_len = len([ch for ch in query_lower if ch in product_name_lower])
    accuracy = match_len / len(query_lower) if query_lower else 0
    
    return accuracy

