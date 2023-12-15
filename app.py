from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from forms import RegistrationForm
from email_validator import validate_email, EmailNotValidError
from sqlalchemy import func
import os
import secrets
import smtplib
from datetime import datetime



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


# Route for home page
@app.route('/')
def home():
    return render_template('home.html')


  # Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
      if request.method == 'POST':
          email = request.form.get('email')
          password = request.form.get('password')
          user = Customer.query.filter_by(email=email).first()
          if user and user.password == password:
              login_user(user)

              # Check if the user is an admin
              if user.is_admin:
                  return redirect(url_for('admin_dashboard'))
              else:
                  return redirect(url_for('dashboard'))
          else:
              flash('Invalid email or password. Please try again.', 'error')
      return render_template('login.html')



  # Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
      form = RegistrationForm()

      if form.validate_on_submit():
          print("Form Data:", form.data)  # Debugging statement

          # Check if the email is already registered
          existing_user = Customer.query.filter_by(email=form.email.data).first()
          if existing_user:
              flash('Email already registered. Please use a different email.', 'error')
              return redirect(url_for('register'))

          # Validate email using email-validator
          try:
              v = validate_email(form.email.data)
              form.email.data = v.email
          except EmailNotValidError as e:
              flash(f'Invalid email: {e}', 'error')
              return redirect(url_for('register'))

          # Check if the password and confirm password match
          if form.password.data != form.confirm_password.data:
              flash('Password and Confirm Password must match.', 'error')
              return redirect(url_for('register'))

          # Create a new user
          new_user = Customer(
              name=form.name.data,
              email=form.email.data,
              phone_number=form.phone_number.data,
              address=form.address.data,
              password=form.password.data
          )

          print("New User Data Before Commit:", new_user.__dict__)  # Debugging statement

          db.session.add(new_user)
          db.session.commit()

          print("New User Data After Commit:", new_user.__dict__)  # Debugging statement

          flash('Account created successfully! You can now log in.', 'success')
          return redirect(url_for('login'))

      # Pass the 'form' variable to the template
      return render_template('register.html', form=form)


