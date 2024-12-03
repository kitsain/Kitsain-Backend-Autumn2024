from flask import request, redirect, url_for, flash
from models import db, Product, Shop, Price, User, WorksFor
from database_functions import create_shop, add_user, add_shopkeeper_to_shop, print_shops
from datetime import datetime
import random


def add_shop():

    shop_name = request.form.get('store_name')
    shop_chain = request.form.get('chain')
    shop_location = request.form.get('location_address')
    shopkeepers = request.form.get('shopkeepers') 
    gps = request.form.get('gps') 

    if not shop_name or not shop_chain or not shop_location:
        flash("Please provide all required shop details.", "shop")
        return redirect(url_for('shops_page'))

    try:
        shop_id = create_shop(shop_name, shop_chain, shop_location, gps)

        if shopkeepers:
            shopkeeper_names = [name.strip() for name in shopkeepers.split(',')]
            for shopkeeper_name in shopkeeper_names:
                #TODO: search for already existing users 
                add_user(shopkeeper_name, password="password", email=f"{shopkeeper_name}@{shop_chain}.com", role="shopkeeper")
                #TODO: change this to search with user id, not name
                shopkeeper = User.query.filter_by(username=shopkeeper_name).first()
                add_shopkeeper_to_shop(shopkeeper.user_id, shop_id)
        print_shops()
    except (ValueError, IndexError):
        print("Error processing the provided details. Please ensure all fields are filled out correctly.", "shop")
    except Exception as e:
        print(f"Database error: {e}", "shop")
        db.session.rollback()

    return redirect(url_for('shops_page'))


def generate_unique_user_id():
    while True:
        user_id = random.randint(1000, 999999)
        if not db.session.query(User).filter_by(user_id=user_id).first():
            return user_id
        
        
def remove_shop(shop_id):
    shop_to_remove = Shop.query.filter_by(shop_id=shop_id).first()
    
    if shop_to_remove:
        shopkeepers = WorksFor.query.filter_by(shop_id=shop_id).all()
        
        db.session.delete(shop_to_remove)
        db.session.commit()  

        for works_for in shopkeepers:
            other_shops = WorksFor.query.filter_by(user_id=works_for.user_id).all()
            if not other_shops:  
                shopkeeper = User.query.filter_by(user_id=works_for.user_id).first()
                if shopkeeper:
                    db.session.delete(shopkeeper) 

        db.session.commit() 
    
    return redirect(url_for('shops_page'))