from flask import request, redirect, url_for, flash
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
