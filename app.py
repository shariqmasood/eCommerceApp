# ====================
# app.py
# ====================
# Brief overview: This Flask application implements a simple e-commerce store
# with user authentication, product catalog, shopping cart, and a hosted
# checkout integration with 2Checkout. It uses Flask-Login for auth,
# SQLAlchemy for ORM, and environment-based config for deployment.

# two users have been registered
# shariqmasood@gmail.com password: hello
# shariq_150@yahoo.com password: film


import os
import datetime
from dotenv import load_dotenv
# Load environment variables early so Config picks up SECRET_KEY, DB URL, etc.
load_dotenv()

from urllib.parse import urlencode
from flask import (
    Flask, render_template, redirect,
    url_for, request, flash, current_app
)
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Product, CartItem, Order, OrderItem


def create_app():
    """
    Factory to create and configure the Flask app.
    Initializes DB, login manager, and registers all routes.
    """
    app = Flask(__name__)
    app.config.from_object(Config)  # Load settings from config.py

    # Initialize database and login manager
    db.init_app(app)
    login_mgr = LoginManager(app)
    login_mgr.login_view = 'login'

    @login_mgr.user_loader
    def load_user(user_id):
        # Given a user_id, return the User object
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_current_year():
        # Make current_year available in all templates
        return {'current_year': datetime.datetime.utcnow().year}

    # ----------------------
    # Authentication routes
    # ----------------------

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """
        GET: Render registration form.
        POST: Validate input, create new user, flash feedback, redirect.
        """
        if request.method == 'POST':
            email     = request.form['email']
            pw        = request.form['password']
            pw_conf   = request.form.get('confirm_password', '')

            # Ensure password and confirmation match
            if pw != pw_conf:
                flash('Passwords do not match.', 'warning')
                return redirect(url_for('register'))

            # Check if email already exists
            if User.query.filter_by(email=email).first():
                flash('Email already registered.', 'warning')
                return redirect(url_for('register'))

            # Hash password and save new user
            user = User(email=email, pw_hash=generate_password_hash(pw))
            db.session.add(user)
            db.session.commit()

            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))

        # Render registration page
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """
        GET: Render login form.
        POST: Authenticate user, flash feedback, redirect.
        """
        if request.method == 'POST':
            email = request.form['email']
            pw    = request.form['password']
            user  = User.query.filter_by(email=email).first()

            # Validate credentials
            if not user or not check_password_hash(user.pw_hash, pw):
                flash('Invalid email or password.', 'danger')
                return redirect(url_for('login'))

            # Log in and redirect home
            login_user(user)
            flash(f'Welcome back, {user.email}!', 'success')
            return redirect(url_for('index'))

        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        """Log out user, flash confirmation, redirect to home."""
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    # ----------------------
    # Product catalog & cart
    # ----------------------

    @app.route('/')
    def index():
        # Show all products on the home page
        products = Product.query.all()
        return render_template('index.html', products=products)

    @app.route('/product/<int:pid>')
    def product(pid):
        # Detail page for a single product
        prod = Product.query.get_or_404(pid)
        return render_template('product.html', product=prod)

    @app.route('/cart')
    @login_required
    def cart():
        # Show current user's cart and total
        items = CartItem.query.filter_by(user_id=current_user.id).all()
        total = sum(ci.quantity * ci.product.price_cents for ci in items)
        return render_template('cart.html', items=items, total=total)

    @app.route('/cart/add/<int:pid>')
    @login_required
    def add_to_cart(pid):
        # Add one unit of given product to cart
        ci = CartItem.query.filter_by(user_id=current_user.id, product_id=pid).first()
        if ci:
            ci.quantity += 1
        else:
            ci = CartItem(user_id=current_user.id, product_id=pid, quantity=1)
            db.session.add(ci)
        db.session.commit()
        flash('Added to cart.', 'success')
        return redirect(url_for('cart'))

    @app.route('/cart/remove/<int:cid>')
    @login_required
    def remove_from_cart(cid):
        # Remove a cart item by its ID
        CartItem.query.filter_by(id=cid, user_id=current_user.id).delete()
        db.session.commit()
        flash('Removed from cart.', 'info')
        return redirect(url_for('cart'))

    # ----------------------
    # 2Checkout hosted checkout
    # ----------------------
    @app.route('/create-checkout-session', methods=['POST'])
    @login_required
    def create_checkout():
        """
        Build an HTML form payload and auto-post to 2Checkout's legacy
        purchase endpoint with demo=Y for test orders. Users manually
        return via "Return to Merchant" link.
        """
        items = CartItem.query.filter_by(user_id=current_user.id).all()
        # Prepare hidden inputs
        inputs = {
            'sid':   current_app.config['TCO_SELLER_ID'],
            'mode':  '2CO',
            'demo':  'Y',
            'x_receipt_link_url': url_for('success', _external=True)
        }
        # Add line items dynamically
        for i, ci in enumerate(items):
            inputs[f'li_{i}_name']     = ci.product.name
            inputs[f'li_{i}_price']    = f"{ci.product.price_cents/100:.2f}"
            inputs[f'li_{i}_quantity'] = str(ci.quantity)
        # Render a small form that auto-submits
        return render_template(
            '2co_redirect.html',
            action_url='https://www.2checkout.com/checkout/purchase',
            inputs=inputs
        )

    @app.route('/success')
    @login_required
    def success():
        """
        Handle the return from 2Checkout. If sale_id present, record order,
        migrate CartItems into OrderItems, clear cart, and show summary.
        """
        sale_id = request.args.get('sale_id')
        if not sale_id:
            flash('Payment not completed.', 'danger')
            return redirect(url_for('cart'))
        order = Order(user_id=current_user.id, stripe_sid=f'2CO:{sale_id}', paid=True)
        db.session.add(order)
        db.session.flush()  # assign order.id
        for ci in CartItem.query.filter_by(user_id=current_user.id):
            db.session.add(OrderItem(
                order_id   = order.id,
                product_id = ci.product_id,
                quantity   = ci.quantity,
                unit_price = ci.product.price_cents
            ))
            db.session.delete(ci)
        db.session.commit()
        return render_template('checkout.html', order=order)

    return app


if __name__ == '__main__':
    # Bootstrap application and auto-create DB tables
    app = create_app()
    with app.app_context():
        db.create_all()
    # Run in debug mode for development
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)