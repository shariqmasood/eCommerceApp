# ====================
# models.py
# ====================
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """Represents a registered user with email and hashed password."""
    __tablename__ = 'users'
    id       = db.Column(db.Integer, primary_key=True)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    pw_hash  = db.Column(db.String(128), nullable=False)
    # Relationships: one user has many cart items and orders
    cart_items = db.relationship('CartItem', backref='user', cascade='all, delete-orphan', lazy='dynamic')
    orders     = db.relationship('Order', backref='user', cascade='all, delete-orphan', lazy='dynamic')

class Product(db.Model):
    """A product available for purchase."""
    __tablename__ = 'products'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price_cents = db.Column(db.Integer, nullable=False)  # stored in cents
    image_url   = db.Column(db.String(200))
    # Reverse relationships
    cart_items  = db.relationship('CartItem', backref='product', lazy='dynamic')
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')

class CartItem(db.Model):
    """An item in a user's shopping cart."""
    __tablename__ = 'cart_items'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity   = db.Column(db.Integer, default=1)

class Order(db.Model):
    """A completed payment session linked to OrderItems."""
    __tablename__ = 'orders'
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stripe_sid = db.Column(db.String(100), nullable=False)  # repurposed for 2CO sale_id
    paid       = db.Column(db.Boolean, default=False)
    # One order → many line items
    items      = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan', lazy='dynamic')

class OrderItem(db.Model):
    """A single line item under an Order."""
    __tablename__ = 'order_items'
    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity   = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)  # price at time of purchase