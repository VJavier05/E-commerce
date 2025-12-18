from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from wtforms import StringField, PasswordField,SubmitField,BooleanField, ValidationError, DateField, SelectField, RadioField, TextAreaField, DecimalField, IntegerField, FieldList, FormField,MultipleFileField,SelectMultipleField
from wtforms.validators import DataRequired, Length,Email, EqualTo, Optional,NumberRange
from app.models import Users
import phonenumbers

class RegistrationForm(FlaskForm):

    first_name = StringField('First Name',validators=[DataRequired(),Length(min=2,max=20)])
    last_name = StringField('Last Name',validators=[DataRequired(),Length(min=2,max=20)])

    email = StringField('Email',validators=[DataRequired(),Email()])

    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    

    picture_id = FileField('Upload ID', validators=[FileRequired(message='ID is required.'),FileAllowed(['jpg', 'png'], 'Only JPG and PNG files are allowed.')])

    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])

    policy = BooleanField('I agree to the privacy,',validators=[DataRequired()])

    submit = SubmitField('Register')


    def validate_email(self,email):

        user = Users.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('That Email is already taken!')


class LoginForm(FlaskForm):

    email = StringField('Email',validators=[DataRequired(),Email()])

    password = PasswordField('Password',validators=[DataRequired()])

    remember = BooleanField('Remember Me')

    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):

    first_name = StringField('First Name',validators=[DataRequired(),Length(min=2,max=20)])
    last_name = StringField('Last Name',validators=[DataRequired(),Length(min=2,max=20)])

    email = StringField('Email',validators=[DataRequired(),Email()])

    picture = FileField('Update Profile Pic',validators=[FileAllowed(['jpg','png'])])
    
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])

    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    
    submit = SubmitField('Update')


    def validate_email(self,email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()

            if user:
                raise ValidationError('That Email is already taken!')
            
class AddAddress(FlaskForm):

    address_name = StringField('Address Title', validators=[DataRequired(), Length(min=2, max=255)])
    
    street = StringField('Street', validators=[DataRequired(), Length(min=2, max=255)])
    barangay = SelectField('Barangay',validate_choice=False, validators=[DataRequired()])
    city = SelectField('City',validate_choice=False, validators=[DataRequired()])
    province = SelectField('Province',validate_choice=False, validators=[DataRequired()])
    region = SelectField('Region',validate_choice=False, validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(min=2, max=4)])
    telephone_no = StringField('Telephone Number', validators=[DataRequired(), Length(min=2, max=20)])
    
    submit = SubmitField('Add Address')
    
    def validate_telephone_no(self, telephone_no):
        if telephone_no.data:
            try:
                parsed_phone = phonenumbers.parse(telephone_no.data, None)
                if not phonenumbers.is_valid_number(parsed_phone):
                 
                    raise ValidationError('Invalid phone number.')
                    
            except phonenumbers.NumberParseException:
                raise ValidationError('Invalid phone number format.')



# REQUEST RESET
class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('No account found with that email.')


#RESET PASS FORM
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')



class UpdateAdminProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_file = FileField('Upload New Photo', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Save changes')

    def validate_email(self,email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()

            if user:
                raise ValidationError('That Email is already taken!')
            

class UpdateSellerProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_file = FileField('Upload New Photo', validators=[FileAllowed(['jpg', 'png'])])
    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Save changes')

    def validate_email(self,email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()

            if user:
                raise ValidationError('That Email is already taken!')
            


class RegistrationFormSeller(FlaskForm):

    first_name = StringField('First Name',validators=[DataRequired(),Length(min=2,max=20)])
    last_name = StringField('Last Name',validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    picture_id = FileField('Valid ID', validators=[FileRequired(message='ID is required.'),FileAllowed(['jpg', 'png'], 'Only JPG and PNG files are allowed.')])
    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Register')


    def validate_email(self,email):

        user = Users.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError('That Email is already taken!')
        
class ShopInformationForm(FlaskForm):
    shop_name = StringField('Shop Name', validators=[DataRequired(), Length(min=2, max=50)])
    category = SelectMultipleField('Category', choices=[
        ('dresses_skirts', 'Dresses & Skirts'),
        ('tops_blouses', 'Tops & Blouses'),
        ('activewear', 'Activewear & Yoga Pants'),
        ('lingerie', 'Lingerie & Sleepwear'),
        ('jackets_coats', 'Jackets & Coats'),
        ('shoes_accessories', 'Shoes & Accessories'),
    ], validators=[DataRequired()])


    street = StringField('Street', validators=[DataRequired(), Length(min=2, max=255)])
    barangay = SelectField('Barangay', validate_choice=False, validators=[DataRequired()])
    city = SelectField('City', validate_choice=False, validators=[DataRequired()])
    province = SelectField('Province', validate_choice=False, validators=[DataRequired()])
    region = SelectField('Region', validate_choice=False, validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(min=2, max=4)])


    business_id = FileField('Business Permit', validators=[FileRequired(message='ID is required.'),FileAllowed(['jpg', 'png'], 'Only JPG and PNG files are allowed.')])

    policy = BooleanField('I accept the')

    submit = SubmitField('Register')

    def validate_policy(self, field):
        if not field.data:
            raise ValidationError('Please accept the terms and conditions.')
        


class UpdateShopInformationForm(FlaskForm):
    shop_name = StringField('Shop Name', validators=[DataRequired(), Length(min=2, max=50)])
    category = SelectMultipleField('Category', choices=[
        ('dresses_skirts', 'Dresses & Skirts'),
        ('tops_blouses', 'Tops & Blouses'),
        ('activewear', 'Activewear & Yoga Pants'),
        ('lingerie', 'Lingerie & Sleepwear'),
        ('jackets_coats', 'Jackets & Coats'),
        ('shoes_accessories', 'Shoes & Accessories'),
    ], validators=[DataRequired()])


    street = StringField('Street', validators=[DataRequired(), Length(min=2, max=255)])
    barangay = StringField('Barangay',validators=[DataRequired(), Length(min=2, max=255)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=255)])
    province = StringField('Province', validators=[DataRequired(), Length(min=2, max=255)])
    region = StringField('Region', validators=[DataRequired(), Length(min=2, max=255)])
    postal_code = StringField('Postal Code', validators=[DataRequired(), Length(min=2, max=4)])
    image_file = FileField('Upload New Photo', validators=[FileAllowed(['jpg', 'png'])])



    submit = SubmitField('Update Shop')


class ProductForm(FlaskForm):
    product_name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=100)])
    category = SelectField('Category', 
        choices=[
            ('dress', 'Dress'),
            ('skirt', 'Skirt'),
            ('top', 'Top'),
            ('blouse', 'Blouse'),
            ('activewear', 'Activewear'),
            ('lingerie', 'Lingerie'),
            ('jackets', 'Jackets'),
            ('coats', 'Coats'),
            ('shoes', 'Shoes'),
            ('accessories', 'Accessories'),
        ], 
        validators=[DataRequired()]
    )


    
    brand = StringField('Brand', validators=[DataRequired(), Length(min=2, max=100)])
    
    material = StringField('Material', validators=[DataRequired(), Length(min=2, max=100)])

    description = TextAreaField('Product Description', validators=[DataRequired(), Length(min=10, max=2000)])
    product_images = MultipleFileField('Product Images', validators=[FileAllowed(['jpg', 'png'], 'Images only!')],
                                    description='Upload product images')
    submit = SubmitField('Save Product')

    def validate_product_images(self, product_images):
        if len(product_images.data) == 0:
            raise ValidationError('At least one image must be uploaded.')
        
    def validate_description(self, field):
        field.data = field.data.strip()  # Trim whitespace
        if len(field.data) < 10:
            raise ValidationError('Description must be at least 10 characters long.')






