from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint

app = Flask(__name__)
app.secret_key = 'asdhfauisdhfuhi'  # Required for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food_waste_new.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    role = db.Column(db.String, nullable=False)
    aura_points = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime, default=db.func.current_timestamp())
    creation_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    __table_args__ = (
        CheckConstraint("role IN ('user', 'shopkeeper', 'admin')", name="valid_role"),
    )
    


class Shop(db.Model):
    __tablename__ = 'shop'
    shop_id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String, nullable=False)
    store_chain = db.Column(db.String)
    location_address = db.Column(db.String)
    location_gps = db.Column(db.String)
    user_created = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    creation_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    prices = db.relationship('Price', backref='shop', lazy=True)


class WorksFor(db.Model):
    __tablename__ = 'works_for'
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.shop_id'), primary_key=True)

    # Relationships
    user = db.relationship('User', backref=db.backref("works_for", cascade="all, delete-orphan"))
    shop = db.relationship('Shop', backref=db.backref("works_for", cascade="all, delete-orphan"))


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

    # Relationships
    prices = db.relationship('Price', backref='product', lazy=True)


class Price(db.Model):
    __tablename__ = 'price'
    price_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'), nullable=False)
    shop_id = db.Column(db.Integer, db.ForeignKey('shop.shop_id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float)
    waste_discount_percentage = db.Column(db.Float)
    report_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    valid_from_date = db.Column(db.DateTime)
    valid_to_date = db.Column(db.DateTime)
    user_created = db.Column(db.Integer, db.ForeignKey('user.user_id'))