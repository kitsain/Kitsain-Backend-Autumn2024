from flask import request, redirect, url_for, flash
from models import db, Product, Shop, Price, User, WorksFor
from database_functions import create_shop, add_user, add_shopkeeper_to_shop
from datetime import datetime
import random


def add_shop():
    shop_id = generate_unique_user_id()
    shop_name = request.form.get('store_name')
    shop_chain = request.form.get('chain')
    shop_location = request.form.get('location_address')
    shopkeepers = request.form.get('shopkeepers') 
    gps = request.form.get('gps') 

    if not shop_name or not shop_chain or not shop_location:
        flash("Please provide all required shop details.", "shop")
        return redirect(url_for('shops_page'))

    try:
        # Set creation_date to now
        #creation_date = datetime.now().date()  # Get the current date

        #new_shop = Shop(
            #shop_id = shop_id,
           # store_name=shop_name,
            #store_chain=shop_chain,
            #location_address=shop_location,
            #user_created=1,  # Adjust as needed
            #creation_date=creation_date
        #)
        create_shop(shop_name, shop_chain, shop_location, gps)

        #db.session.add(new_shop)
        #db.session.commit()  # Commit to get the new shop ID

        if shopkeepers:
            shopkeeper_names = [name.strip() for name in shopkeepers.split(',')]
            for shopkeeper_name in shopkeeper_names:
                add_user(shopkeeper_name, password="default", email="default2", role="shopkeeper")
                #TODO: change this to search with user id, not name
                shopkeeper = User.query.filter_by(username=shopkeeper_name).first()
                add_shopkeeper_to_shop(shopkeeper.user_id, shop_id)


                #shopkeeper = User.query.filter_by(username=shopkeeper_name).first()
                
                #if not shopkeeper:
                    # Create new shopkeeper if not found
                    #shopkeeper = User(
                        #username=shopkeeper_name,
                        #password='default',  # Set a secure password as needed
                        #role='shopkeeper',
                        #aura_points=0
                    #)
                    #db.session.add(shopkeeper)  # Add the new shopkeeper to the db.session
                    #db.session.commit()  # Commit here to flush the new user ID

                # Now add the relationship
                #works_for = WorksFor(user_id=shopkeeper.user_id, shop_id=new_shop.shop_id)
                #db.session.add(works_for)
        
        #db.session.commit()
        print("Shop added successfully!", "shop")
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