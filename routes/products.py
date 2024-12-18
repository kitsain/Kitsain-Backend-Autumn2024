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
        
        shop_id = request.form.get('shop_add')
        price = request.form.get('add-price')
        discount_price = request.form.get('discount_price')
        discount_valid_from = request.form.get('discount_valid_from')
        discount_valid_to = request.form.get('discount_valid_to')
        waste_discount = request.form.get('waste_discount_add')
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

        if os.path.exists(CSV_FILE_PATH):
            with open(CSV_FILE_PATH, mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) >= 10: 
                        barcode = row[0]  
                        product_name = row[1]  
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
                        #print(f"Barcode: {barcode}, Product Name: {product_name}, Shop: {shop}, Price: {price}, Discount Price: {discount_price}, "
                              #f"Discount Valid From: {discount_valid_from}, Discount Valid To: {discount_valid_to}, Waste Discount: {waste_discount}, "
                              #f"Expiration Date: {expiration_date}, Product Amount: {product_amount}")

        #print("Product data from CSV:", product_data)

        barcode = product_data.get('barcode')
        #product_name = product_data.get('product_name')

        discount_price = product_data.get('discount_price', '')
        discount_valid_from = product_data.get('discount_valid_from', '')
        discount_valid_to = product_data.get('discount_valid_to')
        waste_discount = product_data.get('waste_discount', '')
        price = product_data.get('price', '')
        product_amount = product_data.get('product_amount', '')

        #price = session.get('product_data', {}).get('price', '')
        #discount_price = session.get('product_data', {}).get('discount_price', '')
        #discount_valid_from = session.get('product_data', {}).get('discount_valid_from', '')
        #discount_valid_to = session.get('product_data', {}).get('discount_valid_to', '')
        #waste_discount = session.get('product_data', {}).get('waste_discount', '')
        #product_amount = session.get('product_data', {}).get('product_amount', '')

        shop=product_data.get('shop', '')
        expiration_date = product_data.get('expiration_date', '')

        # Open the CSV file in write mode to overwrite it (this clears it)
        with open(CSV_FILE_PATH, mode='w', newline='') as file:
            pass
            
        product_name = request.form.get('product_name_detailed')
        #additional information
        weight_g = float(request.form.get('weight', 0) or 0)
        volume_l = float(request.form.get('volume_ml', 0) or 0)
        #barcode = request.form.get('barcode')
        category = request.form.get('category')
        esg_score = request.form.get('esg_score')
        co2_footprint = request.form.get('CO2')
        brand = request.form.get('brand')
        sub_brand = request.form.get('sub_brand')
        parent_company = request.form.get('parent_company')
        gluten_free = request.form.get('gluten_free') == 'on'

        if (request.form.get("product_image_url") == "Image not found"):
            product_image = None
        else:
            product_image = request.form.get("product_image_url")

        information_links = {
        "product_image_url": product_image,
        "product_page_url": request.form.get("product_page_url"),
        }

        information_links_str = str(information_links)

        discount_valid_from = datetime.strptime(discount_valid_from, '%Y-%m-%d').date() if discount_valid_from else None
        discount_valid_to = datetime.strptime(discount_valid_to, '%Y-%m-%d').date() if discount_valid_to else None
        expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d').date() if expiration_date else None

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
            information_links=information_links_str,
            gluten_free=gluten_free,
        )

        product_id = get_product_id_by_name(product_name)
        if not product_id:
            raise ValueError(f"Product '{product_name}' not found in the database.")

        if product_amount == "":
            product_amount = None
        elif waste_discount == "":
            waste_discount = None
        elif discount_price == "":
            discount_price = None

        add_price(
            product_id=product_id,
            shop_id=int(shop) if shop else None,
            price=float(price) if price else None,
            discount_price=float(discount_price) if discount_price else None,
            waste_discount_percentage=float(waste_discount) if waste_discount else None,
            discount_valid_from=discount_valid_from,
            discount_valid_to=discount_valid_to,
            waste_valid_to=expiration_date,
            waste_quantity=product_amount
        )

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

from flask import request, jsonify

def update_product():
    # Get JSON data from the request
    data = request.get_json() 

    # Extract values from the JSON data
    product_id = data.get('product_id')
    barcode = data.get('barcode')
    product_name = data.get('product_name')
    shop = data.get('shop')
    price = data.get('price')
    waste_discount = data.get('waste_discount')
    expiration_date = data.get('expiration_date')
    product_amount = data.get('product_amount')  # Few, Moderate, Many
    discount_price = data.get('discount_price')
    discount_valid_from = data.get('discount_valid_from')
    discount_valid_to = data.get('discount_valid_to')

    # Call a function to update the product in the database
    success = update_product_in_db(product_id, product_name, shop, price, waste_discount, expiration_date, 
                                    product_amount, discount_price, discount_valid_from, discount_valid_to, barcode)

    # Check if the update was successful and return appropriate response
    if success:
        return jsonify({"message": "Succeeded to update product."}), 200
    else:
        return jsonify({"message": "Failed to update product."}), 500


