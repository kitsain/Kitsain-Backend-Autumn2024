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
    query = Product.query.join(Price).join(Shop)

    # Product filters
    product_name = request.form.get('product_name_filter')
    category = request.form.get('category_filter')
    brand = request.form.get('brand_filter')
    gluten_free = request.form.get('gluten_free_filter')

    if product_name:
        query = query.filter(Product.product_name.ilike(f"%{product_name}%"))
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    if gluten_free:
        query = query.filter(Product.gluten_free == (gluten_free == 'true'))

    # Price filters
    min_price = request.form.get('min_price')
    max_price = request.form.get('max_price')
    discounted_only = request.form.get('discounted_only')
    expiring_only = request.form.get('expiring_only')

    if min_price:
        query = query.filter(Price.price >= float(min_price))
    if max_price:
        query = query.filter(Price.price <= float(max_price))
    if discounted_only == 'true':
        query = query.filter(Price.discount_price.isnot(None))
    if expiring_only == 'true':
        query = query.filter(Price.waste_valid_to >= datetime.now())

    # Shop filters
    shop = request.form.get('shop_filter')
    gps_lat = request.form.get('gps_lat')
    gps_lon = request.form.get('gps_lon')

    if shop:
        query = query.filter(Shop.store_name.ilike(f"%{shop}%"))
    if gps_lat and gps_lon:
        # Add logic to filter nearby shops using Haversine formula or similar
        pass  # Placeholder for nearby shop filtering logic

    products = query.all()
    return render_template('products_page.html', products=products)



