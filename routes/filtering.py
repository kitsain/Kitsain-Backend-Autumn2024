from flask import request, redirect, url_for, jsonify, render_template
from models import db, Product, Shop, Price, User, WorksFor
from datetime import datetime
import random

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