class VariationForm(FlaskForm):
    color = StringField('Color', validators=[Optional(), Length(min=1, max=30)])
    size = StringField('Size', validators=[Optional(), Length(min=1, max=20)])

class AddProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = StringField('Description', validators=[DataRequired(), Length(max=2000)])
    price = DecimalField('Price', validators=[DataRequired()])
    category = SelectField('Category', choices=[('category1', 'Category 1'), ('category2', 'Category 2')])
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    variations = FieldList(FormField(VariationForm), min_entries=1)




class CourierForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])    
    contact_number = StringField('Contact Number',validators=[DataRequired(), Length(min=10, max=20)])
    
    email = StringField('Email',validators=[DataRequired(), Email(), Length(max=120)])
    
    street = StringField('Street', validators=[DataRequired(), Length(min=2, max=255)])
    barangay = SelectField('Barangay', validate_choice=False, validators=[DataRequired()])
    city = SelectField('City', validate_choice=False, validators=[DataRequired()])
    province = SelectField('Province', validate_choice=False, validators=[DataRequired()])
    region = SelectField('Region', validate_choice=False, validators=[DataRequired()])
    service_area = StringField('Service Area',validators=[DataRequired(), Length(max=255)])
    
    vehicle_type = SelectField('Vehicle Type', choices=[
            ('car', 'Car'),
            ('motorcycle', 'Motorcycle'),
            ('bicycle', 'Bicycle'),
            ('truck', 'Truck'),
            ('van', 'Van')
        ], validators=[DataRequired()])     
    vehicle_registration_no = StringField('Vehicle Registration No', validators=[DataRequired(), Length(max=50)])
    
    
    id_picture = FileField('ID Picture', validators=[
            FileRequired(message="ID picture is required."),
            FileAllowed(['jpg', 'png'], 'Images only!')
        ])    
    
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])

    submit = SubmitField('Save Courier')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already in use. Please choose a different one.')
        


        

class UpdateCourierProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    image_file = FileField('Upload New Photo', validators=[FileAllowed(['jpg', 'png'])])
    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])


    street = StringField('Street', validators=[DataRequired(), Length(min=2, max=255)])
    barangay = StringField('Barangay', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    province = StringField('Province', validators=[DataRequired()])
    region = StringField('Region', validators=[DataRequired()])
    service_area = StringField('Service Area',validators=[DataRequired(), Length(max=255)])

    vehicle_type = SelectField('Vehicle Type', choices=[
            ('car', 'Car'),
            ('motorcycle', 'Motorcycle'),
            ('bicycle', 'Bicycle'),
            ('truck', 'Truck'),
            ('van', 'Van')
        ], validators=[DataRequired()]) 


    submit = SubmitField('Save changes')

    def validate_email(self,email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()

            if user:
                raise ValidationError('That Email is already taken!')
            






class ReviewForm(FlaskForm):
    # Rating field with options from 1 to 5
    rating = RadioField(
        "Rating",
        choices=[(5, "5"), (4, "4"), (3, "3"), (2, "2"), (1, "1")],
        coerce=int,
        validators=[DataRequired(message="Please select a rating.")],
    )

    # Title field for the review
    title = StringField(
        "Title",
        validators=[
            DataRequired(message="Please provide a title for your review."),
            Length(max=100, message="The title must not exceed 100 characters."),
        ],
    )

    # Content field for the review
    content = TextAreaField(
        "Review",
        validators=[
            DataRequired(message="Please provide content for your review."),
            Length(min=10, message="The review must be at least 10 characters long."),
        ],
    )

    # Optional image upload field
    images = FileField(
        "Upload Images (Optional)",
        validators=[
            Optional(),
            FileAllowed(["jpg", "jpeg", "png", "gif"], "Only image files are allowed."),
        ],
    )

    # Submit button
    submit = SubmitField("Submit Review")



class TwoFactorForm(FlaskForm):
    code = StringField('2FA Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify')