from flask import request, redirect, url_for, flash, render_template
from models import db, Product, Shop, Price, User, WorksFor
from datetime import datetime
import random

def generate_unique_user_id():
    while True:
        user_id = random.randint(1000, 999999)
        if not db.session.query(User).filter_by(user_id=user_id).first():
            return user_id

def add_user():
    get_user = request.form.get('user_info')

    if not get_user:
        flash("Please provide the user details.", "user")
        return redirect(url_for('users_page'))

    try:
        parts = get_user.split(',')
        username = parts[0]
        role = parts[1]
        user_id = generate_unique_user_id()
        aura_points = 0
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash(f"Username {username} already used! Choose another username.", "user")
            return redirect(url_for('users_page'))

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

    return redirect(url_for('users_page'))


def modify_user(user_id):
    if not user_id:
        flash("User ID is required.", "error")
        return redirect(url_for('modify_user.html'))
    
    user = User.query.get(user_id)
    if not user:
        flash("User not found", "error")
        return redirect(url_for('modify_user.html'))

    # Pass the user object to the template
    return render_template('modify_user.html', user=user)


def remove_user(user_id):
    user_to_remove = User.query.filter_by(user_id=user_id).first()
    if user_to_remove:
        db.session.delete(user_to_remove)
        db.session.commit()
    return redirect(url_for('users_page'))


def modify_shopkeepers(shop_id):
    if not shop_id:
        flash("Shop ID is required.", "error")
        return redirect(url_for('modify_shopkeepers'))
    shop = Shop.query.get(shop_id)
    if not shop:
        flash("Shop not found", "error")
        return redirect(url_for('modify_shopkeepers'))

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

        return redirect(url_for('modify_shopkeepers_method', shop_id=shop_id))

    return render_template('modify_shopkeepers.html', shop=shop, users=users, current_shopkeepers=current_shopkeepers)