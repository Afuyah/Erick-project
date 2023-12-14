from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from forms import RegistrationForm



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grocery_store.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a secure secret key
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Replace with your email server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'your_username'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'  # Replace with your email

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

# Define models
class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Add an admin flag

@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))

    return Customer.query.get(int(user_id))
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    images = db.Column(db.String(500), nullable=True)  # Assuming a comma-separated list of image URLs
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    location = db.relationship('Location', backref=db.backref('orders', lazy=True))
    status = db.Column(db.String(20), default='pending')  # New field to track order status

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))
    quantity = db.Column(db.Integer, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    order = db.relationship('Order', backref=db.backref('cart_items', lazy=True))

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)

# Create tables
with app.app_context():
    db.create_all()

# Routes and views

# Route for home
@app.route('/')
def home():
    return render_template('home.html')
# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # Check if the email is already registered
        existing_user = Customer.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'error')
            return redirect(url_for('register'))

        # Create a new user
        new_user = Customer(
            name=form.name.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            address=form.address.data,
            password=form.password.data
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Customer.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    return render_template('login.html')

# Route for dashboard
@app.route('/admin_dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.name}! You are logged in.'

# Route to add admin user (you may want to secure this route in a production environment)
@app.route('/add_admin')
def add_admin():
    # Check if the admin already exists
    existing_admin = Customer.query.filter_by(email='jhsync@gmail.com').first()
    if existing_admin:
        return 'Admin already exists.'

    # Create a new admin user
    admin = Customer(
        name='Admin',  # Adjust the name as needed
        email='jhsync@gmail.com',
        phone_number='1234567890',  # Adjust the phone number as needed
        address='Admin Address',  # Adjust the address as needed
        password=generate_password_hash('Henrix@54', method='sha256'),  # Hash the password
        is_admin=True
    )

    db.session.add(admin)
    db.session.commit()

    return 'Admin added successfully.'

# Route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Route for checkout
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        location_id = request.form.get('location')  # Assuming you have a form field named 'location'
        location = Location.query.get(location_id)

        # Create an order associated with the selected location
        order = Order(customer=current_user, location=location)
        db.session.add(order)

        # Move cart items to the order
        cart_items = CartItem.query.filter_by(order_id=None, product_id=current_user.id).all()
        for cart_item in cart_items:
            cart_item.order = order
            db.session.add(cart_item)

        db.session.commit()

        # Send email to admin for order confirmation
        admin_email = 'admin@example.com'  # Replace with your admin's email
        send_email('Order Confirmation Required', f'Order from {current_user.name} is pending confirmation.', [admin_email])

        flash('Order placed successfully! The admin will confirm your order shortly.', 'success')
        return redirect(url_for('dashboard'))

    locations = Location.query.all()
    return render_template('checkout.html', locations=locations)

# ...

# Route for admin to confirm order
@app.route('/admin/confirm_order/<int:order_id>')
@login_required
def confirm_order(order_id):
  
    # Check if the current user is an admin (you may need to implement admin authentication)
    if current_user.is_admin:
        order = Order.query.get(order_id)
        if order:
            order.status = 'confirmed'
            db.session.commit()

            # Send email to the customer for order confirmation
            send_email('Order Confirmed', f'Your order has been confirmed. Thank you for shopping with us!', [order.customer.email])

            flash(f'Order {order_id} has been confirmed.', 'success')
        else:
            flash('Order not found.', 'error')
    else:
        flash('You do not have permission to confirm orders.', 'error')

    return redirect(url_for('admin_dashboard'))  # Adjust the route name as needed

# ...
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=81)