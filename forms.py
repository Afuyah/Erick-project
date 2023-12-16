# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    # New field for admin registration
    is_admin = BooleanField('Register as Admin')
    submit = SubmitField('Register')

class AddProductForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired()])
    product_description = StringField('Product Description')
    product_price = FloatField('Product Price', validators=[DataRequired()])
    category_id = IntegerField('Category ID', validators=[DataRequired()])
    submit = SubmitField('Add Product')