# Route for dashboard
@app.route('/admin_dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.name}! You are logged in.'

def dashboard():
    user_info = {
        'Name': current_user.name,
        'Email': current_user.email,
        'Orders': current_user.orders,
        'Notifications': []  # Placeholder for notifications; you can customize this based on your needs
    }

    return render_template('dashboard.html', user_info=user_info)

from flask import Flask, render_template, request, redirect, url_for, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from forms import RegistrationForm
from email_validator import validate_email, EmailNotValidError
from sqlalchemy import func
import os
import secrets
import smtplib
from datetime import datetime



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


# Route for home page
@app.route('/')
def home():
    return render_template('home.html')


  # Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
      if request.method == 'POST':
          email = request.form.get('email')
          password = request.form.get('password')
          user = Customer.query.filter_by(email=email).first()
          if user and user.password == password:
              login_user(user)

              # Check if the user is an admin
              if user.is_admin:
                  return redirect(url_for('admin_dashboard'))
              else:
                  return redirect(url_for('dashboard'))
          else:
              flash('Invalid email or password. Please try again.', 'error')
      return render_template('login.html')



  # Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
      form = RegistrationForm()

      if form.validate_on_submit():
          print("Form Data:", form.data)  # Debugging statement

          # Check if the email is already registered
          existing_user = Customer.query.filter_by(email=form.email.data).first()
          if existing_user:
              flash('Email already registered. Please use a different email.', 'error')
              return redirect(url_for('register'))

          # Validate email using email-validator
          try:
              v = validate_email(form.email.data)
              form.email.data = v.email
          except EmailNotValidError as e:
              flash(f'Invalid email: {e}', 'error')
              return redirect(url_for('register'))

          # Check if the password and confirm password match
          if form.password.data != form.confirm_password.data:
              flash('Password and Confirm Password must match.', 'error')
              return redirect(url_for('register'))

          # Create a new user
          new_user = Customer(
              name=form.name.data,
              email=form.email.data,
              phone_number=form.phone_number.data,
              address=form.address.data,
              password=form.password.data
          )

          print("New User Data Before Commit:", new_user.__dict__)  # Debugging statement

          db.session.add(new_user)
          db.session.commit()

          print("New User Data After Commit:", new_user.__dict__)  # Debugging statement

          flash('Account created successfully! You can now log in.', 'success')
          return redirect(url_for('login'))

      # Pass the 'form' variable to the template
      return render_template('register.html', form=form)


# Route for dashboard
@app.route('/admin_dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.name}! You are logged in.'

def dashboard():
    user_info = {
        'Name': current_user.name,
        'Email': current_user.email,
        'Orders': current_user.orders,
        'Notifications': []  # Placeholder for notifications; you can customize this based on your needs
    }

    return render_template('dashboard.html', user_info=user_info)



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
    # Route to display all users
@app.route('/all_users')
def all_users():
    all_users_data = Customer.query.all()
    return render_template('all_users.html', all_users=all_users_data)
# Route to display all locations
@app.route('/all_locations')
def all_locations():
    all_locations_data = Location.query.all()
    return render_template('all_locations.html', all_locations=all_locations_data)


  # Route to display all products with their categories and prices
@app.route('/all_products')
def all_products():
      with current_app.app_context():
          all_products_data = Product.query.join(Category).with_entities(
              Product.name.label('product_name'),
              Category.name.label('category_name'),
              Product.price
          ).all()

      return render_template('all_products.html', all_products=all_products_data)



# Route to display all orders with detailed information including customer name, location, order items, and prices
@app.route('/all_orders_info')
def all_orders_info():
    all_orders_data = Order.query.join(Customer).join(Location).join(CartItem).join(Product).with_entities(
        Order.id.label('order_id'),
        Customer.name.label('customer_name'),
        Location.name.label('location_name'),
        CartItem.quantity.label('item_quantity'),
        Product.name.label('product_name'),
        Product.price.label('product_price')
    ).all()

    return render_template('all_orders_info.html', all_orders_info=all_orders_data)
  
  # Define a ContactMessage model
class ContactMessage(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String(50), nullable=False)
      email = db.Column(db.String(50), nullable=False)
      message = db.Column(db.Text, nullable=False)
      timestamp = db.Column(db.DateTime, default=datetime.utcnow)

  # Modify the route to store the message in the database
@app.route('/handle_contact_form', methods=['POST'])
def handle_contact_form():
    contact_name = request.form.get('contactName')
    contact_email = request.form.get('contactEmail')
    message_content = request.form.get('message')

    current_app.logger.debug(f"Received form data - Name: {contact_name}, Email: {contact_email}, Message: {message_content}")

    # Create a new ContactMessage object
    new_message = ContactMessage(name=contact_name, email=contact_email, message=message_content)

    # Add and commit the new message to the database
    db.session.add(new_message)
    db.session.commit()

    current_app.logger.debug(f"Message added to the database - ID: {new_message.id}")

    flash('Your message has been sent!', 'success')
    return redirect(url_for('home'))
# Route to display all admin users
@app.route('/all_admin_users')
@login_required  # Make sure to protect this route so that only logged-in users can access it
def all_admin_users():
    # Check if the current user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to view admin users.', 'error')
        return redirect(url_for('home'))

    # Fetch all admin users
    admin_users_data = Customer.query.filter_by(is_admin=True).all()

    return render_template('all_admin_users.html', admin_users=admin_users_data)

with app.app_context():
  db.create_all()

if __name__ == '__main__':
  app.debug = True
  app.run(host='0.0.0.0', port=81)






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
    # Route to display all users
@app.route('/all_users')
def all_users():
    all_users_data = Customer.query.all()
    return render_template('all_users.html', all_users=all_users_data)
# Route to display all locations
@app.route('/all_locations')
def all_locations():
    all_locations_data = Location.query.all()
    return render_template('all_locations.html', all_locations=all_locations_data)


  # Route to display all products with their categories and prices
@app.route('/all_products')
def all_products():
      with current_app.app_context():
          all_products_data = Product.query.join(Category).with_entities(
              Product.name.label('product_name'),
              Category.name.label('category_name'),
              Product.price
          ).all()

      return render_template('all_products.html', all_products=all_products_data)



# Route to display all orders with detailed information including customer name, location, order items, and prices
@app.route('/all_orders_info')
def all_orders_info():
    all_orders_data = Order.query.join(Customer).join(Location).join(CartItem).join(Product).with_entities(
        Order.id.label('order_id'),
        Customer.name.label('customer_name'),
        Location.name.label('location_name'),
        CartItem.quantity.label('item_quantity'),
        Product.name.label('product_name'),
        Product.price.label('product_price')
    ).all()

    return render_template('all_orders_info.html', all_orders_info=all_orders_data)
  
  # Define a ContactMessage model
class ContactMessage(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String(50), nullable=False)
      email = db.Column(db.String(50), nullable=False)
      message = db.Column(db.Text, nullable=False)
      timestamp = db.Column(db.DateTime, default=datetime.utcnow)

  # Modify the route to store the message in the database
@app.route('/handle_contact_form', methods=['POST'])
def handle_contact_form():
    contact_name = request.form.get('contactName')
    contact_email = request.form.get('contactEmail')
    message_content = request.form.get('message')

    current_app.logger.debug(f"Received form data - Name: {contact_name}, Email: {contact_email}, Message: {message_content}")

    # Create a new ContactMessage object
    new_message = ContactMessage(name=contact_name, email=contact_email, message=message_content)

    # Add and commit the new message to the database
    db.session.add(new_message)
    db.session.commit()

    current_app.logger.debug(f"Message added to the database - ID: {new_message.id}")

    flash('Your message has been sent!', 'success')
    return redirect(url_for('home'))
# Route to display all admin users
@app.route('/all_admin_users')
@login_required  # Make sure to protect this route so that only logged-in users can access it
def all_admin_users():
    # Check if the current user is an admin
    if not current_user.is_admin:
        flash('You do not have permission to view admin users.', 'error')
        return redirect(url_for('home'))

    # Fetch all admin users
    admin_users_data = Customer.query.filter_by(is_admin=True).all()

    return render_template('all_admin_users.html', admin_users=admin_users_data)

with app.app_context():
  db.create_all()

if __name__ == '__main__':
  app.debug = True
  app.run(host='0.0.0.0', port=81)