def update_product_in_db(product_id, product_name, shop, price, waste_discount, expiration_date, 
                          product_amount, discount_price, discount_valid_from, discount_valid_to):
    # Get the product by its ID
    product = Product.query.get(product_id)
    
    if not product:
        return False  # Product not found

    # Update the product's attributes
    product.product_name = product_name
    product.shop = shop  
    product.price = price
    product.waste_discount_percentage = waste_discount
    product.valid_to_date = expiration_date
    product.product_amount = product_amount  # New field for stock amount (Few, Moderate, Many)
    product.discount_price = discount_price  # New field for discount price
    product.discount_valid_from = discount_valid_from  # New field for discount validity start
    product.discount_valid_to = discount_valid_to  # New field for discount validity end
    
    try:
        db.session.commit()  # Save changes to the database
        return True  # Successfully updated
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        print(f"Error updating product: {e}")
        return False


def edit_product_detail():
    # Get JSON data from the request
    data = request.get_json() 

    # Extract the fields dynamically from the payload
    product_id = data.get('product_id')
    product_name = data.get('product_name')
    shop = data.get('shop')
    price = data.get('price')
    waste_discount = data.get('waste_discount')
    expiration_date = data.get('expiration_date')
    product_amount = data.get('product_amount')
    discount_price = data.get('discount_price')
    discount_valid_from = data.get('discount_valid_from')
    discount_valid_to = data.get('discount_valid_to')
    barcode = data.get('barcode')

    #additional information
    brand = data.get('brand')
    parent_company = data.get('parent_company')
    volume_ml = data.get('volume_ml')
    gluten_free = data.get('gluten_free')
    co2 = data.get('co2')
    product_image_url = data.get('product_image_url')
    sub_brand = data.get('sub_brand')
    weight = data.get('weight')
    category = data.get('category')
    esg_score = data.get('esg_score')
    product_page_url = data.get('product_page_url')
    product_image = data.get('product_image')

    # Call a function to update the product with the new fields in the database
    success = update_product_in_db(
        product_id, product_name, shop, price, waste_discount, expiration_date, product_amount, discount_price, discount_valid_from, discount_valid_to, barcode, 
        brand, parent_company, volume_ml, gluten_free, co2, product_image_url, sub_brand, weight, category, esg_score, product_page_url, product_image
    )

    # Check if the update was successful and return appropriate response
    if success:
        return jsonify({"message": "Succeeded to update product."}), 200
    else:
        return jsonify({"message": "Failed to update product."}), 500
    

def update_product_in_db(product_id, product_name, shop, price, waste_discount, expiration_date, product_amount, discount_price, discount_valid_from, discount_valid_to, barcode, 
        brand=None, parent_company=None, volume_ml=None, gluten_free=None, co2=None, product_image_url=None, sub_brand=None, weight=None, category=None, esg_score=None, product_page_url=None, product_image=None):
    product = Product.query.get(product_id)
    
    if not product:
        return False  

    # basic info
    product.product_id = product_id
    product.product_name = product_name
    product.barcode = barcode
    product.shop = shop  
    product.price = price
    product.waste_discount_percentage = waste_discount
    product.valid_to_date = expiration_date
    product.product_amount = product_amount  
    product.discount_price = discount_price  
    product.discount_valid_from = discount_valid_from  
    product.discount_valid_to = discount_valid_to 

    if isinstance(gluten_free, str):
        gluten_free = gluten_free.lower() == 'true'

    # Additional fields
    product.brand = brand
    product.parent_company = parent_company
    product.volume_ml = volume_ml
    product.gluten_free = gluten_free
    product.co2_footprint = co2
    product.product_image_url = product_image_url
    product.sub_brand = sub_brand
    product.weight = weight
    product.category = category
    product.esg_score = esg_score
    product.product_page_url = product_page_url
    product.product_image = product_image

    try:
        db.session.commit()  
        return True  
    except Exception as e:
        db.session.rollback() 
        print(f"Error updating product: {e}")
        return False


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

    return render_template('index.html', results=products, query=query, get_product_image=get_product_image)

def calculate_accuracy(query, product_name):
    query_lower = query.lower()
    product_name_lower = product_name.lower()
    
    match_len = len([ch for ch in query_lower if ch in product_name_lower])
    accuracy = match_len / len(query_lower) if query_lower else 0
    
    return accuracy

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


def save_product_data_to_csv(data):
    """
    Validates and saves product data to a CSV file.

    Args:
        data (dict): JSON payload containing product details.

    Returns:
        tuple: A JSON response and HTTP status code.
    """
    # Extract fields from data
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

    # Check for required fields
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
        # Write data to CSV
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
        }), 200

    except Exception as e:
        print(f"Error saving product data to CSV: {e}")
        return jsonify({"message": "Error saving data"}), 500
