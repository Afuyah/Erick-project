from app import db, Customer

# Create Flask app and push an application context
from app import app
app.app_context().push()

# Create an admin user
admin_user = Customer(
    name='jsync',
    email='jsync@gmail.com',
    phone_number='0711667718',
    address='All over',
    password='Henrix@54',
    is_admin=True
)

# Add the admin user to the database
db.session.add(admin_user)
db.session.commit()

print("Admin user created successfully.")
