from datetime import datetime, time, timedelta,timezone
import os
import secrets
from PIL import Image
from functools import wraps
from flask import g, render_template, url_for, flash,redirect, request, abort,make_response,session,json,send_file
from app import app, db, bcrypt, mail
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, AddAddress,RequestResetForm, ResetPasswordForm,UpdateAdminProfileForm,RegistrationFormSeller,ShopInformationForm,UpdateSellerProfileForm,UpdateShopInformationForm,ProductForm,CourierForm,UpdateCourierProfileForm,TwoFactorForm


from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message


from app.models import (
    LoginAttempt,
    Users,
    Admin, 
    Seller, 
    UserAddress,
    Product,
    ProductVariation,
    ProductImage,
    CartItem,
    OrderItem,
    Order,
    Courier,
    Pickup,
    pickup_orderitem,
    Review,
    ReviewImage,
    Messages, 
    Notification,
    UserNotification,
    Voucher,
    UserVoucher, 
    StockNotification,
    StockHistory
) 
from flask_login import login_user, current_user, logout_user, login_required
from flask import jsonify, request
import requests
from flask_caching import Cache
import base64
from werkzeug.utils import secure_filename
import uuid

import json
from werkzeug.utils import secure_filename
from sqlalchemy.orm import aliased,joinedload
from sqlalchemy import and_, func, or_, extract, func, desc
from collections import defaultdict
import logging
import time
import csv
from io import StringIO
from typing import List, Dict
import random, string
import xlsxwriter

from flask_restful import Api, Resource
from flask_cors import CORS
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.context_processor
def inject_user():
    if current_user.is_authenticated:
        # Check if the current user is a seller
        seller = Seller.query.filter_by(user_id=current_user.id).first()  # Adjust based on your Seller model structure

        if seller:
            # If the user is a seller, get the image from the Seller table
            image_file = url_for('static', filename='profile_pics/' + seller.image_file)  # Adjust the path as necessary

        else:
            # If the user is authenticated but not a seller, use the user's image
            image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    else:
        image_file = url_for('static', filename='profile_pics/default.jpg')  # Default image if user is not logged in

    return {
        'user': current_user,
        'image_file_profile': image_file
    }


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                return redirect(url_for('login')) 
            
            # Check if the user has the required role
            if current_user.role != role:
                return redirect(url_for('home')) 
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.errorhandler(403)
def forbidden(error):
    return render_template('pages-misc-error.html'), 403


def auto_confirm_order_received():
    five_days_ago = datetime.utcnow() - timedelta(days=5)

    # Query all pickups delivered more than 5 days ago
    pickups = Pickup.query.filter(
        Pickup.delivered_at <= five_days_ago,
        Pickup.status == "Delivered"
    ).all()

    processed_sellers = set()

    for pickup in pickups:
        for order_item in pickup.order_items:
            if order_item.status == "Delivered":  # Confirm only delivered items
                # Check if we need to add the shipping fee for this seller
                if order_item.seller_id not in processed_sellers:
                    seller_shipping_fee = 45  # Adjust as needed
                    order_item.update_seller_income(seller_shipping_fee)
                    processed_sellers.add(order_item.seller_id)
                else:
                    # Call without adding the shipping fee again for the same seller
                    order_item.update_seller_income(0)

                # Mark the item as "Received"
                order_item.status = "Received"

        # Mark the pickup status as "Confirmed" to avoid reprocessing
        pickup.status = "Confirmed"

    # Commit all changes
    db.session.commit()





@app.route("/", methods=['GET', 'POST'])
@app.route("/home")
def home():

    # Run only if not already checked (GOOD FOR EVERYDAY)
    if not session.get('auto_confirm_checked'):  
        auto_confirm_order_received()
        session['auto_confirm_checked'] = True

    # IF DEDEBUGG MO
    # auto_confirm_order_received()
    
    cart = session.get('cart', {}) 
    new_arrivals = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(10).all()

    clothing_categories = ['dress', 'skirt', 'top', 'blouse', 'activewear', 'lingerie', 'jackets', 'coats']
    clothes = Product.query.filter(Product.category.in_(clothing_categories), Product.is_active == True).order_by(Product.created_at.desc()).limit(10).all()


    shoes_categories = ['shoes']  
    shoes = Product.query.filter(Product.category.in_(shoes_categories), Product.is_active == True).order_by(Product.created_at.desc()).limit(10).all()

    accessories_categories = ['accessories']  
    accessories = Product.query.filter(Product.category.in_(accessories_categories), Product.is_active == True).order_by(Product.created_at.desc()).limit(10).all()


    top_rated_products = db.session.query(Product)\
    .join(Review, Review.product_id == Product.id)\
    .options(db.joinedload(Product.images))\
    .filter(Product.is_active == True).group_by(Product.id)\
    .order_by(func.avg(Review.rating).desc())\
    .limit(10)\
    .all()

    random_products = db.session.query(Product)\
    .options(db.joinedload(Product.images))\
    .filter(Product.is_active == True)\
    .order_by(func.random())\
    .limit(10)\
    .all()

    return render_template('home.html',title="home", cart=cart, new_arrivals=new_arrivals, clothes=clothes, shoes=shoes,accessories=accessories, top_rated_products=top_rated_products,random_products=random_products)




# Generate a random 6-digit code for 2FA
def generate_2fa_code():
    return ''.join(random.choices(string.digits, k=6))

def send_2fa_email(user_email, code):
    msg = Message('Your 2FA Code', recipients=[user_email])
    msg.body = f'Your 2FA verification code is: {code}'
    mail.send(msg)



@app.route("/verify_2fa", methods=['GET', 'POST'])
def verify_2fa():
    if 'email' not in session or '2fa_code' not in session:
        flash('Unauthorized access to 2FA verification.', 'warning')
        return redirect(url_for('login'))

    # ✅ Check expiration
    expires = session.get('2fa_expires')
    if expires and datetime.utcnow() > datetime.fromisoformat(expires):
        session.clear()
        flash('2FA code has expired. Please register again.', 'danger')
        return redirect(url_for('register'))

    form = TwoFactorForm()

    if form.validate_on_submit():
        code = form.code.data

        if code == session.get('2fa_code'):
            user = Users.query.filter_by(email=session.get('email')).first()

            if user:
                user.email_verified = True  #  Just mark email/2FA as verified

                db.session.commit()
                login_user(user)

                # ✅ Clear session
                session.pop('2fa_code', None)
                session.pop('email', None)
                session.pop('2fa_expires', None)

                flash('Email verified! Your account is pending Admin approval.', 'success')
                return redirect(url_for('home'))
            else:
                flash('User not found.', 'danger')
        else:
            flash('Invalid 2FA code. Please try again.', 'danger')

    return render_template('verify_2fa.html', form=form)






@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        existing_user = Users.query.filter_by(email=form.email.data).first()

        # ✅ Check if email exists and isn't verified
        if existing_user:
            if not existing_user.email_verified:
                db.session.delete(existing_user)  # Remove unverified user
                db.session.commit()
            else:
                flash('This email is already registered and verified.', 'danger')
                return redirect(url_for('login'))

        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Read the uploaded ID picture as binary, or fallback to a default image
        if form.picture_id.data:
            id_picture_data = form.picture_id.data.read()
        else:
            with open('static/img/default.jpg', 'rb') as f:
                id_picture_data = f.read()

        # Create the new user
        user = Users(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=hashed_pass,
            date_of_birth=form.date_of_birth.data,
            gender=form.gender.data,
            id_picture=id_picture_data,
            email_verified=False  # Make sure to set this if not default
        )

        db.session.add(user)
        db.session.commit()

        # ✅ Set up 2FA session data
        two_fa_code = generate_2fa_code()
        session['2fa_code'] = two_fa_code
        session['email'] = user.email
        session['2fa_expires'] = (datetime.utcnow() + timedelta(minutes=10)).isoformat()

        send_2fa_email(user.email, two_fa_code)

        flash('Your account has been created! Please verify your email with the 2FA code.', 'success')
        return redirect(url_for('verify_2fa'))

    return render_template('register.html', title="Register", form=form)








def send_shop_info_email(user):
    token = s.dumps(user.email, salt='shop-info-salt')
    shop_info_url = url_for('shop_info', token=token, _external=True)

    msg = Message('Complete Your Seller Registration',
                  recipients=[user.email])
    msg.body = f'''Thank you for registering as a seller!

To complete your seller registration, please click the link below to fill in your shop information:
{shop_info_url}

If you did not request this registration, please ignore this email.
'''
    mail.send(msg)


@app.route("/register/seller", methods=['GET', 'POST'])
def register_seller():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationFormSeller()

    if form.validate_on_submit():
        # Hash the password from the form
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Read the uploaded ID picture as binary
        id_picture_data = form.picture_id.data.read() if form.picture_id.data else None

        # Create a new seller user with all provided information
        new_seller = Users(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=hashed_pass,
            id_picture=id_picture_data,  # Save the binary data of the ID picture
            date_of_birth=form.date_of_birth.data,  # Include date of birth
            gender=form.gender.data,  # Include gender
            role='seller'  # Set the user role as 'seller'
        )

        # Save the new seller to the database
        db.session.add(new_seller)
        db.session.commit()

        # Send a shop info email to the new seller
        send_shop_info_email(new_seller)

        flash('A confirmation email has been sent to complete your seller registration.', 'info')
        return redirect(url_for('login'))

    return render_template('register_seller.html', title="Register as Seller", form=form)



@app.route('/register/seller/shop/<token>', methods=['GET', 'POST'])
def shop_info(token):
    try:
        # Decode the token to extract the email
        email = s.loads(token, salt='shop-info-salt', max_age=3600)  # Token expires after 2 hours
    except:
        flash('The link is invalid or has expired.', 'warning')
        return redirect(url_for('login'))

    seller = Users.query.filter_by(email=email).first_or_404()

    # Ensure the user is a seller
    if seller.role != 'seller':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('login'))

    # Initialize the shop information form
    form = ShopInformationForm()
    regions, provinces, cities, barangays = load_json_data()  # Load JSON data for regions, provinces, etc.

    # Populate region choices
    form.region.choices = [(region['region_code'], region['region_name']) for region in regions]
    
    # Populate province choices if region is selected
    if form.region.data:
        selected_region_id = form.region.data
        form.province.choices = [(province['province_code'], province['province_name']) for province in provinces if province['region_code'] == selected_region_id]

    # Populate city choices if province is selected
    if form.province.data:
        selected_province_id = form.province.data
        form.city.choices = [(city['city_code'], city['city_name']) for city in cities if city['province_code'] == selected_province_id]

    # Populate barangay choices if city is selected
    if form.city.data:
        selected_city_id = form.city.data
        form.barangay.choices = [(barangay['brgy_code'], barangay['brgy_name']) for barangay in barangays if barangay['city_code'] == selected_city_id]

    if form.validate_on_submit():
        # Save the shop information for the seller


        region_name = next((r['region_name'] for r in regions if r['region_code'] == form.region.data), None)
        province_name = next((p['province_name'] for p in provinces if p['province_code'] == form.province.data), None)
        city_name = next((c['city_name'] for c in cities if c['city_code'] == form.city.data), None)
        barangay_name = next((b['brgy_name'] for b in barangays if b['brgy_code'] == form.barangay.data), None)

        new_shop = Seller(
            user_id=seller.id,
            shop_name=form.shop_name.data,
            category=','.join(form.category.data),
            region=region_name,
            province=province_name,
            city=city_name,
            barangay=barangay_name,
            street=form.street.data,
            postal_code=form.postal_code.data,
            business_id=form.business_id.data.read(),  
            policy_accepted=form.policy.data
        )

        # Add the new shop to the database
        db.session.add(new_shop)
        db.session.commit()

        flash('Information Saved, Please Wait for Admin Approval!', 'success')
        return redirect(url_for('login'))

    else:
        print("Form is NOT valid.")
        print(form.errors)  

    return render_template('shop_info.html', form=form,
                           regions=regions, 
                           provinces=provinces, 
                           cities=cities, 
                           barangays=barangays)



def log_attempt(user, email, success):
    attempt = LoginAttempt(
        email=email,
        ip_address=request.remote_addr,
        success=success,
        user_id=user.id if user else None
    )
    db.session.add(attempt)
    db.session.commit()

BLOCK_DURATION_SECONDS = 10 
MAX_FAILED_ATTEMPTS = 3

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    block_until = None

    # Check if user is currently blocked
    if 'block_until' in session:
        block_until = datetime.strptime(session['block_until'], '%Y-%m-%d %H:%M:%S')
        if datetime.utcnow() < block_until:
            # User is still blocked, show block message and countdown
            return render_template('signin.html', form=form, blocked_until=block_until)
        else:
            # Block expired, reset block info and failed attempts
            session.pop('block_until')
            session.pop('failed_attempts', None)
            block_until = None

    # Initialize failed attempts counter if missing
    if 'failed_attempts' not in session:
        session['failed_attempts'] = 0

    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if user.is_banned:
                flash('Your account has been banned. Please contact support.', 'danger')
                return redirect(url_for('login'))

            if not user.is_validated:
                flash('Account not validated. Please contact admin.', 'warning')
                return redirect(url_for('login'))

            # Successful login: reset failed attempts and log user in
            session.pop('failed_attempts', None)
            login_user(user, remember=form.remember.data)

            # Redirect based on role or next page param
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.role == 'admin':
                return redirect(url_for('admin'))
            elif user.role == 'seller':
                return redirect(url_for('seller'))
            elif user.role == 'courier':
                return redirect(url_for('courier'))
            else:
                return redirect(url_for('home'))

        else:
            # Failed login attempt
            session['failed_attempts'] += 1

            if session['failed_attempts'] >= MAX_FAILED_ATTEMPTS:
                block_time = datetime.utcnow() + timedelta(seconds=BLOCK_DURATION_SECONDS)
                session['block_until'] = block_time.strftime('%Y-%m-%d %H:%M:%S')
                flash(f'Too many failed attempts. Please try again in {BLOCK_DURATION_SECONDS} seconds.', 'danger')
                return render_template('signin.html', form=form, blocked_until=block_time)

            flash('Login unsuccessful. Please check email and password.', 'danger')

    # Set no-cache headers in the response
    response = make_response(render_template('signin.html', form=form, blocked_until=block_until))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

    



# from flask import request



@app.route("/shop")
def shop():
    page = request.args.get("page", 1, type=int)
    per_page = 16
    search_query = request.args.get("q", "")
    categories = request.args.getlist("category")  # Get categories as a list
    sizes = request.args.getlist("size")

    # Base query for active products
    products_query = Product.query.filter_by(is_active=True)

    # Apply category filter if there are selected categories
    if categories:
        category_filters = []
        for category in categories:
            if "&" in category:
                keywords = [word.strip() for word in category.split("&")]
                category_filters.extend(
                    [Product.category.ilike(f"%{keyword}%") for keyword in keywords]
                )
            else:
                category_filters.append(Product.category.ilike(f"%{category}%"))
        
        # Combine all category filters with OR logic
        products_query = products_query.filter(or_(*category_filters))

    # Apply size filter if there are selected sizes
    if sizes:
        # Subquery to fetch product IDs that match the selected sizes
        size_subquery = db.session.query(ProductVariation.product_id).filter(
            ProductVariation.size.in_(sizes)
        ).distinct()

        # Filter products based on the size subquery
        products_query = products_query.filter(Product.id.in_(size_subquery))

    # Apply search filter if a search term is provided
    if search_query:
        products_query = products_query.filter(Product.name.ilike(f"%{search_query}%"))

    # Get the total count of filtered products (after applying filters)
    total_filtered_products = products_query.count()

    # Calculate total pages based on filtered products and per_page
    total_pages = (total_filtered_products // per_page) + (1 if total_filtered_products % per_page else 0)

    # Ensure the requested page is within bounds, otherwise fallback to the last page or 1
    if page > total_pages:
        page = total_pages if total_pages > 0 else 1

    # Paginate the results
    pagination = products_query.paginate(page=page, per_page=per_page)
    products = pagination.items

    print(f"Total Filtered Products: {total_filtered_products}")
    print(f"Pagination Total: {pagination.total}")
    print(f"Items on Page: {len(products)}")
    print(f"Page Number: {page}")
    print(f"Items Per Page: {per_page}")

    # Continue with the rest of the logic for reviews, category counts, etc.
    product_reviews = {}
    product_avg_ratings = {}
    for product in products:
        reviews = Review.query.filter_by(product_id=product.id).all()
        product_reviews[product.id] = reviews

        if reviews:
            total_rating = sum([review.rating for review in reviews])
            average_rating = total_rating / len(reviews)
            product_avg_ratings[product.id] = round(average_rating, 1)
        else:
            product_avg_ratings[product.id] = 0

    # Calculate category counts
    category_counts = {}
    all_active_products = Product.query.filter_by(is_active=True).all()
    for product in all_active_products:
        cat = product.category
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # Count the sizes for filtering purposes
    size_counts = {}
    for variation in ProductVariation.query.all():
        size_counts[variation.size] = size_counts.get(variation.size, 0) + 1

    # Prepare query params for pagination links
    query_params = {
        "q": search_query,
        "category": categories,
        "size": sizes,
    }
    query_params = {key: value for key, value in query_params.items() if value}

    # Render the template
    return render_template(
        "shop.html",
        title="Shop",
        products=products,
        pagination=pagination,
        category_counts=category_counts,
        total_products=total_filtered_products,
        search_query=search_query,
        selected_categories=categories,
        product_reviews=product_reviews,
        product_avg_ratings=product_avg_ratings,
        selected_sizes=sizes,
        size_counts=size_counts,
        query_params=query_params  # Pass the query parameters for pagination
    )








@app.route("/logout")
@login_required
def logout():
    # print("🔒 Logout route was triggered!")

    logout_user()           # Log out from Flask-Login
    session.clear()         # Clear session
    session.modified = True

    # Create a response and remove 'remember_token' cookie
    response = make_response(redirect(url_for('login')))
    response.set_cookie('remember_token', '', expires=0)
    return response


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics',picture_fn)


    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    

    return picture_fn





@app.route("/account")
@app.route("/account/profile",methods=['GET','POST'])
@role_required('user')
@login_required
def account_profile():

    # BEST FOR 1 CHECK EVERY SESSION
    if not session.get('auto_confirm_checked'):  
        auto_confirm_order_received()
        session['auto_confirm_checked'] = True

    # DEBUGG
    # auto_confirm_order_received()
    form = UpdateAccountForm()

    if form.validate_on_submit():

        if form.picture.data:
            old_pic = current_user.image_file
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            if old_pic != 'default.jpg':
                os.remove(os.path.join(app.root_path, 'static/profile_pics', old_pic))


        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.gender = form.gender.data
        current_user.date_of_birth = form.date_of_birth.data


        db.session.commit()
        flash('You account has been updated','success')
        return redirect(url_for('account_profile'))
    
    
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.gender.data = current_user.gender if current_user.gender else 'male' 
        form.date_of_birth.data = current_user.date_of_birth if current_user.date_of_birth else datetime.today().date() 


    image_file = url_for('static',filename='profile_pics/' + current_user.image_file)
    return render_template('account_profile.html',title="Account", image_file=image_file, form=form)







@app.route("/account/address", methods=['GET', 'POST'])
@login_required
def account_address():
    form = AddAddress()
    regions, provinces, cities, barangays = load_json_data()  # Load JSON data for regions, provinces, cities, barangays

    # Populate region choices
    form.region.choices = [(region['region_code'], region['region_name']) for region in regions]

    # Filter addresses by the current user ID
    user_addresses = UserAddress.query.filter_by(user_id=current_user.id).order_by(UserAddress.user_id.desc()).all()

    if form.validate_on_submit():
        # Fetch the corresponding names using the selected IDs
        region_text = next((region['region_name'] for region in regions if region['region_code'] == form.region.data), None)
        province_text = next((province['province_name'] for province in provinces if province['province_code'] == form.province.data), None)
        city_text = next((city['city_name'] for city in cities if city['city_code'] == form.city.data), None)
        barangay_text = next((barangay['brgy_name'] for barangay in barangays if barangay['brgy_code'] == form.barangay.data), None)

        new_address = UserAddress(
            user_id=current_user.id,
            address_name=form.address_name.data,
            street=form.street.data,
            barangay=barangay_text,
            city=city_text,
            province=province_text,
            region=region_text,
            postal_code=form.postal_code.data,
            telephone_no=form.telephone_no.data
        )

        db.session.add(new_address)
        db.session.commit()

        flash('Address added successfully', 'success')
        return redirect(url_for('account_address'))

    return render_template('account_address.html', title="Account", address_form=form, regions=regions, posts=user_addresses)



@app.route("/account/address/<int:id>/delete", methods=['POST'])
@login_required
def delete_address(id):
    address = UserAddress.query.get_or_404(id)

    if address.user_id != current_user.id:
        abort(403)

    # Check if the address is linked to any orders
    linked_orders = Order.query.filter_by(address_id=address.id).count()
    if linked_orders > 0:
        flash('This address is linked to existing orders and cannot be deleted.', 'danger')
        return redirect(url_for('account_address'))

    db.session.delete(address)
    db.session.commit()

    flash('Your address has been deleted!', 'success')
    return redirect(url_for('account_address'))



@app.route('/account/address/set-default/<int:address_id>', methods=['POST'])
@login_required
def set_default_address(address_id):
    # Fetch the address to be set as default and ensure it belongs to the current user
    address_to_set = UserAddress.query.filter_by(id=address_id, user_id=current_user.id).first()

    if address_to_set:
        # Set all other addresses of the user to False
        UserAddress.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})
        
        # Set the selected address to True
        address_to_set.is_default = True
        db.session.commit()

        flash('Address set as default successfully.', 'success')
    else:
        flash('Address not found or unauthorized action.', 'error')

    return redirect(url_for('account_address'))





@app.route("/edit_address/<int:address_id>", methods=['GET', 'POST'])
@login_required
def edit_address(address_id):
    # Fetch the address from the database
    address = UserAddress.query.get_or_404(address_id)

    # Ensure the current user owns the address
    if address.user_id != current_user.id:
        flash("You don't have permission to edit this address.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Update the address fields with the form data
        address.address_name = request.form['address_name']
        address.street = request.form['street']
        address.barangay = request.form['barangay']
        address.city = request.form['city']
        address.province = request.form['province']
        address.region = request.form['region']
        address.postal_code = request.form['postal_code']
        address.telephone_no = request.form.get('telephone_no')

        # Commit the changes to the database
        db.session.commit()
        flash("Address updated successfully!", "success")
        return redirect(url_for('account_address'))  # Redirect back to the home page

    return render_template('edit_address.html', address=address)



@app.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    variations = ProductVariation.query.filter_by(product_id=product_id).all()
    reviews = Review.query.filter_by(product_id=product_id).all()


    # Extract unique colors and sizes based on the variations
    unique_colors = set(variation.color for variation in variations)
    
    # Create a dictionary to map colors to their respective sizes
    color_to_sizes = {}
    for variation in variations:
        if variation.color not in color_to_sizes:
            color_to_sizes[variation.color] = set()
        color_to_sizes[variation.color].add(variation.size)

    # Convert the sets to lists for easier template rendering
    color_to_sizes = {color: list(sizes) for color, sizes in color_to_sizes.items()}

      # Get previous and next products
    prev_product = Product.query.filter(Product.id < product_id).order_by(Product.id.desc()).first()
    next_product = Product.query.filter(Product.id > product_id).order_by(Product.id).first()

    return render_template('products.html', title="Product", product=product, variations=variations, unique_colors=unique_colors, color_to_sizes=color_to_sizes, prev_product=prev_product, next_product=next_product, reviews=reviews)





# Route for the "Forgot Password" page
@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html', form=form)



# Route to reset password with the token
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  # Token expires after 1 hour
    except:
        flash('That token is invalid or has expired.', 'warning')
        return redirect(url_for('login'))

    user = Users.query.filter_by(email=email).first_or_404()
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', form=form)

# Function to send the reset email
def send_reset_email(user):
    token = s.dumps(user.email, salt='password-reset-salt')
    reset_url = url_for('reset_password', token=token, _external=True)
    
    msg = Message('Password Reset Request',
                  sender='noreply@example.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, please ignore this email.
'''
    mail.send(msg)





@app.route("/admin")
@login_required
@role_required('admin') 
def admin():

    if not session.get('auto_confirm_checked'):  
        auto_confirm_order_received()
        session['auto_confirm_checked'] = True

    # auto_confirm_order_received()
    total_users = Users.query.filter_by(role='user').count()

    total_sellers = Seller.query.count()
    total_couriers = Courier.query.count()
    total_products = Product.query.count()

    total_admin_income = db.session.query(db.func.sum(Admin.total_admin_income)).scalar() or 0.0
    total_shipping_income = db.session.query(db.func.sum(Admin.total_shipping_income)).scalar() or 0.0

    admin_commissions = (
    db.session.query(
        Order.id.label('order_id'),  # Include the order ID
        func.sum(OrderItem.price * OrderItem.quantity).label('total_amount'),  # Calculate total order amount
        (func.sum(OrderItem.price * OrderItem.quantity) * 0.05).label('admin_commission')  # Calculate 5% commission
    )
    .join(OrderItem, OrderItem.order_id == Order.id)
    .filter(OrderItem.status == 'Received')  # Filter based on the status of the OrderItem
    .group_by(Order.id)
    .order_by(desc(Order.id))  # Order by Order.id in descending order (latest orders first)
    .limit(5)  # Limit the results to the latest 5 orders
    .all()
    )


    # Pass data to the template
    admin_stats = {
        "total_users": total_users,
        "total_sellers": total_sellers,
        "total_couriers": total_couriers,
        "total_products": total_products,
        "total_admin_income": total_admin_income,
        "total_shipping_income": total_shipping_income
    }

    return render_template('admin.html', title="Admin", admin_stats=admin_stats,admin_commissions=admin_commissions)



@app.route("/seller")
@login_required
@role_required('seller') 
def seller():

    if not session.get('auto_confirm_checked'):  # Run only if not already checked
        auto_confirm_order_received()
        session['auto_confirm_checked'] = True

    # auto_confirm_order_received()
    
    seller_id = current_user.seller.id

    # Query the number of products, orders, etc.
    total_products = Product.query.filter_by(seller_id=seller_id).count()
    pending_orders = OrderItem.query.filter_by(seller_id=seller_id, status='Pending').count()
    shipments = OrderItem.query.filter_by(seller_id=seller_id, status='Order Placed').count()
    in_transit = OrderItem.query.filter_by(seller_id=seller_id, status='In Transit').count()
    delivered_orders = OrderItem.query.filter_by(seller_id=seller_id, status='Delivered').count()

    completed_orders = OrderItem.query.filter_by(seller_id=seller_id, status='Received').count()
    total_orders = OrderItem.query.filter(
    OrderItem.seller_id == seller_id,
    OrderItem.status.notin_(['Cancelled', 'Received'])  # Exclude 'Cancelled' and 'Received' statuses
        ).distinct('order_id').count()


    seller = current_user.seller
    total_income = seller.total_income if seller.total_income else 0.0
    
    category_sales = (
    db.session.query(Product.category, func.count(OrderItem.id).label('sales_count'))
    .join(OrderItem, OrderItem.product_id == Product.id)  # Join Product with OrderItem
    .filter(OrderItem.seller_id == seller_id)  # Use OrderItem's seller_id for filtering
    .group_by(Product.category)  # Group by Product category
    .all()
        )



    categories = [
        {"category": category, "sales_count": sales_count}
        for category, sales_count in category_sales
    ]

    user_transactions = (
    db.session.query(Order, func.sum(OrderItem.price * OrderItem.quantity).label('total_amount'))
    .join(OrderItem, OrderItem.order_id == Order.id)
    .filter(OrderItem.seller_id == seller_id)  # Check if the user is the seller
    .filter(OrderItem.status == 'Received')  # Filter based on the status of the OrderItem
    .group_by(Order.id)
    .all()
    )

    # Check if any transactions are returned
    # if user_transactions:
    #     print("Transactions found:", user_transactions)
    # else:
    #     print("No transactions found.")


    


    # Pass data to the template
    seller_stats = {
        "total_products": total_products,
        "pending_orders": pending_orders,
        "shipments": shipments,
        "in_transit": in_transit,
        "completed_orders": completed_orders,
        "total_income": total_income,
        "total_orders": total_orders, 
        "delivered_orders":delivered_orders
    }

    return render_template('seller_dashboard.html',title="Seller", seller_stats=seller_stats, categories=categories, transactions=user_transactions)


@app.route("/admin/accounts/pending/account")
@login_required
@role_required('admin') 
def pending_account():

    all_users = Users.query.filter_by(role='user', is_validated=False).all()  # Filter by role and validation status
    pending_seller = Users.query.filter_by(role='seller', is_validated=False).all()  # Filter by role and validation status

    archived_users = Users.query.filter_by(role='user',is_disapproved=True).all()
    archived_seller = Users.query.filter_by(role='seller',is_disapproved=True).all()


    # Convert BLOB image data to Base64-encoded strings
    for user in all_users + archived_users + pending_seller + archived_seller:
        if user.id_picture:
            user.image_data = base64.b64encode(user.id_picture).decode('utf-8')
        else:
            user.image_data = None  # For users without an image

    for seller_user in pending_seller:
        seller = Seller.query.filter_by(user_id=seller_user.id).first()
        if seller:
            seller_user.shop_info = seller  # Attach the shop info to the user
            # Encode the business ID image
            if seller.business_id:
                seller.business_id_encoded = base64.b64encode(seller.business_id).decode('utf-8')

    # Process archived sellers to attach shop information and encode business ID
    for seller_user in archived_seller:
        seller = Seller.query.filter_by(user_id=seller_user.id).first()
        if seller:
            seller_user.shop_info = seller  # Attach the shop info to the user
            # Encode the business ID image
            if seller.business_id:
                seller.business_id_encoded = base64.b64encode(seller.business_id).decode('utf-8')

    return render_template('pending_account.html', users=all_users,pending_seller=pending_seller ,archived_users=archived_users,archived_seller=archived_seller ,title="Pending Acc")

@app.route('/approve_user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    user = Users.query.get_or_404(user_id)
    user.is_validated = True
    db.session.commit()

    msg = Message('Account Approval Confirmation', recipients=[user.email])
    msg.body = f"""
    Dear {user.first_name},

    Congratulations! Your account has been successfully approved. You can now log in to your account and start enjoying all the features we offer.

    We are excited to have you as part of our community and look forward to supporting your journey. If you have any questions or need assistance, feel free to reach out to our support team.

    Thank you for choosing us!

    Best regards,
    The SheWear Team
    """
    
    mail.send(msg)

    flash('The account has been approved!', 'success')
    return redirect(url_for('pending_account'))



@app.route("/admin/accounts/user")
@login_required
@role_required('admin')
def manage_user():
    all_users = Users.query.filter(
    Users.role == 'user',
    Users.is_validated == True,
    (Users.is_banned == False) | (Users.is_banned == None)  # Include NULL values for is_banned
    ).order_by(Users.last_name).all()

    # Query sellers and include user data in each seller object
    all_seller = (
        db.session.query(Seller, Users)
        .join(Users, Seller.user_id == Users.id)
        .filter(
            Users.role == 'seller',
            Users.is_validated == True,
            (Users.is_banned == False) | (Users.is_banned == None)  # Include NULL values for is_banned
        )
        .order_by(Users.last_name)
        .all()
    )

    ban_seller = (
        db.session.query(Seller, Users)
        .join(Users, Seller.user_id == Users.id)
        .filter(Users.role == 'seller', Users.is_validated == True,Users.is_banned == True)
        .order_by(Users.last_name)
        .all()
    )

    banned_users = (
    db.session.query(Users)
    .filter(
        Users.role == 'user',
        Users.is_validated == True,
        Users.is_banned == True
    )
    .order_by(Users.last_name)
    .all()
    )

    # Convert BLOB image data to Base64-encoded strings for users
    for user in all_users:
        if isinstance(user.image_file, bytes):  # Ensure the image is in bytes format
            user.image_data = base64.b64encode(user.image_file).decode('utf-8')
        else:
            user.image_data = None  # Default value for users without an image

    # Convert image data for sellers
    for seller, user in all_seller:
        if isinstance(user.image_file, bytes):
            user.image_data = base64.b64encode(user.image_file).decode('utf-8')
        else:
            user.image_data = None

    return render_template(
        'manage_user.html', 
        title="User Accounts", 
        users=all_users, 
        sellers=all_seller,
        banned_users=banned_users,
        ban_seller=ban_seller  # Pass the seller-user pairs to the template
    )




@app.route("/admin/accounts/info", methods=['GET', 'POST'])
@login_required
@role_required('admin')
def admin_account():
    user_id = current_user.id  
    user = Users.query.get(user_id)

    # Initialize the form
    form = UpdateAdminProfileForm()

    if request.method == 'POST':
        # Validate the form input
        if form.validate_on_submit():
            # Update user details
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            
            # Handle the image file if the user uploads one
            if form.image_file.data:
                image_filename = save_picture(form.image_file.data)
                user.image_file = image_filename  # Update the user's image_file

            # Commit changes to the database
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('admin_account'))


    if request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
   

    # Create a URL for the user's image
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    
    # Render the template with the user data, image URL, and the form
    return render_template('admin_account.html', title="Account", user=user, image_file=image_file, form=form)





@app.route("/seller/accounts/info", methods=['GET', 'POST'])
@login_required
@role_required('seller')
def seller_account():
    user_id = current_user.id  
    user = Users.query.get(user_id)

    # Initialize the form
    form = UpdateSellerProfileForm()

    if request.method == 'POST':
        # Validate the form input
        if form.validate_on_submit():
            # Update user details
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            user.gender = form.gender.data

            user.date_of_birth = form.date_of_birth.data

            
            # Handle the image file if the user uploads one
            if form.image_file.data:
                image_filename = save_picture(form.image_file.data)
                user.image_file = image_filename  # Update the user's image_file

            # Commit changes to the database
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('seller_account'))


    if request.method == 'GET':
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
        form.gender.data = user.gender
        form.date_of_birth.data = user.date_of_birth
   

    # Create a URL for the user's image
    image_file = url_for('static', filename='profile_pics/' + user.image_file)
    
    # Render the template with the user data, image URL, and the form
    return render_template('seller_account.html', title="Account", user=user, image_file=image_file, form=form)
 
  
@app.route("/seller/accounts/shop", methods=['GET', 'POST'])
@login_required
@role_required('seller')
def seller_shopinfo():
    # Get the current seller's ID
    user_id = current_user.id  
    seller = Seller.query.filter_by(user_id=user_id).first()  # Get the seller's data

    # Initialize the form
    form = UpdateShopInformationForm()

    if request.method == 'POST':
        # Validate the form input
        if form.validate_on_submit():
            # Update seller details with form data
            seller.shop_name = form.shop_name.data
            seller.category = ','.join(form.category.data)
            seller.street = form.street.data
            seller.barangay = form.barangay.data
            seller.city = form.city.data
            seller.province = form.province.data
            seller.region = form.region.data
            seller.postal_code = form.postal_code.data

            # Handle the image file if the user uploads one
            if form.image_file.data:
                image_filename = save_picture(form.image_file.data)  # Implement save_picture function as needed
                seller.image_file = image_filename  # Update the seller's image_file

            # Commit changes to the database
            db.session.commit()
            flash('Your shop information has been updated!', 'success')
            return redirect(url_for('seller_shopinfo'))  # Redirect to the same route

    if request.method == 'GET':
        # Populate the form with existing seller data
        form.shop_name.data = seller.shop_name
        form.category.data = seller.category.split(',')
        form.street.data = seller.street
        form.barangay.data = seller.barangay
        form.city.data = seller.city
        form.province.data = seller.province
        form.region.data = seller.region
        form.postal_code.data = seller.postal_code

    # Create a URL for the seller's image
    image_file = url_for('static', filename='profile_pics/' + seller.image_file) if seller.image_file else url_for('static', filename='profile_pics/default.jpg')
    
    # Render the template with the seller data, image URL, and the form
    return render_template('seller_shopInfo.html', title="Shop Info", seller=seller, image_file=image_file, form=form)




@app.route('/disapprove_user', methods=['POST'])
def disapprove_user():
    user_id = request.form.get('user_id')
    disapprove_reason = request.form.get('disapprove_reason')

    if user_id:
        # Fetch the user from the database
        print(f"User ID: {user_id}")
        print(f"Disapproval Reason: {disapprove_reason}")
        user = Users.query.get(user_id)
        if user:
            # Update the user's disapproval status and reason
            user.is_disapproved = True
            user.is_validated = True
            user.disapproval_reason = disapprove_reason  # Save the reason
            db.session.commit()  # Commit the changes

            # Send a disapproval email with the reason
            msg = Message('Account Disapproval Notification',
                          recipients=[user.email])
            msg.body = f"""
            Hi {user.first_name},

            We regret to inform you that your account has been disapproved for the following reason:

            "{disapprove_reason}"

            If you have any questions, feel free to reach out to our support team.

            Best regards,
            SheWear Support Team
            """
            mail.send(msg)

            flash('User account disapproved successfully, and email notification sent.', 'success')
        else:
            flash('User not found.', 'danger')
    else:
        flash('User ID not found.', 'danger')

    return redirect(url_for('pending_account'))  # Redirect to the appropriate view





@app.route('/return_user', methods=['POST'])
def return_user():
    user_id = request.form.get('user_id')

    if user_id:

        user = Users.query.get(user_id)
        if user:
            user.is_disapproved = False  
            user.is_validated = False
            user.disapproval_reason = None 

            db.session.commit()  
            flash('User account returned to the Pending section successfully.', 'success')
        else:
            flash('User not found.', 'danger')
    else:
        flash('User ID not found.', 'danger')

    return redirect(url_for('pending_account'))  # Redirect to the appropriate view



@app.route("/seller/product", methods=['GET', 'POST'])
@login_required
@role_required('seller')
def seller_product():
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    inactive_page = request.args.get('inactive_page', 1, type=int)
    search_query = request.args.get('search', '')  # Search query
    per_page = 5  # Number of products per page

    # Get the seller
    seller = Seller.query.filter_by(user_id=current_user.id).first()

    # Active products query
    active_query = Product.query.filter_by(seller_id=seller.id, is_active=True)
    if search_query:
        active_query = active_query.filter(Product.name.ilike(f'%{search_query}%'))

    # Inactive products query
    inactive_query = Product.query.filter_by(seller_id=seller.id, is_active=False)
    if search_query:
        inactive_query = inactive_query.filter(Product.name.ilike(f'%{search_query}%'))

    # Paginate the queries
    products = active_query.paginate(page=page, per_page=per_page)
    inactive_products = inactive_query.paginate(page=inactive_page, per_page=per_page)

    return render_template(
        'seller_product.html',
        title="Account",
        products=products,
        inactive_products=inactive_products,
        search_query=search_query  # Pass the search term to the template
    )




@app.route('/unpublish_product', methods=['POST'])
@login_required
@role_required('seller')
def unpublish_product():
    product_id = request.form.get('product_id')  # Get product ID from the form data
    if product_id:
        product = Product.query.get(product_id)
        if product:
            product.is_active = False  # Set the product to inactive or unpublished
            db.session.commit()
            flash('Product unpublished successfully.', 'success')
        else:
            flash('Product not found.', 'danger')
    else:
        flash('No product ID provided.', 'danger')
    
    return redirect(url_for('seller_product'))  # Redirect back to the seller products page



@app.route('/unpublish_product/admin', methods=['POST'])
@login_required
def unpublish_product_admin():
    try:
        product_id = int(request.form.get('product_id', 0))
    except ValueError:
        flash('Invalid product ID.', 'danger')
        return redirect(url_for('admin_products'))

    if product_id <= 0:
        flash('No valid product ID provided.', 'danger')
        return redirect(url_for('admin_products'))

    product = Product.query.filter_by(id=product_id).first()
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin_products'))

    product.is_active = False  # Set the product to inactive or unpublished
    db.session.commit()
    flash('Product unpublished successfully.', 'success')
    return redirect(url_for('admin_products'))




@app.route('/publish_product', methods=['POST'])
@login_required
@role_required('seller')
def publish_product():
    product_id = request.form.get('product_id')  # Get product ID from the form
    if product_id:
        product = Product.query.get(product_id)
        if product:
            product.is_active = True  # Set the product to active or published
            db.session.commit()
            flash('Product published successfully.', 'success')
        else:
            flash('Product not found.', 'danger')
    else:
        flash('No product ID provided.', 'danger')
    
    return redirect(url_for('seller_product'))  # Redirect back to the seller products page


# @app.route("/product/add", methods=['GET', 'POST'])
# @login_required
# def add_product():
#     form = ProductForm()  

#     if form.validate_on_submit():

#         flash('Product added successfully!', 'success')
#         return redirect(url_for('add_product')) 
#     return render_template('add_product.html', form=form, title='Add Product')



@app.route('/add_product', methods=['GET', 'POST'])
@login_required
@role_required('seller')  # Assuming you only want sellers to access this route
def add_product():
    form = ProductForm()  # Create an instance of your form

    if request.method == 'POST':
        # Extract product information from the form
        product_name = request.form.get('product_name')
        category = request.form.get('category')
        brand = request.form.get('brand')
        material = request.form.get('material')
        description = request.form.get('description')

        # Get the seller for the current user
        seller = Seller.query.filter_by(user_id=current_user.id).first()

        # Ensure the seller exists before proceeding
        if not seller:
            flash("You must be a registered seller to add products.", "warning")
            return redirect(url_for('seller_dashboard'))

        # Create and insert a new Product record
        new_product = Product(
            name=product_name,
            category=category,
            brand=brand,
            material=material,
            description=description,
            seller_id=seller.id  # Use the seller's ID, not the user's ID
        )
        db.session.add(new_product)
        db.session.commit()

        # Handle images
        images = request.files.getlist('product_images')  # Use the field name defined in the form
        upload_folder = os.path.join(app.root_path, 'static/profile_pics')

        for image in images:
            if image:
                image_filename = secure_filename(image.filename)
                unique_filename = f"{uuid.uuid4()}_{image_filename}"
                image_path = os.path.join(upload_folder, unique_filename)
                image.save(image_path)

                new_image = ProductImage(
                    product_id=new_product.id,
                    image_path=unique_filename  # Store just the unique filename
                )
                db.session.add(new_image)

        # Handle variations
        variations_data = request.form.get('variations_data')
        if variations_data:
            variations = json.loads(variations_data)
            for variation in variations:
                color = variation['color']
                sizes = variation['sizes']

                for size_info in sizes:
                    size = size_info['size']
                    stock = size_info['stock']
                    price = size_info['price']

                    new_variation = ProductVariation(
                        product_id=new_product.id,
                        color=color,
                        size=size,
                        stock=stock,
                        price=price
                    )
                    db.session.add(new_variation)

        db.session.commit()
        flash('Product and variations added successfully!', 'success')
        return redirect(url_for('seller_product'))

    return render_template('add_product.html', form=form, title='Add Product')







@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)  # Fetch the product by ID
    form = ProductForm()  # Your edit product form class

    if form.validate_on_submit():
        # Update the product details with the form data
        product.name = form.product_name.data
        product.category = form.category.data
        product.brand = form.brand.data
        product.material = form.material.data
        product.description = form.description.data
        
        # Get variations data from the hidden input
        variations_data = request.form.get('variations_data')
        print("Parsed Variations Data:", variations_data)  # This will show the variations data specifically

        if variations_data:
            variations = json.loads(variations_data)  # Parse the JSON string into a Python object
            print("Variations after parsing:", variations)
            existing_variations = {f'{v.color}_{v.size}': v for v in product.variations}

            # Update or add new variations
            for variation in variations:
                color = variation['color']
                size = variation['size']
                stock = variation['stock']
                price = variation['price']
                variation_key = f'{color}_{size}'

                print(f"Processing Variation - Color: {color}, Size: {size}, Stock: {stock}, Price: {price}")


                if variation_key in existing_variations:
                    # Update existing variation
                    existing_variation = existing_variations[variation_key]
                    existing_variation.stock = stock
                    existing_variation.price = price
                    del existing_variations[variation_key]  # Keep track of what was updated
                else:
                    # Create a new variation
                    new_variation = ProductVariation(
                        product_id=product.id,
                        color=color,
                        size=size,
                        stock=stock,
                        price=price
                    )
                    print(f"Adding New Variation - Color: {color}, Size: {size}, Stock: {stock}, Price: {price}")

                    db.session.add(new_variation)

            # Delete variations not included in the form
            for remaining_variation in existing_variations.values():
                db.session.delete(remaining_variation)

        # Handle image upload
        uploaded_files = request.files.getlist('product_images')
        
        # Only proceed with image deletion and upload if there are uploaded files
        if uploaded_files and any(file for file in uploaded_files if file.filename):
            # Remove existing images only if new images are uploaded
            for image in product.images:
                db.session.delete(image)  # Delete from database
                # Optionally delete from filesystem
                image_path = os.path.join(app.root_path, 'static/profile_pics', image.image_path)
                if os.path.exists(image_path):
                    os.remove(image_path)

            # Process new images
            for file in uploaded_files:
                if file:
                    filename = secure_filename(file.filename)
                    upload_folder = os.path.join(app.root_path, 'static/profile_pics')
                    file.save(os.path.join(upload_folder, filename))  # Save the file
                    new_image = ProductImage(product_id=product.id, image_path=filename)
                    db.session.add(new_image)

        db.session.commit()
        flash('Product and variations updated successfully!', 'success')
        return redirect(url_for('seller_product'))  # Redirect to the product list or any desired page
    
    else:
        print("Form Errors:", form.errors)

    # Populate the form with existing product data
    form.product_name.data = product.name
    form.category.data = product.category
    form.brand.data = product.brand
    form.material.data = product.material
    form.description.data = product.description

    # Prepare existing variations data to pre-fill in the form
    existing_variations = [
        {'color': v.color, 'size': v.size, 'stock': v.stock, 'price': v.price}
        for v in product.variations
    ]

    return render_template('edit_product.html', form=form, product=product, existing_variations=existing_variations)







@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not current_user.is_authenticated:
        flash('Please log in to add items to your cart.', 'danger')
        return redirect(url_for('login'))

    quantity = request.form.get('quantity', type=int)
    selected_color = request.form.get('selected_color')
    selected_size = request.form.get('selected_size')
    price = request.form.get('price', type=float)

    print("price",price)

    if not price or price == '':
        flash('Error: Price not found or invalid.', 'danger')
        return redirect(url_for('product', product_id=product_id))

    # Fetch the product from the database
    product = Product.query.get(product_id)
    if not product:
        flash('Error: Product not found.', 'danger')
        return redirect(url_for('shop'))

    # Check if the item already exists in the user's cart
    existing_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id,
        color=selected_color,
        size=selected_size
    ).first()

    if existing_item:
        # Update the quantity if the item already exists in the cart
        existing_item.quantity += quantity
    else:
        # Create a new CartItem and add it to the database
        new_cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity,
            color=selected_color,
            size=selected_size,
            price=price
        )
        db.session.add(new_cart_item)

    db.session.commit()

    flash('Product added to cart!', 'success')
    return redirect(url_for('product', product_id=product_id))






@app.route('/cart')
def view_cart():
    if not current_user.is_authenticated:
        flash('Please log in to view your cart.', 'danger')
        return redirect(url_for('login'))

    # Fetch the user's cart items from the database
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    products = {item.product_id: Product.query.get(item.product_id) for item in cart_items}

    # Calculate the subtotal for the cart
    subtotal = sum(item.price * item.quantity for item in cart_items)

    return render_template('cart.html', cart=cart_items, subtotal=subtotal, products=products)


@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    if not current_user.is_authenticated:
        flash('Please log in to clear your cart.', 'danger')
        return redirect(url_for('login'))

    # Clear all items from the user's cart in the database
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()

    flash('Cart cleared!', 'success')
    return redirect(url_for('view_cart'))  # Redirect to the cart page


@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    if not current_user.is_authenticated:
        flash('Please log in to remove items from your cart.', 'danger')
        return redirect(url_for('login'))

    # Fetch the item to remove from the database
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if cart_item:
        db.session.delete(cart_item)  # Remove the item from the database
        db.session.commit()  # Commit the changes to the database
        flash('Item removed from cart!', 'success')
    else:
        flash('Error: Item not found in cart.', 'danger')

    return redirect(url_for('view_cart'))  # Redirect to the cart page


@app.route('/update_cart', methods=['POST'])
def update_cart():
    item_ids = request.form.getlist('item_ids[]')
    quantities = request.form.getlist('quantities[]')

       # Debugging: Print the incoming data
    print("Received item_ids:", item_ids)
    print("Received quantities:", quantities)

    for item_id, quantity in zip(item_ids, quantities):
        cart_item = CartItem.query.get(item_id)
        if cart_item:
            cart_item.quantity = int(quantity)
            db.session.commit()

    return redirect(url_for('checkout'))




@app.route('/cart_items')
def cart_items():
    if not current_user.is_authenticated:
        flash('Please log in to view your cart.', 'danger')
        return redirect(url_for('login'))

    # Fetch the user's cart items from the database
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    # Calculate the subtotal for the cart
    subtotal = sum(item.price * item.quantity for item in cart_items)

    return render_template('cart.html', cart=cart_items, subtotal=subtotal)

@app.context_processor
def inject_cart():
    cart_items = []
    cart_total = 0
    
    if current_user.is_authenticated:
        # Fetch user's cart items from the database
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        cart_total = sum(item.price * item.quantity for item in cart_items)
    else:
        # Handle guest cart stored in the session
        session_cart = session.get('cart', {})
        # Ensure session_cart is iterable with price and quantity available
        cart_items = [
            {'price': item['price'], 'quantity': item['quantity']}
            for item in session_cart.values()
        ]
        cart_total = sum(item['price'] * item['quantity'] for item in cart_items)

    return dict(cart_items=cart_items, cart_total=cart_total)



# @app.route('/checkout')
# @login_required
# def checkout():
#     if not current_user.is_authenticated:
#         flash('Please log in to proceed with checkout.', 'danger')
#         return redirect(url_for('login'))

#     # Fetch the updated cart items for the user
#     cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

#     # Check if the cart is empty
#     if not cart_items:
#         flash('Your cart is empty.', 'danger')
#         return redirect(url_for('shop'))

#     # Group cart items by seller to calculate shipping fees per seller
#     seller_orders = {}
#     for item in cart_items:
#         product = Product.query.get(item.product_id)
#         seller_id = product.seller_id

#         if seller_id not in seller_orders:
#             seller_orders[seller_id] = []
#         seller_orders[seller_id].append(item)

#     # Calculate subtotal for all cart items and shipping fees for each seller
#     subtotal = sum(item.price * item.quantity for item in cart_items)
#     total_shipping_fee = len(seller_orders) * 45.00  # Flat fee of 45.00 per seller
#     total_amount = subtotal + total_shipping_fee

#     user_addresses = UserAddress.query.filter_by(user_id=current_user.id).all()
#     default_address = UserAddress.query.filter_by(user_id=current_user.id, is_default=True).first()

#     if not user_addresses:
#         flash('Please add a shipping address before proceeding to checkout.', 'danger')
#         return redirect(url_for('account_address'))

#     # Fetch products by their IDs to create a dictionary for quick access
#     product_ids = [item.product_id for item in cart_items]
#     products = Product.query.filter(Product.id.in_(product_ids)).all()

#     # Create a dictionary to map product IDs to product objects for easy access
#     product_dict = {product.id: product for product in products}

#     # Pass cart items, products, subtotal, shipping fee, and total amount to the checkout template
#     return render_template('checkout.html',
#                            cart=cart_items,
#                            products=product_dict,
#                            subtotal=subtotal,
#                            shipping_fee=total_shipping_fee,
#                            total=total_amount,
#                            address=user_addresses,
#                            default_address=default_address)


# @app.route('/buy_now/<int:product_id>', methods=['POST'])
# def buy_now(product_id):
#     if not current_user.is_authenticated:
#         flash('Please log in to proceed with checkout.', 'danger')
#         return redirect(url_for('login'))
    
#     print(int(request.form.get('quantity')) )
#     quantity = int(request.form.get('quantity', 1)) 
#     selected_color = request.form.get('selected_color')
#     selected_size = request.form.get('selected_size')

#     # Check for price validity before converting to float
#     price_str = request.form.get('price', None)
#     if not price_str or price_str == '':
#         flash('Error: Price not found or invalid.', 'danger')
#         return redirect(url_for('product', product_id=product_id))
    
#     try:
#         price = float(price_str)  # Convert to float here
#     except ValueError:
#         flash('Error: Invalid price format.', 'danger')
#         return redirect(url_for('product', product_id=product_id))

#     # Fetch the product and variation
#     product = Product.query.get(product_id)
#     if not product:
#         flash('Product not found.', 'danger')
#         return redirect(url_for('shop'))

#     # Check for valid product variation
#     product_variation = ProductVariation.query.filter_by(
#         product_id=product.id,
#         color=selected_color,
#         size=selected_size
#     ).first()

#     if not product_variation:
#         flash('Error: Price not found or invalid.', 'danger')
#         return redirect(url_for('product', product_id=product_id))

#     # Add product to a temporary cart-like structure for immediate checkout
#     cart_items = [{
#         'product_id': product_id,
#         'quantity': quantity,
#         'color': selected_color,
#         'size': selected_size,
#         'price': price  
#     }]

#     user_addresses = UserAddress.query.filter_by(user_id=current_user.id).all()
#     default_address = UserAddress.query.filter_by(user_id=current_user.id, is_default=True).first()

#     if not user_addresses:
#         flash('Please add a shipping address before proceeding to checkout.', 'danger')
#         return redirect(url_for('account_address'))

#     # Direct the user to the checkout page with the item added
#     return redirect(url_for('checkout_single', 
#                             product_id=product_id, 
#                             quantity=quantity,
#                             color=selected_color, 
#                             size=selected_size, 
#                             price=price,
#                             address=user_addresses,
#                             default_address=default_address))





# @app.route('/checkout_single')
# def checkout_single():
#     if not current_user.is_authenticated:
#         flash('Please log in to proceed with checkout.', 'danger')
#         return redirect(url_for('login'))

#     # Get parameters from the request
#     product_id = request.args.get('product_id')
#     quantity_str = request.args.get('quantity')  # This comes as a string
#     color = request.args.get('color')
#     size = request.args.get('size')
#     price_str = request.args.get('price')  # This also comes as a string

#     # Debugging: Log the received values
#     print(f'Product ID: {product_id}, Quantity: {quantity_str}, Color: {color}, Size: {size}, Price: {price_str}')

#     # Convert received values
#     try:
#         quantity = int(quantity_str) if quantity_str is not None else 1  # Default to 1 if None
#         price = float(price_str) if price_str is not None else 0.0 
#         total_price = quantity * price  # Calculate total price
#     except ValueError:
#         flash('Error: Invalid quantity or price format.', 'danger')
#         return redirect(url_for('shop'))

#     # Fetch the product
#     product = Product.query.get(product_id)
#     if not product:
#         flash('Product not found.', 'danger')
#         return redirect(url_for('shop'))

#     shipping_fee = 45.00 
#     # Fetch user addresses
#     user_addresses = UserAddress.query.filter_by(user_id=current_user.id).all()
#     default_address = UserAddress.query.filter_by(user_id=current_user.id, is_default=True).first()

#     # Render the checkout template
#     return render_template('checkout_single.html',
#                            product=product,
#                            quantity=quantity,
#                            color=color,
#                            size=size,
#                            price=price,
#                            shipping_fee=shipping_fee,
#                            total_price=total_price,  # Pass total price to the template
#                            user_addresses=user_addresses,
#                            default_address=default_address)









# @app.route('/confirm_order', methods=['POST'])
# def confirm_order():
#     if not current_user.is_authenticated:
#         flash('Please log in to confirm your order.', 'danger')
#         return redirect(url_for('login'))

#     # Get the cart items for the current user
#     cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

#     if not cart_items:
#         flash('Your cart is empty.', 'danger')
#         return redirect(url_for('shop'))

#     # Retrieve the default address for the current user
#     default_address = UserAddress.query.filter_by(user_id=current_user.id, is_default=True).first()

#     if not default_address:
#         flash('Please set a default address before confirming your order.', 'danger')
#         return redirect(url_for('checkout'))

#     # Group cart items by seller
#     seller_orders = {}
#     for item in cart_items:
#         product = Product.query.get(item.product_id)
#         seller_id = product.seller_id

#         if seller_id not in seller_orders:
#             seller_orders[seller_id] = []
#         seller_orders[seller_id].append(item)

#     # Create orders for each seller
#     order_ids = []  # Store the IDs of created orders
#     for seller_id, items in seller_orders.items():
#         # Calculate subtotal for the seller's items
#         subtotal = sum(item.price * item.quantity for item in items)
#         shipping_fee = 45.00  # Flat shipping fee per seller
#         total_amount = subtotal + shipping_fee

#         # Create a new order in the database for this seller
#         new_order = Order(
#             user_id=current_user.id,
#             address_id=default_address.id,
#             total_amount=total_amount
#         )
#         db.session.add(new_order)
#         db.session.flush()  # Use flush to get the order ID without committing yet

#         # Save each cart item as an order item for this seller
#         for item in items:
#             # Create OrderItem with size and color
#             order_item = OrderItem(
#                 order_id=new_order.id,
#                 product_id=item.product_id,
#                 quantity=item.quantity,
#                 price=item.price,
#                 seller_id=seller_id,
#                 color=item.color,  # Retrieve color from the cart item
#                 size=item.size  # Retrieve size from the cart item
#             )
#             db.session.add(order_item)

#         order_ids.append(new_order.id)  # Collect the order ID for feedback later

#     # Clear the user's cart after creating all the orders
#     CartItem.query.filter_by(user_id=current_user.id).delete()
#     db.session.commit()  # Commit all changes at once

#     flash('Your orders have been placed successfully!', 'success')
#     return redirect(url_for('order_summary', order_ids=','.join(map(str, order_ids))))  # Pass order_ids as a comma-separated string





@app.route('/order_summary/<string:order_ids>')
def order_summary(order_ids):
    # Split the order_ids string into a list of integers
    order_id_list = list(map(int, order_ids.split(',')))

    # Retrieve orders from the database
    orders = Order.query.filter(Order.id.in_(order_id_list)).all()
    
    addresses = {}
    order_items = []

    # Retrieve order details
    for order in orders:
        if order:
            # Retrieve the address linked to each order
            address = UserAddress.query.get(order.address_id)
            addresses[order.id] = address  # Store the address by order ID

            # Retrieve order items for each order
            items = OrderItem.query.filter_by(order_id=order.id).all()
            order_items.append((order, items))  # Append a tuple of order and its items

    return redirect(url_for('user_ToPay'))







@app.route('/change_address', methods=['POST'])
@login_required
def change_address():
    address_id = request.form.get('address_id')

    # Update the existing default address to False
    UserAddress.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})

    # Set the selected address as the new default address
    new_default_address = UserAddress.query.get(address_id)
    new_default_address.is_default = True

    db.session.commit()

    flash('Delivery address updated successfully.', 'success')

    # Redirect back to the checkout or the page where the address is displayed
    return redirect(url_for('checkout'))


@app.route('/change_address/single', methods=['POST'])
@login_required
def change_address_single():
    address_id = request.form.get('address_id')

    # Retrieve the additional parameters
    product_id = request.form.get('product_id')
    quantity_str = request.form.get('quantity')  # This will be a string
    color = request.form.get('color')
    size = request.form.get('size')
    price_str = request.form.get('price')  # This will also be a string

    # Validate address_id
    if address_id is None:
        flash('Error: No address selected. Please select an address.', 'danger')
        return redirect(url_for('checkout_single'))

    # Update the existing default address to False
    UserAddress.query.filter_by(user_id=current_user.id, is_default=True).update({'is_default': False})

    # Set the selected address as the new default address
    new_default_address = UserAddress.query.get(address_id)

    if new_default_address is None:
        flash('Error: Selected address not found.', 'danger')
        return redirect(url_for('checkout_single'))

    new_default_address.is_default = True
    db.session.commit()

    flash('Delivery address updated successfully.', 'success')

    # Redirect back to the checkout with parameters
    return redirect(url_for('checkout_single', 
                            product_id=product_id,
                            quantity=quantity_str,
                            color=color,
                            size=size,
                            price=price_str))







# @app.route('/place_order', methods=['POST'])
# def place_order():
#     # Extract data from the form submission
#     product_id = request.form.get('product_id')
#     quantity = request.form.get('quantity', type=int)  # Ensure quantity is an integer
#     selected_color = request.form.get('selected_color')
#     selected_size = request.form.get('selected_size')
#     total_price = request.form.get('total_price', type=float)  
#     price = request.form.get('price', type=float)
    
    
   
#     shipping_fee = 45.00  

#     # Find the default address for the current user
#     default_address = UserAddress.query.filter_by(user_id=current_user.id, is_default=True).first()

#     if not default_address:
#         flash('No default address found. Please add or select a default address.', 'danger')
#         return redirect(url_for('user_profile'))  # Redirect to the user profile or address management page


#     # Calculate the total price including shipping
#     print(f"TOTAL PRICE GALING CHECKOUT SINGLE: {total_price}")

#     total_price_with_shipping = total_price + shipping_fee
#     print(f"Total Price (with shipping): {total_price_with_shipping}")

#     # Create a new Order instance
#     new_order = Order(
#         user_id=current_user.id,
#         total_amount=total_price_with_shipping,  # Store the total amount with shipping
#         address_id=default_address.id,
#         date_created=datetime.utcnow()
     
#     )

#     # Add the order to the session and flush to get the order ID
#     db.session.add(new_order)
#     db.session.flush()  # Flush so we can get new_order.id before committing

#     # Get the product and seller details
#     product = Product.query.get(product_id)
#     seller_id = product.seller_id if product else None

#     if not product or not seller_id:
#         flash('Invalid product or seller information.', 'danger')
#         return redirect(url_for('shop'))  # Redirect to the shop if the product is not found

#     # Create a new OrderItem instance
#     new_order_item = OrderItem(
#         order_id=new_order.id,  
#         product_id=product_id,
#         quantity=quantity,
#         price=price,  
#         seller_id=seller_id,
#         color=selected_color,  # Store the selected color
#         size=selected_size     # Store the selected size
#     )

#     # Add the order item to the session
#     db.session.add(new_order_item)

#     # Commit the changes to the database
#     db.session.commit()

#     # Flash a success message
#     flash('Order placed successfully!', 'success')

#     # Redirect to a relevant page, e.g., order confirmation or product page
#     return redirect(url_for('user_ToPay'))  # Replace 'shop' with your target function





@app.route("/account/pay", methods=['GET', 'POST'])
@login_required
def user_ToPay():
    order_items = (OrderItem.query
          .join(Order) 
          .join(Product, OrderItem.product_id == Product.id)  # Join with Product if necessary
          .filter(Order.user_id == current_user.id)  
          .filter(OrderItem.status == 'Pending') 
          .order_by(OrderItem.id)  
          .all())

    # Create a dictionary to map order IDs to total amounts
    order_totals = {}
    for item in order_items:
        if item.order.id not in order_totals:
            order_totals[item.order.id] = item.order.total_amount

    return render_template('to_pay.html', order_items=order_items, order_totals=order_totals)




@app.route("/account/Ship", methods=['GET', 'POST'])
@login_required
def user_ToShip():
    order_items = (OrderItem.query
          .join(Order) 
          .join(Product, OrderItem.product_id == Product.id)  # Join with Product if necessary
          .filter(Order.user_id == current_user.id)  
          .filter(OrderItem.status.in_( ['Order Placed', 'Preparing to Shipped']))  # Include both statuses
          .order_by(OrderItem.id)  
          .all())

    # Create a dictionary to map order IDs to total amounts
    order_totals = {}
    for item in order_items:
        if item.order.id not in order_totals:
            order_totals[item.order.id] = item.order.total_amount

    return render_template('ToShip.html', order_items=order_items, order_totals=order_totals)


@app.route("/account/Receive", methods=['GET', 'POST'])
@login_required
def user_ToReceive():
    order_items = (OrderItem.query
          .join(Order) 
          .join(Product, OrderItem.product_id == Product.id)  # Join with Product if necessary
          .filter(Order.user_id == current_user.id)  
          .filter(OrderItem.status.in_( ['In Transit']))  # Include both statuses
          .order_by(OrderItem.id)  
          .all())
    

    # Create a dictionary to map order IDs to total amounts
    order_totals = {}
    for item in order_items:
        if item.order.id not in order_totals:
            order_totals[item.order.id] = item.order.total_amount

    for item in order_items:
        print(f"OrderItem ID: {item.id}, Product: {item.product}, Seller: {item.product.seller if item.product else 'No Product'}")


    return render_template('ToReceive.html', order_items=order_items, order_totals=order_totals)



# from collections import defaultdict

@app.route("/account/Completed", methods=['GET', 'POST'])
@login_required
def user_Completed():

    if not session.get('auto_confirm_checked'):  
        auto_confirm_order_received()
        session['auto_confirm_checked'] = True
    
    # auto_confirm_order_received()

    # Fetch all delivered order items for the current user
    order_items = (OrderItem.query
                   .join(Order)
                   .join(Product, OrderItem.product_id == Product.id)  # Join with Product if necessary
                   .filter(Order.user_id == current_user.id)
                   .filter(OrderItem.status.notin_(['Cancelled']))  # Exclude Cancelled
                   .filter(OrderItem.status == 'Delivered')        # Only Delivered
                   .order_by(OrderItem.id)
                   .all())

    # Group order items by order_id
    grouped_orders = defaultdict(list)
    grouped_sellers = {}
    for item in order_items:
        grouped_orders[item.order.id].append(item)
        if item.product and item.product.seller:
            grouped_sellers[item.product.seller.user.id] = item.product.seller.user

    # Create a dictionary for order totals
    order_totals = {order_id: items[0].order.total_amount for order_id, items in grouped_orders.items()}

    return render_template('account_completed.html', grouped_orders=grouped_orders, order_totals=order_totals, grouped_sellers=grouped_sellers)



@app.route("/account/Receive/Order", methods=['GET', 'POST'])
@login_required
def user_received():
    # Fetch all delivered order items for the current user
    order_items = (OrderItem.query
          .join(Order) 
          .filter(Order.user_id == current_user.id)  
          .filter(OrderItem.status == 'Received')  # Include only 'Delivered' status
          .order_by(OrderItem.id)  
          .all())

    reviews = {item.product.id: Review.query.filter_by(product_id=item.product.id, user_id=current_user.id).first() for item in order_items}


    # Calculate total amounts for each order item (if needed)
    item_totals = {item.id: item.price * item.quantity for item in order_items}

    return render_template('account_received.html', order_items=order_items, item_totals=item_totals, reviews=reviews)



@app.route("/account/Cancelled", methods=['GET', 'POST'])
@login_required
def user_Cancelled():
    order_items = (OrderItem.query
          .join(Order) 
          .filter(Order.user_id == current_user.id)  
          .filter(OrderItem.status == 'Cancelled') 
          .order_by(OrderItem.id)  
          .all())

    # Create a dictionary to map order IDs to total amounts
    order_totals = {}
    for item in order_items:
        if item.order.id not in order_totals:
            order_totals[item.order.id] = item.order.total_amount

    return render_template('UserCancelled.html', order_items=order_items, order_totals=order_totals)



@app.route('/seller/orders')
@login_required  
def seller_orders():
    # Get the current user's seller ID
    seller = Seller.query.filter_by(user_id=current_user.id).first()
    
    if not seller:
        flash('No seller account found.', 'danger')
        return redirect(url_for('shop'))  # Redirect to shop or any other page

    # Fetch all orders that contain items sold by this seller
    seller_orders = (Order.query
                     .join(OrderItem)  # Join the OrderItem table
                     .filter(OrderItem.seller_id == seller.id)  # Filter by the seller's ID
                     .all())

    # Prepare structures to hold combined orders based on their status
    combined_orders = {}
    canceled_orders = {}
    order_placed_orders = {}
    preparing_to_ship_orders = {}
    delivered_orders = {}
    
    

    for order in seller_orders:
        # Find pending order items in this order for the current seller
        pending_items = [item for item in order.order_items if item.seller_id == seller.id and item.status == 'Pending']

        # If there are pending items, add the order and items to the combined orders structure
        if pending_items:
            combined_orders[order.id] = {
                'order': order,
                'items': pending_items
            }

        # Find canceled order items in this order for the current seller
        canceled_items = [item for item in order.order_items if item.seller_id == seller.id and item.status == 'Cancelled']

        # If there are canceled items, add the order and items to the canceled orders structure
        if canceled_items:
            canceled_orders[order.id] = {
                'order': order,
                'items': canceled_items
            }

        # Find order placed items in this order for the current seller
        order_placed_items = [item for item in order.order_items if item.seller_id == seller.id and item.status == 'Order Placed']

        # If there are order placed items, add the order and items to the order placed orders structure
        if order_placed_items:
            order_placed_orders[order.id] = {
                'order': order,
                'items': order_placed_items
            }

        preparing_to_ship_items = [
            item for item in order.order_items 
            if item.seller_id == seller.id and item.status in ['Preparing to Shipped', 'In Transit','Delivered']
        ]
        if preparing_to_ship_items:
            preparing_to_ship_orders[order.id] = {
                'order': order,
                'items': preparing_to_ship_items
            }

        delivered_items = [item for item in order.order_items if item.seller_id == seller.id and item.status == 'Received']

        # If there are delivered items, add the order and items to the delivered orders structure
        if delivered_items:
            delivered_orders[order.id] = {
                'order': order,
                'items': delivered_items
            }

            for item in order.order_items:
                # Query Pickup through the pickup_orderitem association table
                pickup = Pickup.query.join(pickup_orderitem).filter(pickup_orderitem.c.order_item_id == item.id).first()
                
                if pickup and pickup.delivery_image:
                    # Store the delivery image data as base64 encoding
                    item.delivery_image = base64.b64encode(pickup.delivery_image).decode('utf-8')
                    print("FOUND IMAGE")
                else:
                    item.delivery_image = None  # No image found
                    print("NOT FOUND IMAGE")


            # Debugging: Print order placed orders to the console
            print(f"Order Placed ID: {order.id}")
            for item in order_placed_items:
                print(f"Product ID: {item.product_id}, Quantity: {item.quantity}, Price: {item.price}")

    # Convert combined_orders, canceled_orders, and order_placed_orders to lists for rendering in the template
    combined_order_list = [{
        'order': order_data['order'],
        'order_items': order_data['items'],
    } for order_id, order_data in combined_orders.items()]

    canceled_order_list = [{
        'order': order_data['order'],
        'order_items': order_data['items'],
    } for order_id, order_data in canceled_orders.items()]

    order_placed_order_list = [{
        'order': order_data['order'],
        'order_items': order_data['items'],
    } for order_id, order_data in order_placed_orders.items()]


    delivered_order_list = [{
        'order': order_data['order'],
        'order_items': order_data['items'],
    } for order_id, order_data in delivered_orders.items()]

    preparing_to_ship_order_list = [{'order': order_data['order'], 'order_items': order_data['items']} for order_id, order_data in preparing_to_ship_orders.items()]


    # Render the orders in the template (including order placed)
    return render_template('seller_orders.html', 
                           orders=combined_order_list, 
                           canceled_orders=canceled_order_list,
                           order_placed_orders=order_placed_order_list,preparing_to_ship_orders=preparing_to_ship_order_list,delivered_orders=delivered_order_list)






@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    order_item_id = request.form.get('order_item_id')
    cancel_reason = request.form.get('cancel_reason')  # Get the cancellation reason

    # Fetch the specific order item
    order_item = OrderItem.query.get(order_item_id)
    
    if order_item:
        order_item.status = 'Cancelled'
        order_item.cancel_reason = cancel_reason  # Store the cancellation reason

        order = order_item.order

        # Recalculate the total amount for the order, excluding cancelled items
        non_cancelled_items_total = sum(
            item.price * item.quantity for item in order.order_items if item.status != 'Cancelled'
        )
        
        # Add the fixed shipping fee (set to 45)
        shipping_fee = 45
        new_total = non_cancelled_items_total + shipping_fee
        order.total_amount = new_total  # Update the total amount in the order

        db.session.commit()

        # Send email to the user
        user = order.user  # Assuming the `Order` model has a `user` relationship
        if user:
            send_cancellation_notification_email(user.email, order_item, cancel_reason, new_total)

        flash(f'Item {order_item.product.name} cancelled successfully! Reason: {cancel_reason}. New total: ₱{new_total}', 'success')
    else:
        flash('Order item not found.', 'danger')

    return redirect(url_for('seller_orders'))


def send_cancellation_notification_email(to_email, order_item, cancel_reason, new_total):
    """
    Sends a cancellation notification email to the user.
    """
    try:
        subject = "Order Item Cancellation Notification"
        body = (
            f"Dear {order_item.order.user.first_name} {order_item.order.user.last_name},\n\n"
            f"We would like to inform you that one of your order items has been cancelled.\n\n"
            f"Item: {order_item.product.name}\n"
            f"Reason for Cancellation: {cancel_reason}\n"
            f"Please log in to your account for more details.\n\n"
            f"Regards,\n"
            f"The SheWear Team"
        )
        msg = Message(subject, recipients=[to_email], body=body)
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send cancellation email: {e}")
        flash('Failed to notify the user via email.', 'danger')




    

@app.route('/order/placed', methods=['POST'])
@login_required  
def placed_order():
    order_item_id = request.form.get('order_item_id')  
    order_item = OrderItem.query.get(order_item_id)
    
    if not order_item:
        flash('Order item not found.', 'danger')
        return redirect(url_for('seller_orders')) 

    # Fetch the product variation associated with the order item
    product_variation = ProductVariation.query.filter_by(
        product_id=order_item.product_id,
        color=order_item.color,
        size=order_item.size
    ).first()

    if not product_variation:
        flash('Product variation not found.', 'danger')
        return redirect(url_for('seller_orders'))  

    # Check if the quantity can be fulfilled
    if order_item.quantity > 0 and product_variation.stock >= order_item.quantity:
        order_item.status = 'Order Placed'  
        previous_stock = product_variation.stock
        product_variation.stock -= order_item.quantity

        # Log the stock change in StockHistory
        stock_history_entry = StockHistory(
            product_id=order_item.product_id,
            stock_change=abs(order_item.quantity),
            previous_stocks=previous_stock,
            date=datetime.utcnow(),
            seller_id=order_item.seller_id,
            user_id=order_item.order.user_id,
            order_id=order_item.order_id
        )
        db.session.add(stock_history_entry)

        # Define thresholds and corresponding messages
        thresholds = {
            20: "Stock for {product} is at 20 units. Consider restocking soon.",
            15: "Stock for {product} is at 15 units. Pay attention to inventory.",
            10: "Stock for {product} is running low at 10 units.",
            5: "Stock for {product} is critically low with only 5 units left!",
            1: "Urgent! Stock for {product} is almost gone with just 1 unit left.",
            0: "Out of stock alert! Stock for {product} has completely run out!"
        }

        # Check if the stock crosses a threshold
        for threshold, message in thresholds.items():
            if previous_stock > threshold >= product_variation.stock:
                # Check for an existing notification for this product variation
                existing_notification = StockNotification.query.filter_by(
                    seller_id=order_item.seller_id,
                    product_id=order_item.product_id,
                    stock=threshold
                ).first()

                # Avoid duplicate notifications for the same threshold
                if not existing_notification:
                    product = Product.query.get(order_item.product_id)
                    notification = StockNotification(
                        seller_id=order_item.seller_id,
                        product_id=order_item.product_id,
                        stock=product_variation.stock,
                        message=message.format(product=product.name if product else "Unknown Product"),
                        date=datetime.utcnow()
                    )
                    db.session.add(notification)
                    print(f"Notification added: {notification}")
        
        db.session.commit()

        flash('Order status updated to Placed. Quantity decreased.', 'success')
    else:
        flash('Insufficient stock to fulfill the order.', 'danger')
        
    return redirect(url_for('seller_orders'))  # Redirect back to the orders page






@app.route('/order/<int:order_id>', methods=['GET'])
@login_required  
def order_detail(order_id):
    # Fetch the order by ID
    order = Order.query.get_or_404(order_id)

    if order.user_id != current_user.id:
        flash("You do not have permission to view this order.", "danger")
        return redirect(url_for('home'))

    # Fetch order items that are not cancelled
    order_items = OrderItem.query.filter_by(order_id=order.id).filter(OrderItem.status != 'Cancelled').all()

    # Pass order and order_items to the template for rendering
    return render_template('order_detail.html', order=order, order_items=order_items)



@app.route('/admin/products', methods=['GET'])
@role_required('admin')
@login_required
def admin_products():
    # Get the current page number from the request arguments, default to 1
    page = request.args.get('page', 1, type=int)

    # Query products with pagination
    products = Product.query.options(joinedload(Product.seller)).filter_by(is_active=True).paginate(page=page, per_page=6)


    return render_template('admin_products.html', products=products)



@app.route('/admin/courier', methods=['GET', 'POST'])
@role_required('admin')
@login_required
def admin_courier():
    couriers = Courier.query.all()  # Fetch all couriers
    
    for courier in couriers:
        user = courier.user
        # Encode ID picture to Base64 if available
        if user.id_picture:  # Assuming `id_picture` is a binary blob in the database
            user.image_data = base64.b64encode(user.id_picture).decode('utf-8')
        else:
            user.image_data = None  # Default to None if no image is available

    return render_template('admin_courier.html', couriers=couriers)


@app.route('/admin/courier/update/<int:courier_id>', methods=['POST'])
@role_required('admin')
@login_required
def update_courier(courier_id):
    data = request.get_json()

    courier = Courier.query.get_or_404(courier_id)
    user = courier.user  # Access the courier's associated user
    
    # Update the courier fields
    courier.service_area = data['serviceArea']
    courier.vehicle_type = data['vehicleType']
    courier.vehicle_registration_no = data['vehicleRegistration']

    # Update the user's fields (optional)
    user.first_name = data['firstName']
    user.last_name = data['lastName']
    user.email = data['email']
    
    try:
        db.session.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

    


def load_json_data():
    data_directory = os.path.join(os.path.dirname(__file__), '..', 'data')
    
    regions = []
    provinces = []
    cities = []
    barangays = []

    try:
        with open(os.path.join(data_directory, 'region.json'), encoding='utf-8') as f:
            regions = json.load(f)

        with open(os.path.join(data_directory, 'province.json'), encoding='utf-8') as f:
            provinces = json.load(f)

        with open(os.path.join(data_directory, 'city.json'), encoding='utf-8') as f:
            cities = json.load(f)

        with open(os.path.join(data_directory, 'barangay.json'), encoding='utf-8') as f:
            barangays = json.load(f)

    except Exception as e:
        print("Error loading JSON data:", e)

    return regions, provinces, cities, barangays


@app.route('/get_provinces/<region_code>', methods=['GET'])
def get_provinces(region_code):
    _, provinces, _, _ = load_json_data()
    
    # Filter provinces based on the selected region_code
    filtered_provinces = [
        (province['province_code'], province['province_name'])
        for province in provinces if province['region_code'] == region_code
    ]
    
    return jsonify(filtered_provinces)

@app.route('/get_cities/<province_code>', methods=['GET'])
def get_cities(province_code):
    _, _, cities, _ = load_json_data()
    
    # Filter cities based on the selected province_code
    filtered_cities = [
        (city['city_code'], city['city_name'])
        for city in cities if city['province_code'] == province_code
    ]
    
    return jsonify(filtered_cities)


@app.route('/get_barangays/<city_code>', methods=['GET'])
def get_barangays(city_code):
    _, _, _, barangays = load_json_data()
    
    # Filter barangays based on the selected city_code
    filtered_barangays = [
        (barangay['brgy_code'], barangay['brgy_name'])
        for barangay in barangays if barangay['city_code'] == city_code
    ]
    
    return jsonify(filtered_barangays)







@app.route('/admin/courier/add', methods=['GET', 'POST'])
@role_required('admin')
@login_required
def admin__add_courier():
    form = CourierForm()
    regions, provinces, cities, barangays = load_json_data()

    # Populate region choices
    form.region.choices = [(region['region_code'], region['region_name']) for region in regions]

    if form.validate_on_submit():
        # Step 1: Create a new user entry for the courier
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = Users(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            # Hash the password securely
            password=hashed_pass,
            is_validated=True,
            role='courier'
            
        )

        # Save ID picture if uploaded
        if form.id_picture.data:
            filename = secure_filename(form.id_picture.data.filename)
            user.id_picture = form.id_picture.data.read()

        db.session.add(user)
        db.session.flush()  # Flush to get the user ID for foreign key references


        selected_region_id = form.region.data         # Get selected region ID
        selected_province_id = form.province.data     # Get selected province ID
        selected_barangay_id = form.barangay.data     # Get selected barangay ID
        selected_city_id = form.city.data             # Get selected city ID

        # Fetch the corresponding names using the selected IDs
        barangay_name = next((b['brgy_name'] for b in barangays if b['brgy_code'] == selected_barangay_id), None)
        city_name = next((c['city_name'] for c in cities if c['city_code'] == selected_city_id), None)
        region_name = next((r['region_name'] for r in regions if r['region_code'] == selected_region_id), None)
        province_name = next((p['province_name'] for p in provinces if p['province_code'] == selected_province_id), None)


        # Step 2: Create a Courier entry with address details
        courier = Courier(
            user_id=user.id,
            service_area=form.service_area.data,
            vehicle_type=form.vehicle_type.data,
            vehicle_registration_no=form.vehicle_registration_no.data,
            contact_number=form.contact_number.data, 
            # Address details
            street=form.street.data,  
            barangay=barangay_name,    
            city=city_name,            
            province=province_name,      # Use the actual province name
            region=region_name 
        )

        db.session.add(courier)

        # Commit all changes
        db.session.commit()
        flash('Courier added successfully!', 'success')
        return redirect(url_for('admin_courier'))
    
    else:
        print("Form is NOT valid.")
        print(form.errors)  
    
    return render_template('add_courier.html', form=form, 
                           regions=regions, 
                           provinces=provinces,
                           cities=cities,
                           barangays=barangays)



@app.route("/courier")
@login_required
@role_required('courier')
def courier():

    courier_id = current_user.courier.id

    # Query to count the number of delivered orders for this courier
    delivery_count = (
        db.session.query(func.count(OrderItem.id))
        .join(Order, Order.id == OrderItem.order_id)  # Join OrderItem with Order
        .join(Courier, Courier.id == Order.courier_id)  # Join Order with Courier
        .filter(Courier.id == courier_id, OrderItem.status == 'Delivered')  # Filter by courier and delivered status
        .scalar()  # Get the count directly
    )

    pickup_count = (
    db.session.query(func.count(Pickup.id))
    .join(pickup_orderitem)  # Join Pickup with the association table
    .join(OrderItem, pickup_orderitem.c.order_item_id == OrderItem.id)  # Join with OrderItem
    .join(Order, Order.id == OrderItem.order_id)  # Join with Order
    .filter(Order.courier_id == courier_id, Pickup.status == 'Pending')  # Filter by courier ID and Pickup status
    .scalar()
    )


    received_count = (
        db.session.query(func.count(OrderItem.id))
        .join(Order, Order.id == OrderItem.order_id)  # Join OrderItem with Order
        .join(Courier, Courier.id == Order.courier_id)  # Join Order with Courier
        .filter(Courier.id == courier_id, OrderItem.status == 'Received')  # Filter by courier and delivered status
        .scalar()  # Get the count directly
    )

 


    total_courier_income = db.session.query(db.func.sum(Courier.total_shipping_income)).scalar() or 0.0


    # If no income is found, set it to 0

    return render_template('courier_home.html',title="Courier", delivery_count=delivery_count , courier_income=total_courier_income,pickup_count=pickup_count,received_count=received_count)

@app.route("/courier/orders")
@login_required
@role_required('courier')
def courier_orders():
    courier = current_user.courier  
    if not courier:
        flash("You are not registered as a courier.", "danger")
        return redirect(url_for('home'))

    # Query for all pickups assigned to the current courier, and include related order items and their orders
    assigned_pickups = (
        db.session.query(Pickup)
        .filter(Pickup.courier_id == courier.id)
        .filter(Pickup.status == 'Pending')  
        .join(Pickup.order_items)
        .join(OrderItem.order)
        .options(
            db.joinedload(Pickup.order_items).joinedload(OrderItem.order)
        )
        .all()
    )

   # Retrieve pickups that are ready for delivery (status "Pickup") and group them by Order.id
    to_deliver_query = (
        db.session.query(Pickup)
        .filter(Pickup.courier_id == courier.id)
        .filter(Pickup.status == 'Pickup')  
        .join(Pickup.order_items)
        .join(OrderItem.order)
        .options(
            db.joinedload(Pickup.order_items).joinedload(OrderItem.order)
        )
        .all()
    )

    # Grouping pickups by Order ID
    to_deliver = defaultdict(list)
    for pickup in to_deliver_query:
        for item in pickup.order_items:
            to_deliver[item.order.id].append({
                "pickup": pickup,
                "order_item": item
            })

    delivered_query = (
    db.session.query(Pickup)
    .filter(Pickup.courier_id == courier.id)
    .filter(Pickup.status == 'Delivered')  
    .join(Pickup.order_items)
    .join(OrderItem.order)
    .options(
        db.joinedload(Pickup.order_items).joinedload(OrderItem.order)
    )
    .all()
)

    # Grouping pickups by Order ID for "Delivered" status
    delivered = defaultdict(list)
    for pickup in delivered_query:
        for item in pickup.order_items:
            delivered[item.order.id].append({
                "pickup": pickup,
                "order_item": item
            })


            

    return render_template(
        'courier_orders.html',
        title="Courier Orders",
        orders_grouped_by_id=assigned_pickups,
        to_deliver=to_deliver,
        delivered=delivered
    )


@app.route('/confirm_pickup', methods=['POST'])
def confirm_pickup():
    try:
        # Get the JSON data sent from the client
        data = request.get_json()

        # Log the received data for debugging
        # app.logger.debug(f"Received data: {data}")

        selected_items = data.get('selected_items', [])
        
        if not selected_items:
            return jsonify({'error': 'No items selected for pickup'}), 400
        
        # Track the updated IDs to avoid redundant updates
        updated_ids = []

        # Convert selected_items to a set to ensure unique order IDs
        unique_order_ids = set(selected_items)

        # Update the pickup status to 'Pickup' for each selected item
        for order_id in unique_order_ids:
            order_id = int(order_id)  # Ensure the order_id is an integer

            # Find all OrderItems with this order_id
            order_items = OrderItem.query.filter(OrderItem.order_id == order_id).all()

            for order_item in order_items:
                # Get the associated Pickup for the order_item
                pickup = Pickup.query.join(pickup_orderitem).filter(pickup_orderitem.c.order_item_id == order_item.id).first()

                if pickup and pickup.status != 'Pickup':  # Only update if it's not already 'Pickup'
                    # Log the current status before update
                    app.logger.debug(f"Order {order_id} before update: {pickup.status}")
                    
                    # Update the status directly
                    pickup.status = 'Pickup'  # Set the status to 'Pickup'
                    updated_ids.append(order_id)  # Append the order_id to the list
                    app.logger.debug(f"Order {order_id} status updated to 'Pickup'")
                    send_pickup_email(order_item.order.user, order_item)

        # If any updates occurred, commit them
        if updated_ids:
            db.session.commit()  # Commit the transaction after all updates

        # Return success message
        return jsonify({'success': f'Pickup confirmed for orders: {updated_ids}'})

    except Exception as e:
        # Log the error for debugging purposes
        app.logger.error(f"Error confirming pickup: {e}")
        db.session.rollback()  # Rollback in case of error
        return jsonify({'error': 'An error occurred while confirming pickup'}), 500





def send_pickup_email(user, order_item):
    """
    Sends an email to the user notifying them about the pickup update.
    """
    try:
        msg = Message(
            "Order Pickup Update",
            recipients=[user.email]
        )
        msg.body = f"""
        Hello {user.first_name} {user.last_name},

        Your order for the product "{order_item.product.name}" has been picked up and is on its way for delivery.
        Thank you for shopping with us!

        Best regards,
        SheWear
        """
        mail.send(msg)
        app.logger.debug(f"Email sent to {user.email}")
    except Exception as e:
        app.logger.error(f"Error sending email to {user.email}: {e}")




# ADMIN COURIER DELIVERY
@app.route("/courier/delivery")
@login_required
@role_required('admin')
def courier_delivery():
    pickups = Pickup.query.filter(Pickup.courier_id.isnot(None)).options(
        db.joinedload(Pickup.order_items).joinedload(OrderItem.product)
    ).all()

    return render_template('courier_product_status.html', title="Courier Deliveries", pickups=pickups)





# PAG SCHEDULE NG PICKUP NG COURIER (BY SELLER)
@app.route('/schedule_pickup', methods=['POST'])
@login_required  
def schedule_pickup():
    try:
        data = request.json
        selected_items = data.get('selected_items')
        pickup_date = data.get('pickup_date')

        # Check if required data is provided
        if not selected_items or not pickup_date:
            return jsonify({"error": "Invalid data"}), 400

        # Convert pickup_date from string to a date object
        pickup_date_object = datetime.strptime(pickup_date, '%Y-%m-%d').date()

        # Save each item with the pickup date in the database
        for item_id in selected_items:
            # Assuming `OrderItem` is the model where you're linking items to pickups
            order_item = OrderItem.query.get(item_id)
            if order_item:
                # Update the status of the OrderItem to 'Preparing to Shipped'
                order_item.status = 'Preparing to Shipped'

                # Create a new Pickup record for each item (if not already created)
                pickup = Pickup(scheduled_date=pickup_date_object, status='Scheduled')
                pickup.order_items.append(order_item)  
                db.session.add(pickup)

        db.session.commit()
        
        return jsonify({"success": "Pickup scheduled successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# TABLE LOAD 
@app.route("/courier/assign")
@login_required
@role_required('admin')
def courier_assign():
    # Fetch orders that have at least one item with status 'Preparing to Shipped'
    assignable_orders = (Order.query
                         .join(OrderItem)
                         .filter(OrderItem.status == "Preparing to Shipped")
                         .filter(~OrderItem.status.in_(["Canceled"]))  
                         .distinct()  # Ensure unique orders are returned
                         .all())
    
    # Fetch available couriers (those who are active)
    available_couriers = Courier.query.filter(Courier.is_active == True).all()  # Use is_active instead of is_available

   

    return render_template(
        'assign_courier.html',
        title="Assign Courier",
        assignable_orders=assignable_orders,
        available_couriers=available_couriers
    )



# LOGIC FOR ASSIGNIGN COURIERS
@app.route('/assign_courier', methods=['POST'])
@role_required('admin')
def assign_courier():
    order_ids = request.form.get('order_ids').split(',')
    courier_id = request.form.get('courier_id')
    
    successful_assignments = 0  # To track successful assignments
    courier = Courier.query.get(courier_id)

    if not courier:
        flash("Courier not found.", "danger")
        return redirect(url_for('courier_assign'))
    
    user = courier.user 
    
    for order_id in order_ids:
        order = Order.query.get(order_id)
        if order:
            # Assign the courier ID to the order
            order.courier_id = courier_id
            
            # Update each OrderItem status to 'Shipped'
            for item in order.order_items:
                if item.status == 'Cancelled':  # Skip canceled items
                    continue


                item.status = 'In Transit'

                # Check if a Pickup record exists for this order item
                pickup = Pickup.query.filter(Pickup.order_items.any(id=item.id)).first()  

                if pickup:
                    pickup.courier_id = courier_id
                    pickup.status = "Pending"  
                else:
                    pickup = Pickup(
                        scheduled_date=datetime.utcnow(), 
                        courier_id=courier_id,
                        status="Pending" 
                    )
                    db.session.add(pickup)  
            
            successful_assignments += 1  

    db.session.commit()  
    
    if successful_assignments > 0:
        flash(f"{successful_assignments} orders successfully assigned to the courier and items marked as shipped!", "success")
        
        # Send the email
        try:
            subject = "New Orders Assigned to You"
            body = (
                f"Dear {user.first_name} {user.last_name},\n\n"
                f"We’re pleased to inform you that {successful_assignments} new orders have been assigned to you.\n\n"
                f"Please check your assigned orders and proceed with the deliveries at your earliest convenience.\n\n"
                f"We appreciate your dedication and service, and we’re here to support you if you have any questions or issues.\n\n"
                f"Thank you for being an essential part of our team.\n\n"
                f"Best regards,\n"
                f"The SheWear Team"
            )
            msg = Message(subject, recipients=[user.email], body=body)
            mail.send(msg)  # Send the email
            print("Email sent to courier successfully.")
        except Exception as e:
            flash(f'Orders assigned successfully, but an error occurred while sending the email: {str(e)}', 'danger')
    else:
        flash("No orders were assigned. Please check the order IDs.", "danger")
    
    return redirect(url_for('courier_assign'))



@app.route('/cancel_item', methods=['POST'])
def cancel_item():
    order_item_id = request.form.get('order_item_id')
    cancel_reason = request.form.get('cancel_reason')

    if order_item_id and cancel_reason:
        # Update the order item status in the database
        order_item = OrderItem.query.get(order_item_id)
        if order_item:
            # Update status and cancellation reason
            order_item.status = 'Cancelled'
            order_item.cancel_reason = cancel_reason
            db.session.commit()

            # Send email to the seller
            seller = order_item.product.seller  # Assuming OrderItem has a relationship to Product and Seller
            if seller and seller.user:  # Ensure seller and associated user exist
                seller_email = seller.user.email  # Access email via the user relationship
                cancelling_user = current_user  # Assuming Flask-Login is being used to get the current user
                send_cancellation_email(seller_email, order_item, cancel_reason, cancelling_user)

            flash('Item cancelled successfully and seller notified.', 'success')
        else:
            flash('Item not found.', 'danger')
    else:
        flash('Invalid cancellation request.', 'danger')

    return redirect(url_for('user_ToPay'))  # Replace with the correct route for "To Pay" orders


def send_cancellation_email(to_email, order_item, cancel_reason, cancelling_user):
    """
    Sends a cancellation notification email to the seller, including the user's details who cancelled the order.
    """
    try:
        seller_user = order_item.product.seller.user  # Assuming this relationship exists
        subject = "Order Item Cancellation Notification"
        body = (
            f"Dear {seller_user.first_name} {seller_user.last_name},\n\n"
            f"We would like to inform you that an order item has been cancelled.\n\n"
            f"Item: {order_item.product.name}\n"
            f"Reason for Cancellation: {cancel_reason}\n\n"
            f"Cancelled by:\n"
            f"Name: {cancelling_user.first_name} {cancelling_user.last_name}\n"
            f"Please log in to your seller dashboard for more details.\n\n"
            f"Regards,\n"
            f"The SheWear Team"
        )
        msg = Message(subject, recipients=[to_email], body=body)
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send cancellation email: {e}")
        flash('Failed to notify the seller via email.', 'danger')





@app.route("/courier/account", methods=["GET", "POST"])
@login_required
@role_required('courier')
def courier_account():
    form = UpdateCourierProfileForm()

    # Check if the user is authenticated and handle the form submission
    if current_user.is_authenticated:
        if form.validate_on_submit():  # Check if form is valid on submission
            # Update User fields
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.email = form.email.data
            current_user.date_of_birth = form.date_of_birth.data
            current_user.gender = form.gender.data

            # Handle the image upload
            if form.image_file.data:
                # Call the save_picture function to handle image saving
                image_filename = save_picture(form.image_file.data)
                # Update the user's image_file in the database
                current_user.image_file = image_filename

            # Update Courier profile if it exists
            courier = current_user.courier
            if courier:
                courier.street = form.street.data
                courier.barangay = form.barangay.data
                courier.city = form.city.data
                courier.province = form.province.data
                courier.region = form.region.data
                courier.service_area = form.service_area.data
                courier.vehicle_type = form.vehicle_type.data

            # Commit changes to the database
            db.session.commit()

            # Flash a success message
            flash('Profile updated successfully!', category='success')
            return redirect(url_for('courier_account'))  # Redirect to the same page after saving

        # Populate the form with current user data (on GET request)
        else:
            form.first_name.data = current_user.first_name
            form.last_name.data = current_user.last_name
            form.email.data = current_user.email
            form.date_of_birth.data = current_user.date_of_birth
            form.gender.data = current_user.gender

            # Check if the user has a courier profile
            courier = current_user.courier
            if courier:
                form.street.data = courier.street
                form.barangay.data = courier.barangay
                form.city.data = courier.city
                form.province.data = courier.province
                form.region.data = courier.region
                form.service_area.data = courier.service_area
                form.vehicle_type.data = courier.vehicle_type

    # Generate the URL for the uploaded image
    image_file_url = url_for('static', filename='profile_pics/' + current_user.image_file) if current_user.image_file else url_for('static', filename='profile_pics/default.jpg')
    
    return render_template('courier_account.html', title="Courier Deliveries", form=form, image_file_url=image_file_url)





@app.route("/About")
def about():

    return render_template('about.html', title="About")


@app.route("/Contact")
def contact():

    return render_template('contact.html', title="Contact")


@app.route("/Faq")
def faq():

    return render_template('faq.html', title="Faq")



@app.route('/confirm_delivery', methods=['POST'])
def confirm_delivery():
    # Get the order and pickup IDs from the form data
    pickup_id = request.form.get("pickup_id")
    order_id = request.form.get("order_id")
    image_file = request.files.get("delivery_image")

    # Query the relevant Pickup record
    pickup = Pickup.query.get(pickup_id)
    if not pickup:
        flash("Pickup not found.", "danger")
        return redirect(url_for('courier_orders'))

    # Query all OrderItems related to this order_id via the pickup_orderitem association
    order_items = (OrderItem.query
                   .filter_by(order_id=order_id)
                   .filter(OrderItem.status != "Cancelled")  # Exclude Cancelled
                   .all())

    # Query the related Order for the total amount
    order = Order.query.get(order_id)

    # Save the delivery image as binary data if it exists
    if image_file:
        delivery_image = image_file.read()  # Store binary image data in delivery_image variable

    # Query all pickups associated with the same order items (by their order_id)
    pickups = Pickup.query.join(pickup_orderitem).join(OrderItem).filter(OrderItem.order_id == order_id).all()

    delivery_time = datetime.utcnow()

    # Update the status and image for all related Pickup records
    for pickup in pickups:
        pickup.status = "Delivered"
        pickup.delivered_at = delivery_time 
        if image_file:  # Only update the image if a new image is provided
            pickup.delivery_image = delivery_image

    # Track which sellers' shipping fees have been processed
    # processed_sellers = set()

    # Update the status of all related OrderItems to "Delivered" and calculate seller income
    for order_item in order_items:
        order_item.status = "Delivered"
        
        # Check if we need to add the shipping fee for this seller
        # if order_item.seller_id not in processed_sellers:
        #     seller_shipping_fee = 45  # Assuming $45 per seller, adjust as needed
        #     order_item.update_seller_income(seller_shipping_fee)
        #     processed_sellers.add(order_item.seller_id)
        # else:
            # Call without adding the shipping fee again for the same seller
            # order_item.update_seller_income(0)

    # Commit the changes to the database
    db.session.commit()

    # Flash success message
    flash("Delivery confirmed successfully.", "success")

    # Redirect to courier orders page
    return redirect(url_for('courier_orders'))




@app.route('/confirm_order_received', methods=['POST'])
def confirm_order_received():
    order_id = request.form.get("order_id")

    if not order_id:
        flash("Order ID is required.", "danger")
        return redirect(url_for("user_Completed"))

    # Fetch all order items related to this order
    order_items = (OrderItem.query
                   .filter_by(order_id=order_id)
                   .filter(OrderItem.status != "Cancelled")  # Exclude Cancelled
                   .all())
    
    if not order_items:
        flash("No order items found for the provided order ID.", "danger")
        return redirect(url_for("user_Completed"))

    # Ensure all items are in "Delivered" status
    undelivered_items = [item for item in order_items if item.status != "Delivered"]
    if undelivered_items:
        flash("Not all items in the order are delivered yet.", "danger")
        return redirect(url_for("user_Completed"))

    # Track which sellers' shipping fees have been processed
    processed_sellers = set()

    # Update the status of all related OrderItems to "Received" and calculate seller/admin income
    for order_item in order_items:
        # Avoid processing already cancelled items (although they should already be excluded)
        if order_item.status == "Cancelled":
            continue

        # Check if we need to add the shipping fee for this seller
        if order_item.seller_id not in processed_sellers:
            seller_shipping_fee = 45  # Assuming $45 per seller, adjust as needed
            order_item.update_seller_income(seller_shipping_fee)
            processed_sellers.add(order_item.seller_id)
        else:
            # Call without adding the shipping fee again for the same seller
            order_item.update_seller_income(0)

        # Mark the item as "Received"
        order_item.status = "Received"

    db.session.commit()  # Commit changes to the database
    flash("Order received successfully.", "success")

    return redirect(url_for("user_Completed"))






@app.route('/submit_review/<int:product_id>', methods=['POST'])
@login_required
def submit_review(product_id):
    # Retrieve form data
    rating = request.form.get('rating')
    title = request.form.get('title')
    content = request.form.get('content')
    uploaded_files = request.files.getlist('images')  # Get the list of uploaded files

    # Print debug information about the uploaded files
    print(f"Uploaded files: {uploaded_files}")
    for file in uploaded_files:
        print(f"File: {file.filename}, Content-Type: {file.content_type}")

    # Validate rating (ensure it's between 1 and 5)
    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            raise ValueError("Invalid rating value")
    except ValueError:
        flash("Rating must be an integer between 1 and 5.", "danger")
        return redirect(url_for('user_received'))

    # Check if the user has already reviewed the product
    existing_review = Review.query.filter_by(product_id=product_id, user_id=current_user.id).first()

    if existing_review:
        # Update the existing review
        existing_review.rating = rating
        existing_review.title = title
        existing_review.content = content

        # Handle image deletion and upload
        if uploaded_files and any(file for file in uploaded_files if file.filename):
            # Remove existing images only if new images are uploaded
            for image in existing_review.images:  # Assuming Review has a relationship with ReviewImage
                db.session.delete(image)
                # Optionally delete from filesystem
                image_path = os.path.join(app.root_path, 'static/profile_pics', image.image_path)
                print(f"Deleting image at path: {image_path}")
                if os.path.exists(image_path):
                    os.remove(image_path)

            # Process new images
            for file in uploaded_files:
                if file and file.filename:
                    filename = save_picture(file)
                    new_image = ReviewImage(review_id=existing_review.id, image_path=filename)
                    db.session.add(new_image)

        db.session.commit()
        flash("Review updated successfully!", "success")
    else:
        # Create a new review
        review = Review(
            product_id=product_id,
            user_id=current_user.id,
            rating=rating,
            title=title,
            content=content,
            verified_purchase=True
        )
        db.session.add(review)
        db.session.flush()  # Flush to get the review ID for associating images

        # Process uploaded images
        if uploaded_files:
            for file in uploaded_files:
                if file and file.filename:
                    filename = save_picture(file)
                    new_image = ReviewImage(review_id=review.id, image_path=filename)
                    db.session.add(new_image)

        db.session.commit()
        flash("Review submitted successfully!", "success")

    return redirect(url_for('user_received'))





@app.route('/seller/<int:seller_id>')
def seller_page(seller_id):
    seller = Seller.query.get_or_404(seller_id)
    products = Product.query.filter_by(seller_id=seller_id).all()

    # Dictionary to store the average ratings for each product
    product_avg_ratings = {}
    # Dictionary to store reviews for each product
    product_reviews = {}

    # List to store all ratings for calculating seller rating
    all_seller_reviews = []

    # Loop through each product to calculate the average rating and gather reviews
    for product in products:
        # Assuming you have a 'reviews' relationship on the Product model
        reviews = product.reviews
        product_reviews[product.id] = reviews  # Storing reviews for each product
        
        if reviews:
            average_rating = sum([review.rating for review in reviews]) / len(reviews)
            # Add each review's rating to the seller's reviews list
            all_seller_reviews.extend([review.rating for review in reviews])
        else:
            average_rating = 0
        
        product_avg_ratings[product.id] = average_rating

    # Calculate seller's average rating
    if all_seller_reviews:
        seller_avg_rating = sum(all_seller_reviews) / len(all_seller_reviews)
    else:
        seller_avg_rating = 0

    return render_template(
        'seller_home.html', 
        seller=seller, 
        products=products, 
        product_avg_ratings=product_avg_ratings, 
        product_reviews=product_reviews, 
        seller_avg_rating=seller_avg_rating  # Passing seller's average rating
    )





# from datetime import datetime

# from datetime import datetime
# from flask import request, jsonify
# from sqlalchemy import extract, func

@app.route('/sales-data')
def sales_data():
    # Retrieve filter parameters from the request (query string)
    start_date_str = request.args.get('start_date', None)  # Optional start date filter
    end_date_str = request.args.get('end_date', None)  # Optional end date filter
    
    # Debugging: Print filter parameters
    print(f"Start Date: {start_date_str}, End Date: {end_date_str}")

    # Parse start and end dates if provided
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

    # Debugging: Print parsed dates
    print(f"Parsed Start Date: {start_date}, Parsed End Date: {end_date}")

    # Start building the query
    query = db.session.query(
        extract('year', Order.date_created).label('year'),
        extract('month', Order.date_created).label('month'),
        (func.sum(OrderItem.price * OrderItem.quantity) * 0.95).label('revenue')  # Calculate revenue with 5% commission
    ).join(OrderItem, OrderItem.order_id == Order.id).filter(
        OrderItem.seller_id == current_user.seller.id,  # Filter by seller ID
        OrderItem.status == 'Received'  # Only include orders with status 'Received'
    )

    # Apply additional filters based on date range if provided
    if start_date:
        query = query.filter(Order.date_created >= start_date)
    if end_date:
        query = query.filter(Order.date_created <= end_date)

    # Group and order the data
    results = query.group_by('year', 'month').order_by('year', 'month').all()

    # Format results into chart data
    revenue_data = {}
    for year, month, revenue in results:
        year = int(year)
        month = int(month)
        if year not in revenue_data:
            revenue_data[year] = [0] * 12
        revenue_data[year][month - 1] = round(float(revenue), 2)  # Month is 1-indexed

    # Prepare data for ApexCharts
    categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    series = [
        {"name": str(year), "data": revenue_data[year]}
        for year in sorted(revenue_data.keys())
    ]

    # Return the data in JSON format for the front-end
    return jsonify({"categories": categories, "series": series})






@app.route('/order-statistics')
def order_statistics():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User not authenticated'}), 401  # Handle unauthenticated user
    
    # Query to get total sales per order category
    results = (
        db.session.query(
            Product.category.label('category'),  # Getting category from Product model
            func.count(OrderItem.id).label('order_count'),  # Count the number of orders per category
            func.sum(OrderItem.price * OrderItem.quantity).label('total_sales')
        )
        .join(OrderItem, OrderItem.product_id == Product.id)  # Join OrderItem and Product
        .join(Order, Order.id == OrderItem.order_id)  # Join Order and OrderItem
        .filter(OrderItem.seller_id == current_user.seller.id)  # Filter by current seller
        .filter(OrderItem.status != 'Cancelled')  # Exclude cancelled orders
        .group_by(Product.category)  # Group by Product category
        .all()  # Execute the query
    )
    
    # If no results, return empty arrays
    if not results:
        return jsonify({'categories': [], 'sales': [], 'order_counts': []})
    
    # Prepare the data for the chart
    categories = []
    sales = []
    order_counts = []  # Store the order counts as well

    for category, order_count, total_sales in results:
        categories.append(category)
        sales.append(float(total_sales) if total_sales is not None else 0)
        order_counts.append(order_count)

    print("Categories:", categories)
    print("Sales:", sales)
    print("Order Counts:", order_counts)

    return jsonify({
        'categories': categories,
        'sales': sales,
        'order_counts': order_counts
    })





@app.route('/admin-profit-data')
def admin_profit_data():
    # Retrieve filter parameters from the request (query string)
    start_date_str = request.args.get('start_date', None)  # Optional start date filter
    end_date_str = request.args.get('end_date', None)  # Optional end date filter
    
    # Debugging: Print filter parameters
    print(f"Start Date: {start_date_str}, End Date: {end_date_str}")

    # Parse start and end dates if provided
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str else None

    # Debugging: Print parsed dates
    print(f"Parsed Start Date: {start_date}, Parsed End Date: {end_date}")

    # Start building the query
    query = db.session.query(
        extract('year', Order.date_created).label('year'),
        extract('month', Order.date_created).label('month'),
        (func.sum(OrderItem.price * OrderItem.quantity) * 0.05).label('profit')  # Admin's profit (5%)
    ).join(OrderItem, OrderItem.order_id == Order.id).filter(
        OrderItem.status == 'Received'  # Only include orders with status 'Received'
    )

    # Apply additional filters based on date range if provided
    if start_date:
        query = query.filter(Order.date_created >= start_date)
    if end_date:
        query = query.filter(Order.date_created <= end_date)

    # Group and order the data
    results = query.group_by('year', 'month').order_by('year', 'month').all()

    # Format results into chart data
    profit_data = {}
    for year, month, profit in results:
        year = int(year)
        month = int(month)
        if year not in profit_data:
            profit_data[year] = [0] * 12
        profit_data[year][month - 1] = round(float(profit), 2)  # Month is 1-indexed

    # Prepare data for ApexCharts
    categories = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    series = [
        {"name": str(year), "data": profit_data[year]}
        for year in sorted(profit_data.keys())
    ]

    # Return the data in JSON format for the front-end
    return jsonify({"categories": categories, "series": series})



@app.route('/monthly-shipping-income')
def monthly_shipping_income():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User not authenticated'}), 401

    # Query to calculate shipping income for each month of the current year
    current_year = datetime.utcnow().year
    results = (
        db.session.query(
            extract('month', Order.date_created).label('month'),
            (func.count(func.distinct(Order.id)) * 45).label('shipping_income')  # Apply fee only once per distinct order
        )
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(
            OrderItem.status == 'Received',  # Include only completed orders
            extract('year', Order.date_created) == current_year  # Filter by the current year
        )
        .group_by('month')
        .order_by('month')
        .all()
    )

    # Format the results
    monthly_income = [0] * 12  # Initialize an array for all months
    for month, income in results:
        monthly_income[int(month) - 1] = float(income)  # Assign income to the correct month

    return jsonify({
        "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        "series": [{"data": monthly_income}]
    })



@app.route('/monthly-deliveries')
def monthly_deliveries():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User not authenticated'}), 401

    # Ensure the current user is a courier
    if not hasattr(current_user, 'courier') or current_user.courier is None:
        return jsonify({'error': 'User is not a courier'}), 403

    # Get the courier ID
    courier_id = current_user.courier.id

    # Query to count deliveries completed by the courier for each month of the current year
    current_year = datetime.utcnow().year

    results = (
        db.session.query(
            extract('month', Order.date_created).label('month'),
            func.count(OrderItem.id).label('delivery_count')  # Count of delivered OrderItems (not just Orders)
        )
        .join(OrderItem, OrderItem.order_id == Order.id)  # Join OrderItem to ensure status is included
        .filter(
            Order.courier_id == courier_id,  # Filter orders assigned to this courier
            OrderItem.status == 'Delivered',  # Include only delivered order items
            extract('year', Order.date_created) == current_year  # Filter by the current year
        )
        .group_by('month')  # Group by month
        .order_by('month')  # Order results by month for chronological order
        .all()
    )

    # Format the results into a list, ensuring that each index corresponds to the correct month
    monthly_deliveries = [0] * 12  # Initialize an array with 12 zeros (one for each month)
    for month, count in results:
        monthly_deliveries[int(month) - 1] = int(count)  # Assign count to the correct month (1-12)

    return jsonify({
        "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        "series": [{"data": monthly_deliveries}]
    })






@app.route('/monthly-courier-income')
def monthly_courier_income():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User not authenticated'}), 401

    # Ensure the current user is a courier
    if not hasattr(current_user, 'courier') or current_user.courier is None:
        return jsonify({'error': 'User is not a courier'}), 403

    # Get the courier ID
    courier_id = current_user.courier.id

    # Query to calculate courier's monthly income for the current year
    current_year = datetime.utcnow().year
    results = (
        db.session.query(
            extract('month', Order.date_created).label('month'),
            (func.count(func.distinct(Order.id)) * 45 * 0.40).label('courier_income')  # 10% of the shipping fee per order
        )
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(
            Order.courier_id == courier_id,  # Filter orders assigned to this courier
            OrderItem.status == 'Delivered',  # Include only delivered orders
            extract('year', Order.date_created) == current_year  # Filter by the current year
        )
        .group_by('month')
        .order_by('month')
        .all()
    )

    # Format the results
    monthly_income = [0] * 12  # Initialize an array for all months
    for month, income in results:
        monthly_income[int(month) - 1] = float(income)  # Assign income to the correct month

    return jsonify({
        "categories": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        "series": [{"data": monthly_income}]
    })



@app.route('/admin/ban_user/<int:user_id>', methods=['POST'])
def ban_user_route(user_id):
    user = Users.query.get_or_404(user_id)
    reason = request.form.get('ban_reason')
    user.is_banned = True
    user.ban_reason = reason
    db.session.commit()

    try:
        subject = "Account Banned Notification"
        body = (
            f"Dear {user.first_name} {user.last_name},\n\n"
            f"We regret to inform you that your account has been banned.\n"
            f"Reason: {reason if reason else 'No specific reason provided.'}\n\n"
            f"If you believe this was done in error, please contact our support team.\n\n"
            f"Regards, SheWear Team"
        )
        msg = Message(subject, recipients=[user.email], body=body)
        mail.send(msg)
        flash(f'{user.first_name} {user.last_name} has been banned and notified via email.', 'success')

    except Exception as e:
        flash(f'User banned, but an error occurred while sending the email: {str(e)}', 'danger')

    
    return redirect(url_for('manage_user'))



@app.route("/admin/unban_user/<int:user_id>", methods=['POST'])
@login_required
@role_required('admin')
def unban_user(user_id):
    # Fetch the user by ID
    user = Users.query.get_or_404(user_id)

    # Unban the user
    user.is_banned = False
    user.ban_reason = None  # Optionally, clear the ban reason as well

    db.session.commit()

    try:
        subject = "Welcome Back: Your Account Has Been UnBanned"
        body = (
            f"Dear {user.first_name} {user.last_name},\n\n"
            f"We’re excited to inform you that your account has been UnBanned, and you now have full access to our platform.\n\n"
            f"We appreciate your patience and understanding during this time. Should you have any questions or require assistance, please don’t hesitate to reach out to our support team.\n\n"
            f"Thank you for being a valued member of our community.\n\n"
            f"Warm regards,\n"
            f"The SheWear Team"
        )
        msg = Message(subject, recipients=[user.email], body=body)
        mail.send(msg)
        flash(f'{user.first_name} {user.last_name} has been unbanned and notified via email.', 'success')
    except Exception as e:
        flash(f'User unbanned, but an error occurred while sending the email: {str(e)}', 'danger')

    # flash(f'{user.first_name} {user.last_name} has been unbanned.', 'success')
    return redirect(url_for('manage_user'))  # Redirect to the user management page




# from datetime import datetime, timedelta

@app.route('/seller/finance', methods=['GET', 'POST'])
@role_required('seller')
@login_required
def seller_finance():
    # Get current date information
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_week = datetime.now().isocalendar()[1]

    seller_id = current_user.seller.id

    # Get start_date and end_date from query params
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    # Base query to get order items for Delivered status
    query_delivered = db.session.query(
        OrderItem, Order, Pickup
    ).join(Order).join(pickup_orderitem).join(Pickup).filter(
        OrderItem.seller_id == seller_id,
        OrderItem.status == 'Delivered'
    )

    # Base query to get order items for Received status
    query_received = db.session.query(
        OrderItem, Order, Pickup
    ).join(Order).join(pickup_orderitem).join(Pickup).filter(
        OrderItem.seller_id == seller_id,
        OrderItem.status == 'Received'
    )


    # Apply start_date and end_date filters for Delivered orders
    start_date_obj = parse_date(start_date, default_hour=0, default_minute=0, default_second=0)
    end_date_obj = parse_date(end_date, default_hour=23, default_minute=59, default_second=59)

    if start_date_obj:
        query_delivered = query_delivered.filter(Pickup.delivered_at >= start_date_obj)
        query_received = query_received.filter(Pickup.delivered_at >= start_date_obj)

    if end_date_obj:
        query_delivered = query_delivered.filter(Pickup.delivered_at <= end_date_obj)
        query_received = query_received.filter(Pickup.delivered_at <= end_date_obj)
    # Execute both queries
    orders_delivered = query_delivered.all()
    orders_received = query_received.all()

    # Total deductions for Delivered orders (5% of the price * quantity)
    delivered_total_with_deduction = db.session.query(
        func.sum(OrderItem.price * OrderItem.quantity * 0.95)
    ).filter(
        OrderItem.seller_id == seller_id,
        OrderItem.status == 'Delivered'
    ).scalar()

    # Total release amounts for Received orders (5% of the price * quantity)
    release_total = db.session.query(
        func.sum(OrderItem.price * OrderItem.quantity * 0.95)
    ).filter(
        OrderItem.seller_id == seller_id,
        OrderItem.status == 'Received'
    ).scalar()

    # Total release amounts for Received orders in the current week
    release_total_week = db.session.query(
        func.sum(OrderItem.price * OrderItem.quantity * 0.95)
    ).join(Order).filter(
        OrderItem.seller_id == seller_id,
        OrderItem.status == 'Received',
        func.extract('year', Order.date_created) == current_year,
        func.extract('week', Order.date_created) == current_week
    ).scalar()

    # Total release amounts for Received orders in the current month
    release_total_month = db.session.query(
        func.sum(OrderItem.price * OrderItem.quantity * 0.95)
    ).join(Order).filter(
        OrderItem.seller_id == seller_id,
        OrderItem.status == 'Received',
        func.extract('year', Order.date_created) == current_year,
        func.extract('month', Order.date_created) == current_month
    ).scalar()

    # Return the rendered template with the necessary data
    return render_template('seller_finance.html',
                           title="Seller Finance",
                           delivered_total=delivered_total_with_deduction,
                           release_total=release_total,
                           release_total_month=release_total_month,
                           release_total_week=release_total_week,
                           orders_delivered=orders_delivered,
                           orders_received=orders_received)






# Helper function to convert date string to datetime object
def parse_date(date_str, default_hour=0, default_minute=0, default_second=0):
    if date_str:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.replace(hour=default_hour, minute=default_minute, second=default_second, microsecond=0)
    return None

@app.route('/admin/finance', methods=['GET', 'POST'])
@role_required('admin')
@login_required
def admin_finance():
    # Get current date details (used elsewhere in the code)
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_week = datetime.now().isocalendar()[1]

    # Get start_date and end_date from query params
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    print(f"PINAKA BABA Start Date: {start_date}, End Date: {end_date}")

    # Base query to get order items for Delivered status (for all sellers)
    query_delivered = db.session.query(
        OrderItem, Order, Pickup, Seller
    ).join(Order).join(pickup_orderitem).join(Pickup).join(OrderItem.product).join(Product.seller).filter(OrderItem.status == 'Delivered')

    # Base query to get order items for Received status (for all sellers)
    query_received = db.session.query(
        OrderItem, Order, Pickup, Seller
    ).join(Order).join(pickup_orderitem).join(Pickup).join(OrderItem.product).join(Product.seller).filter(OrderItem.status == 'Received')

    # Apply date filters based on start_date and end_date for Delivered orders
    start_date_obj = parse_date(start_date, default_hour=0, default_minute=0, default_second=0)
    end_date_obj = parse_date(end_date, default_hour=23, default_minute=59, default_second=59)

    if start_date_obj:
        query_delivered = query_delivered.filter(Pickup.delivered_at >= start_date_obj)
        query_received = query_received.filter(Pickup.delivered_at >= start_date_obj)

    if end_date_obj:
        query_delivered = query_delivered.filter(Pickup.delivered_at <= end_date_obj)
        query_received = query_received.filter(Pickup.delivered_at <= end_date_obj)

    # Execute both queries
    orders_delivered = query_delivered.all()
    orders_received = query_received.all()

    # Total deductions for Delivered orders (5% of the price * quantity)
    total_deduction = db.session.query(
        func.sum(OrderItem.price * OrderItem.quantity * 0.05)
    ).filter(
        OrderItem.status == 'Delivered'
    ).scalar()

    # Total shipping costs for Delivered orders (45 per unique order)
    total_shipping_pending = db.session.query(
        func.count(func.distinct(OrderItem.order_id)) * 45
    ).join(OrderItem.order).filter(
        OrderItem.status == 'Delivered'
    ).scalar()

    # Total shipping costs for Received orders in the current week
    total_shipping_pending_week = db.session.query(
        func.count(func.distinct(OrderItem.order_id)) * 45
    ).join(OrderItem.order).filter(
        OrderItem.status == 'Received',
        func.extract('year', Order.date_created) == current_year,
        func.extract('week', Order.date_created) == current_week
    ).scalar()

    # Total shipping costs for Received orders in the current month
    total_shipping_pending_month = db.session.query(
        func.count(func.distinct(OrderItem.order_id)) * 45
    ).join(OrderItem.order).filter(
        OrderItem.status == 'Received',
        func.extract('year', Order.date_created) == current_year,
        func.extract('month', Order.date_created) == current_month
    ).scalar()

    # Total shipping costs for Received orders (all time)
    total_shipping_total = db.session.query(
        func.count(func.distinct(OrderItem.order_id)) * 45
    ).join(OrderItem.order).filter(
        OrderItem.status == 'Received'
    ).scalar()

    # Total release amounts (5% of the price * quantity) for Received orders in the current week
    release_total_week = db.session.query(
        func.sum(OrderItem.price * OrderItem.quantity * 0.05)
    ).join(Order).filter(
        OrderItem.status == 'Received',
        func.extract('year', Order.date_created) == current_year,
        func.extract('week', Order.date_created) == current_week
    ).scalar()

    # Total release amounts for Received orders in the current month
    release_total_month = db.session.query(
        func.sum(OrderItem.price * OrderItem.quantity * 0.05)
    ).join(Order).filter(
        OrderItem.status == 'Received',
        func.extract('year', Order.date_created) == current_year,
        func.extract('month', Order.date_created) == current_month
    ).scalar()

    # Total release amounts for Received orders (all time)
    release_total = db.session.query(
        func.sum(func.coalesce(OrderItem.price, 0) * func.coalesce(OrderItem.quantity, 0) * 0.05)
    ).filter(
        OrderItem.status == 'Received'
    ).scalar()

    # Render the template with the calculated values
    return render_template('admin_finance.html',
                           total_deduction=total_deduction,
                           release_total_week=release_total_week,
                           release_total_month=release_total_month,
                           release_total=release_total,
                           total_shipping_pending=total_shipping_pending,
                           total_shipping_pending_week=total_shipping_pending_week,
                           total_shipping_pending_month=total_shipping_pending_month,
                           total_shipping_total=total_shipping_total,
                           orders_delivered=orders_delivered,
                           orders_received=orders_received)


# from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph,Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.ttfonts import TTFont




@app.route('/export_orders', methods=['GET'])
def export_orders():
    # Get the start and end dates from query parameters
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    # Fetch the data
    seller_id = current_user.seller.id
    seller = current_user.seller
    shop_name = seller.shop_name 
    first_name = seller.user.first_name  
    last_name = seller.user.last_name
    category = seller.category
    province = seller.province
    city = seller.city
    barangay = seller.barangay
    street = seller.street
    postal_code = seller.postal_code

    query_delivered = db.session.query(OrderItem, Order, Pickup).join(Order).join(pickup_orderitem).join(Pickup).filter(
        OrderItem.seller_id == seller_id,
        OrderItem.status == 'Delivered'
    )

    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        start_date_obj = start_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        query_delivered = query_delivered.filter(Pickup.delivered_at >= start_date_obj)

    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
        query_delivered = query_delivered.filter(Pickup.delivered_at <= end_date_obj)

    orders_delivered = query_delivered.all()

    # Prepare the PDF document
    output = BytesIO()
    pdf = SimpleDocTemplate(output, pagesize=landscape(letter), title="Delivered Report")

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Normal']
    

    logo_path = 'app/static/img/18.png'  # Replace with the path to your logo image
    logo = Image(logo_path, width=150, height=75)  # Adjust size as needed
    logo.hAlign = 'CENTER'  # Align the logo to the center

    
    # Add date range details
    if start_date and end_date:
        date_range = f"From: {datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d, %Y')} To: {datetime.strptime(end_date, '%Y-%m-%d').strftime('%B %d, %Y')}"
    elif start_date:
        date_range = f"From: {datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d, %Y')}"
    elif end_date:
        date_range = f"Up To: {datetime.strptime(end_date, '%Y-%m-%d').strftime('%B %d, %Y')}"
    else:
        date_range = "All Time"

    # Report Description
    report_description = Paragraph(f"""
    This report provides a detailed overview of the sales performance for the specified period <b>{date_range}</b> 
    for the shop <b>{shop_name}</b>, managed by <b>{first_name} {last_name}</b>. 
    It focuses on the delivered orders, highlighting key metrics such as the total revenue generated, the number of items sold, and the profitability from each sale. 
    Operating in the <b>{category.replace("_", " & ")}</b> category, <b>{shop_name}</b> is located at <b>{street}, {barangay}, {city}, {province}, {postal_code}</b>. 
    By evaluating the sales data alongside this information, the report aims to provide valuable insights into the shop's performance, uncovering trends, and identifying 
    opportunities for optimizing future operations and business strategies.
    """, subtitle_style)

    report_description.alignment = 1  # Center-align the report description
    report_description.spaceAfter = 15

        
    title_style.alignment = 1  
    title = Paragraph("Delivered Orders Report", title_style)

    # Table data with additional columns for Original Price, Deduction (5%), and Profit
    table_data = [[
        'ID', 'Product', 'Category', 'Color', 'Size', 'Price', 'Commission (5%)', 'Profit', 'Buyer', 'Delivered At'
    ]]

    # Populate table rows
    for order_item, order, pickup in orders_delivered:
        product_name = order_item.product.name
        product_category = order_item.product.category
        order_id = order.id
        original_price = order_item.price
        deduction = original_price * 0.05
        profit = original_price - deduction
        user_name = f"{order.user.first_name} {order.user.last_name}"
        delivered_at = pickup.delivered_at.strftime('%B %d, %Y, %H:%M:%S') if pickup.delivered_at else "Not Delivered"

        # Retrieve color and size from OrderItem directly
        color = order_item.color if order_item.color else "Not Available"
        size = order_item.size if order_item.size else "Not Available"

        table_data.append([
            order_id, product_name, product_category, color, size, f"₱{original_price:.2f}", f"₱{deduction:.2f}", f"₱{profit:.2f}", user_name, delivered_at
        ])

    # Create table with styling
    table = Table(table_data, colWidths=[30, 90, 60, 50, 40, 60, 90, 70, 125, 138])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Add elements to the PDF
    elements = [logo, title, report_description, table]
    pdf.build(elements)

    # Return the PDF file as a response
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="delivered_orders_report.pdf", mimetype="application/pdf")





@app.route('/export_orders/admin', methods=['GET'])
def export_orders_admin():
    # Get the start and end dates from query parameters
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    # Query for delivered order items (admin scope)
    query_delivered = db.session.query(OrderItem, Order, Pickup).join(Order).join(pickup_orderitem).join(Pickup).filter(
        OrderItem.status == 'Delivered'
    )

    # Apply date filters if provided
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        start_date_obj = start_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        query_delivered = query_delivered.filter(Pickup.delivered_at >= start_date_obj)

    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
        query_delivered = query_delivered.filter(Pickup.delivered_at <= end_date_obj)

    orders_delivered = query_delivered.all()
    

    # Prepare the PDF document
    output = BytesIO()
    pdf = SimpleDocTemplate(output, pagesize=landscape(letter), title="Delivered Orders Report")

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Normal']

    logo_path = 'app/static/img/18.png'  # Replace with the path to your logo image
    logo = Image(logo_path, width=150, height=75)  # Adjust size as needed
    logo.hAlign = 'CENTER'  # Align the logo to the center

    # Title
    if start_date and end_date:
        date_range = f"From: {datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d, %Y')} To: {datetime.strptime(end_date, '%Y-%m-%d').strftime('%B %d, %Y')}"
    elif start_date:
        date_range = f"From: {datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d, %Y')}"
    elif end_date:
        date_range = f"Up To: {datetime.strptime(end_date, '%Y-%m-%d').strftime('%B %d, %Y')}"
    else:
        date_range = "All Time"
    report_description = Paragraph(f"""
    This report provides a detailed overview of the sales performance for the specified period <b>{date_range}</b>. 
    It focuses on the delivered orders, highlighting key metrics such as the total revenue generated, the number of items sold, and the profitability from each sale. 
    By evaluating the sales data, the report aims to provide valuable insights into overall performance, uncovering trends, and identifying 
    opportunities for optimizing future operations and business strategies.
    """, subtitle_style)
    report_description.alignment = 1  
    report_description.spaceAfter = 15


    title = Paragraph("Delivered Orders Report", title_style)
    title_style.alignment = 1  


    # Table data (same content as /export_orders)
    table_data = [[
        'ID', 'Product', 'Category', 'Color', 'Size', 'Price', 'Commission (5%)', 'Profit', 'Buyer', 'Delivered At'
    ]]

    # Populate table rows
    for order_item, order, pickup in orders_delivered:
        product_name = order_item.product.name
        product_category = order_item.product.category
        order_id = order.id
        original_price = order_item.price
        deduction = original_price * 0.05
        profit = original_price - deduction
        user_name = f"{order.user.first_name} {order.user.last_name}"
        delivered_at = pickup.delivered_at.strftime('%B %d, %Y, %H:%M:%S') if pickup.delivered_at else "Not Delivered"

        # Retrieve color and size from OrderItem directly
        color = order_item.color if order_item.color else "Not Available"
        size = order_item.size if order_item.size else "Not Available"

        table_data.append([
            order_id, product_name, product_category, color, size, f"₱{original_price:.2f}", f"₱{deduction:.2f}", f"₱{profit:.2f}", user_name, delivered_at
        ])

    # Create table with styling
    table = Table(table_data, colWidths=[30, 90, 60, 50, 40, 60, 90, 70, 125, 138])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Add elements to the PDF
    elements = [logo, title, report_description, table]
    pdf.build(elements)

    # Return the PDF file as a response
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="admin_delivered_orders_report.pdf", mimetype="application/pdf")



@app.route('/export_received_orders', methods=['GET'])
def export_received_orders():
    # Get the start and end dates from query parameters
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    # Fetch the data
    seller_id = current_user.seller.id
    seller = current_user.seller
    shop_name = seller.shop_name 
    first_name = seller.user.first_name  
    last_name = seller.user.last_name
    category = seller.category
    province = seller.province
    city = seller.city
    barangay = seller.barangay
    street = seller.street
    postal_code = seller.postal_code

    # Base query to get received order items
    query_received = db.session.query(OrderItem, Order, Pickup).join(Order).join(pickup_orderitem).join(Pickup).filter(
        OrderItem.seller_id == seller_id,
        OrderItem.status == 'Received'
    )

    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        start_date_obj = start_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        query_received = query_received.filter(Pickup.delivered_at >= start_date_obj)

    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
        query_received = query_received.filter(Pickup.delivered_at <= end_date_obj)

    orders_received = query_received.all()

    # Prepare the PDF document
    output = BytesIO()
    pdf = SimpleDocTemplate(output, pagesize=landscape(letter), title="Received Orders Report")

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Normal']

    
    logo_path = 'app/static/img/18.png'  # Replace with the path to your logo image
    logo = Image(logo_path, width=150, height=75)  # Adjust size as needed
    logo.hAlign = 'CENTER'  # Align the logo to the center

    
    # Add date range details
    if start_date and end_date:
        date_range = f"From: {datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d, %Y')} To: {datetime.strptime(end_date, '%Y-%m-%d').strftime('%B %d, %Y')}"
    elif start_date:
        date_range = f"From: {datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d, %Y')}"
    elif end_date:
        date_range = f"Up To: {datetime.strptime(end_date, '%Y-%m-%d').strftime('%B %d, %Y')}"
    else:
        date_range = "All Time"

    # Report Description
    report_description = Paragraph(f"""
    This report provides a detailed overview of the sales performance for the specified period <b>{date_range}</b> 
    for the shop <b>{shop_name}</b>, managed by <b>{first_name} {last_name}</b>. 
    It focuses on the delivered orders, highlighting key metrics such as the total revenue generated, the number of items sold, and the profitability from each sale. 
    Operating in the <b>{category.replace("_", " & ")}</b> category, <b>{shop_name}</b> is located at <b>{street}, {barangay}, {city}, {province}, {postal_code}</b>. 
    By evaluating the sales data alongside this information, the report aims to provide valuable insights into the shop's performance, uncovering trends, and identifying 
    opportunities for optimizing future operations and business strategies.
    """, subtitle_style)

    report_description.alignment = 1  # Center-align the report description
    report_description.spaceAfter = 15

    title = Paragraph("Received Orders Report", title_style)
    title_style.alignment = 1  
   
    # Table data with additional columns for Original Price, Deduction (5%), and Profit
    table_data = [[
        'ID', 'Product', 'Category', 'Color', 'Size', 'Price', 'Commission (5%)', 'Profit', 'Buyer', 'Delivered At'
    ]]

    # Populate table rows
    for order_item, order, pickup in orders_received:
        product_name = order_item.product.name
        product_category = order_item.product.category
        order_id = order.id
        original_price = order_item.price
        deduction = original_price * 0.05
        profit = original_price - deduction
        user_name = f"{order.user.first_name} {order.user.last_name}"
        delivered_at = pickup.delivered_at.strftime('%B %d, %Y, %H:%M:%S') if pickup.delivered_at else "Not Delivered"

        # Retrieve color and size from OrderItem directly
        color = order_item.color if order_item.color else "Not Available"
        size = order_item.size if order_item.size else "Not Available"

        table_data.append([
            order_id, product_name, product_category, color, size, f"{original_price:.2f}", f"{deduction:.2f}", f"{profit:.2f}", user_name, delivered_at
        ])

    # Create table with styling
    table = Table(table_data, colWidths=[30, 90, 60, 50, 40, 60, 90, 70, 125, 138])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Add elements to the PDF
    elements = [logo, title, report_description, table]
    pdf.build(elements)

    # Return the PDF file as a response
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="received_orders_report.pdf", mimetype="application/pdf")







@app.route('/export_orders/received/admin', methods=['GET'])
def export_orders_received_admin():
    # Get the start and end dates from query parameters
    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)
    
    # Query for received order items (Admin view - No seller filtering)
    query_received = db.session.query(OrderItem, Order, Pickup, Seller).join(Order).join(pickup_orderitem).join(Pickup).join(Seller).filter(
        OrderItem.status == 'Received'
    )

    # Apply date filters if provided
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        start_date_obj = start_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        query_received = query_received.filter(Pickup.delivered_at >= start_date_obj)

    if end_date:
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
        end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
        query_received = query_received.filter(Pickup.delivered_at <= end_date_obj)

    orders_received = query_received.all()

    # Prepare the PDF document
    output = BytesIO()
    pdf = SimpleDocTemplate(output, pagesize=landscape(letter), title="Admin Received Orders Report")

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Normal']

    logo_path = 'app/static/img/18.png'  # Replace with the path to your logo image
    logo = Image(logo_path, width=150, height=75)  # Adjust size as needed
    logo.hAlign = 'CENTER'  # Align the logo to the center

    # Title
    # Add date range details
    if start_date and end_date:
        date_range = f"From: {datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d, %Y')} To: {datetime.strptime(end_date, '%Y-%m-%d').strftime('%B %d, %Y')}"
    elif start_date:
        date_range = f"From: {datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d, %Y')}"
    elif end_date:
        date_range = f"Up To: {datetime.strptime(end_date, '%Y-%m-%d').strftime('%B %d, %Y')}"
    else:
        date_range = "All Time"

    report_description = Paragraph(f"""
    This report provides a detailed overview of the sales performance for the specified period <b>{date_range}</b>. 
    It focuses on the delivered orders, highlighting key metrics such as the total revenue generated, the number of items sold, and the profitability from each sale. 
    By evaluating the sales data, the report aims to provide valuable insights into overall performance, uncovering trends, and identifying 
    opportunities for optimizing future operations and business strategies.
    """, subtitle_style)
    report_description.alignment = 1  
    report_description.spaceAfter = 15

    # Title
    title = Paragraph("Admin Received Orders Report", title_style)
    title_style.alignment = 1  

    # Table data with additional columns for Original Price, Deduction (5%), and Profit
    table_data = [[
        'ID', 'Product', 'Category', 'Color', 'Size', 'Price', 'Commission (5%)', 'Profit', 'Buyer', 'Delivered At', 'Seller'
    ]]

    # Populate table rows
    for order_item, order, pickup, seller in orders_received:
        product_name = order_item.product.name
        product_category = order_item.product.category
        order_id = order.id
        original_price = order_item.price
        deduction = original_price * 0.05
        profit = original_price - deduction
        user_name = f"{order.user.first_name} {order.user.last_name}"
        delivered_at = pickup.delivered_at.strftime('%B %d, %Y, %H:%M:%S') if pickup.delivered_at else "Not Delivered"

        # Retrieve color and size from OrderItem directly
        color = order_item.color if order_item.color else "Not Available"
        size = order_item.size if order_item.size else "Not Available"

        table_data.append([
            order_id, product_name, product_category, color, size, f"₱{original_price:.2f}", f"₱{deduction:.2f}", f"₱{profit:.2f}", user_name, delivered_at, seller.shop_name
        ])

    # Create table with styling
    table = Table(table_data, colWidths=[20, 90, 55, 50, 35, 55, 90, 60, 115, 135,80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Add elements to the PDF
    elements = [logo, title, report_description, table]
    pdf.build(elements)

    # Return the PDF file as a response
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="admin_received_orders_report.pdf", mimetype="application/pdf")



# NEW CODE

# MESSAGE BOX
# ADMIN MESSAGE BOX (can contact all)
@app.route('/chat/<int:receiver_id>')
@login_required
@role_required('admin')
def chat(receiver_id):
    receiver = Users.query.get_or_404(receiver_id)  
    
    # Get all messages between current_user and the receiver
    messages = Messages.query.filter(
        ((Messages.sender_id == current_user.id) & (Messages.receiver_id == receiver_id)) |
        ((Messages.sender_id == receiver_id) & (Messages.receiver_id == current_user.id))
    ).order_by(Messages.timestamp).all()  

        # Mark messages as seen
    unseen_messages = [msg for msg in messages if msg.receiver_id == current_user.id and not msg.is_seen]
    for msg in unseen_messages:
        msg.is_seen = True
    db.session.commit()  # Commit the changes to mark messages as seen
    
    # Query users and order by the latest message with the current user, putting unread messages first
    # Query users and order by the latest message with the current user, putting unread messages first
    users = (Users.query.filter(Users.id != current_user.id)
            .outerjoin(
                Messages,
                ((Messages.sender_id == Users.id) & (Messages.receiver_id == current_user.id)) |
                ((Messages.receiver_id == Users.id) & (Messages.sender_id == current_user.id))
            )
            .order_by(
                db.desc(db.func.max(Messages.timestamp)),
                db.desc(db.func.sum(db.case((Messages.is_seen == False, 1), else_=0)))
            )
            .group_by(Users.id)
            .all())

    
    # Display a message if the current user has no image file
    if current_user.image_file is None:
        flash('Please upload a profile picture to continue.', 'warning')
        
    print("Current User ID:", current_user.id)
    print("Users Available:", users)
    return render_template('message_box.html', messages=messages, current_user=current_user, receiver=receiver, users=users)


@app.route('/send_message', methods=['POST'])
@role_required('admin')
def send_message():
    message_content = request.form.get('message').strip()
    receiver_id = request.form.get('receiver')
    file = request.files.get('file')  # Get the file from the form


    receiver = Users.query.get(receiver_id)
    if not receiver:
        flash("Receiver does not exist.")
        return redirect(url_for('chat', receiver_id=receiver_id))

    file_path = None
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid conflicts
        unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_CHAT_FOLDER'], unique_filename)
        file.save(file_path)  # Save the file to the specific directory

        # Store the relative file path for database storage
        file_path = f"{unique_filename}"



    if not message_content and not file:
        flash("Please enter a message or select a file to send.", 'warning')
        return redirect(url_for('chat', receiver_id=receiver_id))

    # Save message details in the database
    new_message = Messages(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        content=message_content or '',  # Avoid None content if no message text is provided
        file_path=file_path,  # Store the file path
        timestamp=datetime.now()
    )


    db.session.add(new_message)
    db.session.commit()


    return redirect(url_for('chat', receiver_id=receiver.id))


@app.route('/archive_message/<int:message_id>', methods=['POST'])
@role_required('admin')
def archive_message(message_id):
    # Get the message by its ID
    message = Messages.query.get_or_404(message_id)

    # Ensure that the current user is either the sender or the receiver of the message
    if message.sender_id != current_user.id and message.receiver_id != current_user.id:
        flash("You don't have permission to archive this message.")
        return redirect(url_for('chat', receiver_id=message.receiver_id))

    # Here, instead of deleting, we can archive the message by moving it to another table,
    # or just add a column like 'is_archived' to flag it as archived.
    message.is_archived = True  # Assume natin na you have an 'is_archived' column in your Message model

    db.session.commit()
    flash('Message archived successfully.','success')

    return redirect(url_for('chat', receiver_id=message.receiver_id))


# Fetch all the unread or unseen messages
@app.template_global()
def user_has_unread_message(user_id):
    return Messages.query.filter_by(sender_id=user_id, receiver_id=current_user.id, is_seen=False).count() > 0


# SELLER MESSAGEBOX (can contact admin and all user role except co-seller)
@app.route('/seller/chat/<int:receiver_id>')
@login_required
@role_required('seller')
def seller_chat(receiver_id):
    receiver = Users.query.get_or_404(receiver_id)  
    
    # Get all messages between current_user and the receiver
    messages = Messages.query.filter(
        ((Messages.sender_id == current_user.id) & (Messages.receiver_id == receiver_id)) |
        ((Messages.sender_id == receiver_id) & (Messages.receiver_id == current_user.id))
    ).order_by(Messages.timestamp).all()  

        # Mark messages as seen
    unseen_messages = [msg for msg in messages if msg.receiver_id == current_user.id and not msg.is_seen]
    for msg in unseen_messages:
        msg.is_seen = True
    db.session.commit()  # Commit the changes to mark messages as seen
    
    users = (Users.query.filter(Users.id != current_user.id)
            .outerjoin(
                Messages,
                ((Messages.sender_id == Users.id) & (Messages.receiver_id == current_user.id)) |
                ((Messages.receiver_id == Users.id) & (Messages.sender_id == current_user.id))
            )
            .order_by(
                db.desc(db.func.max(Messages.timestamp)),
                db.desc(db.func.sum(db.case((Messages.is_seen == False, 1), else_=0)))
            )
            .group_by(Users.id)
            .all())
    

    # Display a message if the current user has no image file
    if current_user.image_file is None:
        flash('Please upload a profile picture to continue.', 'warning')

    return render_template('seller_message_box.html', messages=messages, current_user=current_user, receiver=receiver, users=users)


@app.route('/seller_send_message', methods=['POST'])
def seller_send_message():
    message_content = request.form.get('message').strip()
    receiver_id = request.form.get('receiver')
    file = request.files.get('file')  # Get the file from the form

    receiver = Users.query.get(receiver_id)
    if not receiver:
        flash("Receiver does not exist.")
        return redirect(url_for('seller_chat', receiver_id=receiver_id))

    # Handle file upload
    file_path = None
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid conflicts
        unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_CHAT_FOLDER'], unique_filename)
        file.save(file_path)  # Save the file to the specific directory

        # Store the relative file path for database storage
        file_path = f"{unique_filename}"


    if not message_content and not file:
        flash("Please enter a message or select a file to send.", 'warning')
        return redirect(url_for('seller_chat', receiver_id=receiver_id))

    # Save message details in the database
    new_message = Messages(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        content=message_content or '',  # Avoid None content if no message text is provided
        file_path=file_path,  # Store the file path
        timestamp=datetime.now()
    )

    db.session.add(new_message)
    db.session.commit()


    return redirect(url_for('seller_chat', receiver_id=receiver.id))


@app.route('/seller/archive_message/<int:message_id>', methods=['POST'])
@role_required('seller')
def seller_archive_message(message_id):
    # Get the message by its ID
    message = Messages.query.get_or_404(message_id)

    if message.sender_id != current_user.id and message.receiver_id != current_user.id:
        flash("You don't have permission to archive this message.")
        return redirect(url_for('seller_chat', receiver_id=message.receiver_id))

    message.is_archived = True  

    db.session.commit()
    flash('Message archived successfully.', 'success')


    return redirect(url_for('seller_chat', receiver_id=message.receiver_id))


# USER MESSAGE BOX (can contact admin and all seller except co-user role)
@app.before_request
def load_unseen_message_count():
    if current_user.is_authenticated:
        g.unseen_message_count = Messages.query.filter_by(receiver_id=current_user.id, is_seen=False).count()
    else:
        g.unseen_message_count = 0


@app.route('/get_unseen_message_count')
def get_unseen_message_count():
    unseen_message_count = g.unseen_message_count  # Adjust this to get the actual unseen count from your logic
    return jsonify(unseen_message_count=unseen_message_count)


@app.route('/user/chat/<int:receiver_id>/', methods=['GET', 'POST'])
@login_required
@role_required('user')
def user_chat(receiver_id):
    receiver = Users.query.get_or_404(receiver_id)
    if not receiver:
        return jsonify({"error": "Receiver not found"}), 404

    messages = Messages.query.filter(
        ((Messages.sender_id == current_user.id) & (Messages.receiver_id == receiver_id)) |
        ((Messages.sender_id == receiver_id) & (Messages.receiver_id == current_user.id))
    ).order_by(Messages.timestamp).all()

    # Mark messages as seen
    unseen_messages = [msg for msg in messages if msg.receiver_id == current_user.id and not msg.is_seen]
    for msg in unseen_messages:
        msg.is_seen = True
    db.session.commit()

    users = (Users.query.filter(Users.id != current_user.id)
            .outerjoin(
                Messages,
                ((Messages.sender_id == Users.id) & (Messages.receiver_id == current_user.id)) |
                ((Messages.receiver_id == Users.id) & (Messages.sender_id == current_user.id))
            )
            .order_by(
                db.desc(db.func.max(Messages.timestamp)),
                db.desc(db.func.sum(db.case((Messages.is_seen == False, 1), else_=0)))
            )
            .group_by(Users.id)
            .all())

    return render_template(
        'user_messagebox.html',
        messages=messages,
        receiver=receiver,
        current_user=current_user,
        users=users
    )


@app.route('/user/send_message', methods=['POST'])
@role_required('user')
def user_send_message():
    message_content = request.form.get('message').strip()
    receiver_id = request.form.get('receiver')
    file = request.files.get('file')  # Get the file from the form

    receiver = Users.query.get(receiver_id)
    if not receiver:
        flash("Receiver does not exist.")
        return redirect(url_for('user_chat', receiver_id=receiver_id))
    
    # Handle file upload
    file_path = None
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid conflicts
        unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_CHAT_FOLDER'], unique_filename)
        file.save(file_path)  # Save the file to the specific directory

        # Store the relative file path for database storage
        file_path = f"{unique_filename}"

        # Ensure at least message content or file is present
    if not message_content and not file:
        flash("Please enter a message or select a file to send.", 'warning')
        return redirect(url_for('user_chat', receiver_id=receiver_id))

    # Save message details in the database
    new_message = Messages(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        content=message_content,  # Avoid None content if no message text is provided
        file_path=file_path,  # Store the file path
        timestamp=datetime.now()
    )


    db.session.add(new_message)
    db.session.commit()

    return redirect(url_for('user_chat', receiver_id=receiver.id))


@app.route('/user/archive_message/<int:message_id>', methods=['POST'])
@role_required('user')
def user_archive_message(message_id):
    # Get the message by its ID
    message = Messages.query.get_or_404(message_id)

    # Ensure that the current user is either the sender or the receiver of the message
    if message.sender_id != current_user.id and message.receiver_id != current_user.id:
        flash("You don't have permission to archive this message.", 'danger')  # Flash error message if no permission
        return redirect(url_for('user_chat', receiver_id=message.receiver_id))

    # Archive the message by setting the 'is_archived' flag
    message.is_archived = True  # Assuming you have an 'is_archived' column in your Message model

    db.session.commit()
    flash('Message archived successfully.', 'success')  
    return redirect(url_for('user_chat', receiver_id=message.receiver_id))



# Use to send picture
@app.context_processor
def inject_user_images():
    # Provide a helper function to get the profile image URL for each user
    def get_user_image(user):
        if user.image_file:
            return url_for('static', filename=f'profile_pics/{user.image_file}')
        return url_for('static', filename='profile_pics/default.jpg')

    return dict(get_user_image=get_user_image)
# END OF MESSAGE BOX CODE 

# FOR NOTIFICATION
# Admin view for notification
@app.route('/notifications')
@login_required
def view_notifications():
    # Fetch all active notifications, joining with the related Product for detailed info
    notifications = db.session.query(Notification).join(Product).filter(
        Notification.is_active == True
    ).all()

    notifications = db.session.query(Notification).filter(
        Notification.is_active == True
    ).all()
    return render_template('notification.html', notifications=notifications)


@app.route('/layout')
def layout():
    notifications = StockNotification.query.filter_by(seller_id=current_user.seller.id).all()
    return render_template('layout.html', notifications=notifications)


@app.route('/get_seller_notifications', methods=['GET'])
@login_required
def get_seller_notifications() -> Dict[str, List[Dict[str, str]]]:
    if current_user.role != 'seller':
        return jsonify({"error": "Unauthorized"}), 403

    notifications = StockNotification.query.filter_by(seller_id=current_user.seller.id).order_by(
        StockNotification.seen.asc(), StockNotification.date.desc()
    ).all()

    # Map stock levels to notification types for styling
    stock_level_colors = {
        20: "info",  # Blue
        15: "primary",  # Dark blue
        10: "warning",  # Yellow
        5: "danger",  # Red
        1: "urgent",  # Bright red
        0: "out-of-stock"  # Gray/Black
    }

    return jsonify({
        "notifications": [
            {
                "id": n.id,
                "message": n.message,
                "date": n.date.strftime("%Y-%m-%d %H:%M:%S"),
                "product_id": n.product_id,  # Include the product ID here
                "product_name": n.product.name if n.product else "Unknown Product",
                "type": stock_level_colors.get(n.stock, "default"),  # Default fallback
                "seen": n.seen
            }
            for n in notifications
        ]
    })


@app.route('/mark_notification_seen/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_seen(notification_id):
    if current_user.role != 'seller':
        return jsonify({"error": "Unauthorized"}), 403

    notification = StockNotification.query.filter_by(id=notification_id, seller_id=current_user.seller.id).first()
    if notification:
        notification.seen = True
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Notification not found."}), 404


@app.route('/notifications/archive/<int:notification_id>', methods=['POST'])
@login_required
def seller_archive_notification(notification_id):
    if current_user.role != 'seller':
        return jsonify({"error": "Unauthorized"}), 403

    notification = StockNotification.query.filter_by(id=notification_id, seller_id=current_user.seller.id).first()
    if notification:
        db.session.delete(notification)
        db.session.commit()
        return jsonify({"success": True})
    return jsonify({"error": "Notification not found."}), 404


# Route for adding new notifications
@app.route('/add_notification', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_notification():
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        notification_type = request.form['notification_type']
        product_id = request.form.get('product_id')

        # Validate fields based on notification type
        if notification_type == 'promotion' and not product_id:
            flash("Promotion notifications require a selected product.")
            return redirect(url_for('add_notification'))
        elif notification_type == 'message':
            # For general notifications, clear product_id as it's not required
            product_id = None
        
        new_notification = Notification(
            title=title,
            message=message,
            product_id=product_id,
            notification_type=notification_type,
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(new_notification)
        db.session.commit()  # Commit to save the notification

        # Assuming you want to notify all users
        users = Users.query.filter_by(role='user').all()  # Fetch all users
        for user in users:
            user_notification = UserNotification(user_id=user.id, notification_id=new_notification.id)
            db.session.add(user_notification)

        db.session.commit()  # Commit to save user notifications
        return redirect(url_for('view_notifications'))

    # Load products for selection
    products = Product.query.all()
    return render_template('add_notifications.html', products=products)


@app.route('/archive/notification/<int:notification_id>', methods=['POST'])
@login_required
def archive_notification(notification_id):
    user = current_user

    # Check if the notification exists
    notification = Notification.query.get_or_404(notification_id)

    if user.role == 'admin':
        # Admin archives by deactivating the notification
        notification.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Notification has been deactivated."})
    else:
        # User archives their personal notification
        user_notification = UserNotification.query.filter_by(
            user_id=user.id, 
            notification_id=notification_id
        ).first()

        if not user_notification:
            return jsonify({"success": False, "message": "Notification not found for user."}), 404
        
        user_notification.is_archived = True
        db.session.commit()
        return jsonify({"success": True, "message": "Notification archived successfully."})


@app.before_request
def load_unseen_count():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            g.unseen_count = UserNotification.query.filter_by(
                user_id=current_user.id, seen=False, is_archived=False
            ).count()
        elif current_user.role == 'seller':
            g.unseen_count = StockNotification.query.filter_by(
                seller_id=current_user.id, seen=False
            ).count()
    else:
        g.unseen_count = 0
# END OF NOTIFICATION CODE


# VOUCHER CODES
# Use to auto gemerate a 6 alphanumeric code
def generate_unique_code():
    """Generate a unique 6-character alphanumeric code."""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        # Check if the generated code already exists
        if not Voucher.query.filter_by(code=code).first():
            return code

# routes.py
@app.route('/archive_voucher/<int:voucher_id>', methods=['POST'])
@login_required
def archive_voucher(voucher_id):
    # Ensure the user is a seller
    if not hasattr(current_user, 'seller') or not current_user.seller:
        flash("Only sellers can archive vouchers.", "danger")
        return redirect(url_for('view_vouchers'))

    # Find the voucher and archive it
    voucher = Voucher.query.get_or_404(voucher_id)
    if voucher.seller_id != current_user.seller.id:
        flash("You do not have permission to archive this voucher.", "danger")
        return redirect(url_for('view_vouchers'))

    voucher.is_archived = True
    db.session.commit()
    flash("Voucher archived successfully.", "success")
    return redirect(url_for('view_vouchers'))

# Creat a Shop Voucher
@app.route('/create_voucher', methods=['GET', 'POST'])
@login_required
@role_required('seller')
def create_voucher():
    # Ensure the user is a seller
    if not hasattr(current_user, 'seller') or not current_user.seller:
        flash("Only sellers can create vouchers.", "danger")
        return redirect(url_for('seller'))

    if request.method == 'POST':
        try:
            # Retrieve form data
            voucher_name = request.form.get('voucher_name')
            voucher_type = "shop"
            code = request.form.get('code') or generate_unique_code()
            discount_type = request.form.get('discount_type')

            discount_amount = request.form.get('discount_amount')
            min_price = request.form.get('min_price')
            quantity = request.form.get('quantity')  # Default to 1 if not provided



            # Check if discount_amount, min_price, or quantity are missing or empty, and set defaults if needed
            try:
                discount_amount = float(discount_amount) if discount_amount else 0.00
                min_price = float(min_price) if min_price else 0.00
                quantity = int(quantity) if quantity else 0
            except ValueError:
                flash("Please enter valid numbers for discount amount, minimum price, and quantity.", "danger")
                return redirect(url_for('create_voucher'))

            # Parse dates and validate them
            expiration_date_str = request.form.get('expiration_date')
            if not expiration_date_str:
                flash("Expiration date is required.", "danger")
                return redirect(url_for('create_voucher'))
            expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d')

            display_option = request.form.get('voucherDisplay')
            display_early = request.form.get('display_early') == "on"

            if not display_option:
                flash("Please select a Voucher Display Setting.", "danger")
                return redirect(url_for('create_voucher'))

            # Start date handling based on early display checkbox
            if display_early:
                early_usage_start_str = request.form.get('early_usage_period_start')
                if early_usage_start_str:
                    start_date = datetime.strptime(early_usage_start_str, '%Y-%m-%dT%H:%M')
                    expiration_date = expiration_date.replace(hour=start_date.hour, minute=start_date.minute)
                    if start_date >= expiration_date:
                        flash("Start date must be before the expiration date.", "danger")
                        return redirect(url_for('create_voucher'))
                else:
                    flash("Early usage start is required if Display Early is selected.", "danger")
                    return redirect(url_for('create_voucher'))
            else:
                start_date = datetime.combine(datetime.strptime(request.form.get('start_date'), '%Y-%m-%d'), datetime.min.time())

            # Additional validation for start and expiration dates
            if start_date >= expiration_date:
                flash("Start date must be before the expiration date.", "danger")
                return redirect(url_for('create_voucher'))

            # Create voucher instance
            new_voucher = Voucher(
                voucher_name=voucher_name,
                voucher_type=voucher_type,
                code=code,
                discount_type=discount_type,
                discount_amount=discount_amount,
                min_price=min_price,
                quantity=quantity,
                start_date=start_date,
                expiration_date=expiration_date,
                seller_id=current_user.seller.id,
            )

            db.session.add(new_voucher)
            db.session.commit()

            # Handle display option (e.g., assign to all users)
            if display_option == 'allPages':
                users = Users.query.filter_by(role='user').all()
                for user in users:
                    user_voucher = UserVoucher(user_id=user.id, voucher_id=new_voucher.id, claimed=False)
                    db.session.add(user_voucher)
            db.session.commit()

            flash(f'Voucher "{new_voucher.voucher_name}" created successfully!', 'success')
            return redirect(url_for('view_vouchers'))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('create_voucher'))

    # Fetch products for the form's product selection dropdown, only products belonging to the seller
    return render_template('create_voucher.html')


@app.route('/vouchers', methods=['GET'])
@login_required
@role_required('seller')
def view_vouchers():

    return render_template('view_vouchers.html')


@app.route('/voucher/table', methods=['GET'])
@login_required
@role_required('seller')
def view_table_vouchers():
    
    seller_id = current_user.seller.id

    vouchers = Voucher.query.filter_by(seller_id=current_user.seller.id, is_archived=False).all()
    now = datetime.now()

    # Voucher statistics
    voucher_stats = monitor_voucher_quantities(seller_id)
    voucher_stats['claimed_vouchers_count'] = monitor_claimed_vouchers(seller_id)

    return render_template(
        'voucher.html', 
        vouchers=vouchers, 
        now=now,       
        voucher_stats=voucher_stats
        )

# Create a Product Voucher
@app.route('/create_product_voucher', methods=['GET', 'POST'])
@login_required
@role_required('seller')
def create_product_voucher():
    # Ensure the user is a seller
    if not hasattr(current_user, 'seller') or not current_user.seller:
        flash("Only sellers can create vouchers.", "danger")
        return redirect(url_for('seller'))

    if request.method == 'POST':
        try:
            # Get and validate form data
            voucher_name = request.form.get('voucher_name')
            voucher_type = "product"
            code = request.form.get('code') or generate_unique_code()
            discount_type = request.form.get('discount_type')
            product_ids = request.form.getlist('eligible_products') 

            discount_amount = request.form.get('discount_amount')
            min_price = request.form.get('min_price')
            quantity = request.form.get('quantity')

            # Fetch selected products from database
            products = Product.query.filter(Product.id.in_(product_ids), Product.seller_id == current_user.seller.id).all()

            # Check if discount_amount, min_price, or quantity are missing or empty, and set defaults if needed
            try:
                discount_amount = float(discount_amount) if discount_amount else 0.00
                min_price = float(min_price) if min_price else 0.00
                quantity = int(quantity) if quantity else 0
            except ValueError:
                flash("Please enter valid numbers for discount amount, minimum price, and quantity.", "danger")
                return redirect(url_for('create_voucher'))
            
            display_option = request.form.get('voucherDisplay')  # Get the display option
            display_early = request.form.get('display_early') == "on"

            if not display_option:
                flash("Please select a Voucher Display Setting.", "danger")
                return redirect(url_for('create_voucher'))

            if not products:
                flash("No valid products selected for the voucher.", "danger")
                return redirect(url_for('create_product_voucher'))

            # Parse and validate expiration date
            expiration_date_str = request.form.get('expiration_date')
            if not expiration_date_str:
                flash("Expiration date is required.", "danger")
                return redirect(url_for('create_product_voucher'))
            expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d')

            # Start date handling based on early display checkbox
            if display_early:
                early_usage_start_str = request.form.get('early_usage_period_start')
                if early_usage_start_str:
                    start_date = datetime.strptime(early_usage_start_str, '%Y-%m-%dT%H:%M')
                    expiration_date = expiration_date.replace(hour=start_date.hour, minute=start_date.minute)
                    if start_date >= expiration_date:
                        flash("Start date must be before the expiration date.", "danger")
                        return redirect(url_for('create_voucher'))
                else:
                    flash("Early usage start is required if Display Early is selected.", "danger")
                    return redirect(url_for('create_voucher'))
            else:
                # Default start date time is 12:00 AM if Display Early is unchecked
                start_date = datetime.combine(datetime.strptime(request.form.get('start_date'), '%Y-%m-%d'), datetime.min.time())

            # Validate start and expiration dates
            if start_date >= expiration_date:
                flash("Start date must be before expiration date.", "danger")
                return redirect(url_for('create_product_voucher'))

            # Create the voucher
            new_voucher = Voucher(
                voucher_name=voucher_name,
                voucher_type=voucher_type,
                code=code,
                discount_type=discount_type,
                discount_amount=discount_amount,
                min_price=min_price,
                quantity=quantity,
                start_date=start_date,
                expiration_date=expiration_date,
                seller_id=current_user.seller.id,
            )

            # Associate selected products with the voucher
            new_voucher.products.extend(products)
            db.session.add(new_voucher)
            db.session.commit()

            # If voucher display option is set to all pages, assign it to users
            if display_option == 'allPages':
                users = Users.query.filter_by(role='user').all()
                for user in users:
                    user_voucher = UserVoucher(user_id=user.id, voucher_id=new_voucher.id, claimed=False)
                    db.session.add(user_voucher)
            db.session.commit()  # Commit user vouchers

            flash(f'Voucher "{new_voucher.voucher_name}" created successfully!', 'success')
            return redirect(url_for('view_vouchers'))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for('create_product_voucher'))

    # Fetch products for the form's product selection dropdown, only products belonging to the seller
    seller_products = Product.query.filter_by(seller_id=current_user.seller.id).all()
    return render_template('create_product_voucher.html', seller_products=seller_products)

# Check voucher status 
@app.route('/check_and_archive_voucher/<int:voucher_id>', methods=['GET'])
def check_and_archive_voucher(voucher_id):
    # Retrieve the voucher by ID
    voucher = Voucher.query.get(voucher_id)
    if not voucher:
        return jsonify({"message": "Voucher not found"}), 404

    # Check if the voucher quantity is 0 and archive if necessary
    if voucher.quantity == 0:
        voucher.archive_if_needed()
        message = "Voucher has been archived due to zero quantity."
    else:
        message = "Voucher quantity is greater than zero. No action taken."

    db.session.commit()  # Commit any changes if the voucher was archived
    return jsonify({"message": message, "is_archived": voucher.is_archived})

# User view Shop and Product Voucher
@app.route('/shop/voucher')
@login_required
@role_required('user')
def shop_voucher():
    user = current_user

    # Fetch all active vouchers sent to the user
    user_vouchers = UserVoucher.query.filter_by(user_id=user.id).all()
    sent_voucher_ids = {uv.voucher_id for uv in user_vouchers}

    # Retrieve all relevant vouchers
    vouchers = Voucher.query.filter(
        Voucher.id.in_(sent_voucher_ids),
        Voucher.is_archived == False,
        Voucher.start_date <= datetime.utcnow()
    ).all()

    available_vouchers = []
    for voucher in vouchers:
        expiration_date = None
        if voucher.expiration_date:
            if isinstance(voucher.expiration_date, str):
                try:
                    expiration_date = datetime.fromisoformat(voucher.expiration_date)
                except ValueError:
                    print(f"Invalid expiration_date for voucher ID {voucher.id}: {voucher.expiration_date}")
            elif isinstance(voucher.expiration_date, datetime):
                expiration_date = voucher.expiration_date

        expired = expiration_date and expiration_date < datetime.utcnow()
        claimed = any(uv.voucher_id == voucher.id and uv.claimed for uv in user_vouchers)
        archived = any(uv.voucher_id == voucher.id and uv.is_archived for uv in user_vouchers)

        # Handle voucher type and item info
        if voucher.voucher_type == "shop":
            shop = Seller.query.get(voucher.seller_id)
            item_info = {'name': shop.shop_name, 'image': shop.image_file}
        elif voucher.voucher_type == "product":
            product = Product.query.filter(Product.vouchers.contains(voucher)).first()
            item_info = {
                'name': product.name,
                'image': product.images[0].image_path if product.images else 'default_product_image.jpg'
            }
        else:
            item_info = {'name': None, 'image': None}

        # Add expiration_date check in the voucher_with_status object
        voucher_with_status = {
            'id': voucher.id,
            'voucher_name': voucher.voucher_name,
            'voucher_type': voucher.voucher_type,
            'min_price': voucher.min_price,
            'discount_amount': voucher.discount_amount,
            'discount_type': voucher.discount_type,
            'expiration_date': expiration_date,  # Pass as datetime object
            'code': voucher.code,
            'claimed': claimed,
            'expired': expired,
            'quantity': voucher.quantity,
            'archived': archived,
            'item_info': item_info
        }
        available_vouchers.append(voucher_with_status)

    return render_template('claim_shop_voucher.html', available_vouchers=available_vouchers)

# Use to claim shop and product voucher
@app.route('/claim_voucher/<int:voucher_id>', methods=['POST'])
@login_required
def claim_voucher(voucher_id):
    user = current_user

    # Retrieve the voucher
    voucher = Voucher.query.get(voucher_id)
    if not voucher or not voucher.is_active or voucher.quantity <= 0:
        flash("This voucher is not available or has expired.", "danger")
        return redirect(url_for('shop_voucher'))

    # Check if the voucher is assigned to the current user
    user_voucher = UserVoucher.query.filter_by(user_id=user.id, voucher_id=voucher.id).first()
    if not user_voucher:
        flash("You are not authorized to claim this voucher.", "danger")
        return redirect(url_for('shop_voucher'))

    # Check if the voucher has already been claimed
    if user_voucher.claimed:
        flash("You have already claimed this voucher.", "warning")
        return redirect(url_for('shop_voucher'))

    # Check if the user has already claimed 5 vouchers
    claimed_count = UserVoucher.query.filter_by(user_id=user.id, claimed=True).count()
    if claimed_count >= 5:
        flash("You can only claim up to 5 vouchers at a time.", "warning")
        return redirect(url_for('shop_voucher'))

    # Mark the voucher as claimed
    user_voucher.claimed = True
    user_voucher.claimed_at = datetime.now()
    voucher.quantity -= 1

    # Commit changes to the database
    db.session.commit()

    flash("Voucher claimed successfully!", "success")
    return redirect(url_for('shop_voucher'))

# Use to Claim shop and Product Voucher Thru Voucher Code
@app.route('/claim_voucher_by_code', methods=['POST'])
@login_required
def claim_voucher_by_code():
    user = current_user  # Get the currently logged-in user
    voucher_code = request.form['voucher_code'].strip()  # Retrieve the voucher code from the form

    # Retrieve the voucher based on the entered code
    voucher = Voucher.query.filter_by(code=voucher_code).first()

    if not voucher:
        flash("Invalid voucher code.", "danger")
        return redirect(url_for('shop_voucher'))

    # Check if the voucher is active and available
    if not voucher.is_active or voucher.quantity <= 0:
        flash("This voucher is not available or has expired.", "danger")
        return redirect(url_for('shop_voucher'))

    # Check if the voucher has already been assigned to the user
    user_voucher = UserVoucher.query.filter_by(user_id=user.id, voucher_id=voucher.id).first()

    # If the voucher is assigned to the user but already claimed or archived, show appropriate message
    if user_voucher:
        if user_voucher.claimed:
            flash("You have already claimed this voucher.", "warning")
        elif user_voucher.is_archived:
            flash("This voucher has been archived or is no longer available to claim.", "warning")
        else:
            flash("This voucher is already assigned to you but not yet claimed.", "warning")
        return redirect(url_for('shop_voucher'))

    # Check if the user has already claimed this voucher
    if user_voucher and user_voucher.claimed:
        flash("You have already claimed this voucher.", "warning")
        return redirect(url_for('shop_voucher'))

    # Check if the user has already claimed 5 vouchers
    claimed_count = UserVoucher.query.filter_by(user_id=user.id, claimed=True).count()
    if claimed_count >= 5:
        flash("You can only claim up to 5 vouchers at a time.", "warning")
        return redirect(url_for('shop_voucher'))

    # If the voucher hasn't been claimed yet, claim it
    if not user_voucher:
        # Otherwise, create a new UserVoucher entry
        user_voucher = UserVoucher(user_id=user.id, voucher_id=voucher.id, claimed=True, claimed_at=datetime.utcnow())
        db.session.add(user_voucher)

    # Decrease the voucher quantity
    voucher.quantity -= 1

    # Commit the transaction
    db.session.commit()

    flash("Voucher claimed successfully!", "success")
    return redirect(url_for('shop_voucher'))

# For User Pop-up Notification Voucher
@app.route('/check_new_vouchers', methods=['GET'])
@login_required
@role_required('user')
def check_new_vouchers():
    # Define the time range for "new" vouchers (vouchers added in the last 24 hours)
    last_24_hours = datetime.utcnow() - timedelta(hours=24)

    # Fetch new vouchers that are not archived and not expired, and are assigned to the user
    new_vouchers = Voucher.query.join(UserVoucher, isouter=True).filter(
        Voucher.start_date >= last_24_hours,  # Voucher added in the last 24 hours
        Voucher.is_archived == False,  # Voucher is not archived
        Voucher.expiration_date > datetime.utcnow(),  # Voucher is not expired
        UserVoucher.user_id == current_user.id,  # Voucher must be assigned to the current user
        ~Voucher.user_vouchers.any(
            (UserVoucher.user_id == current_user.id) & 
            ((UserVoucher.claimed == True) | (UserVoucher.is_archived == True))
        )
    ).all()

    # Prepare the response with voucher information
    if new_vouchers:
        vouchers_info = []

        for v in new_vouchers[:1]:  # Only return one voucher at a time
            # Determine the message based on the voucher type
            if v.voucher_type == 'product':
                # For product vouchers, fetch the related seller and product info
                seller = Seller.query.filter(Seller.vouchers.contains(v)).first()
                product = Product.query.filter(Product.vouchers.contains(v)).first()

                if seller and product:
                    item_info = {
                        'shop': seller.shop_name.upper(),  # Make shop name uppercase
                        'name': product.name,
                        'category': product.category.upper()  # Make category name uppercase
                    }
                    # Formatting the message for product vouchers
                    voucher_message = f"Get a discount for {item_info['name']} in <strong>{item_info['category']}</strong> Category from <strong>{item_info['shop']}</strong> Shop"
                else:
                    # In case no seller or product is found
                    voucher_message = "Product or Seller not found"
            else:
                # Shop-wide voucher message
                voucher_message = "Shop-wide discount available"

            # Construct the voucher data
            voucher_data = {
                'voucher_id': v.id,
                'voucher_name': v.voucher_name,
                'discount_amount': v.discount_amount,
                'discount_type': v.discount_type,  # Include the type of discount
                'code': v.code,
                'expiration_date': v.expiration_date,
                'voucher_type': v.voucher_type,  # Include voucher type ('Product' or 'Shop')
                'discount_value': v.discount_amount if v.discount_type == 'value' else None,  # Display discount value for 'value' type vouchers
                'discount_percentage': v.discount_amount if v.discount_type == 'percentage' else None,  # Display percentage for 'percentage' type vouchers
                'voucher_message': voucher_message,  # Add the voucher message
                'item_info': item_info if v.voucher_type == 'product' else None  # Include item info only for product vouchers
            }

            vouchers_info.append(voucher_data)

        return jsonify({"new_vouchers": vouchers_info}), 200

    return jsonify({"new_vouchers": []}), 200


# Monitoring function for voucher quantities
def monitor_voucher_quantities(seller_id):
    """
    Monitors total quantities for shop vouchers, product vouchers, and all vouchers for a given seller.
    """
    # Total shop voucher quantity
    shop_vouchers_quantity = db.session.query(
        func.sum(Voucher.quantity)
    ).filter(
        Voucher.seller_id == seller_id,
        Voucher.voucher_type == 'shop'
    ).scalar() or 0

    # Total product voucher quantity
    product_vouchers_quantity = db.session.query(
        func.sum(Voucher.quantity)
    ).filter(
        Voucher.seller_id == seller_id,
        Voucher.voucher_type == 'product'
    ).scalar() or 0

    # Total quantity of all vouchers
    total_vouchers_quantity = shop_vouchers_quantity + product_vouchers_quantity

    return {
        'shop_vouchers_quantity': shop_vouchers_quantity,
        'product_vouchers_quantity': product_vouchers_quantity,
        'total_vouchers_quantity': total_vouchers_quantity
    }

# Monitoring function for claimed vouchers
def monitor_claimed_vouchers(seller_id):
    """
    Monitors the total number of claimed vouchers for a given seller.
    """
    claimed_vouchers_count = db.session.query(
        func.count(UserVoucher.id)
    ).join(Voucher, Voucher.id == UserVoucher.voucher_id).filter(
        Voucher.seller_id == seller_id,
        UserVoucher.claimed == True
    ).scalar() or 0

    return claimed_vouchers_count

# Example Usage
def display_monitoring_data(seller_id):
    """
    Display monitoring data for a given seller.
    """
    quantities = monitor_voucher_quantities(seller_id)
    claimed_count = monitor_claimed_vouchers(seller_id)

    print(f"Monitoring Data for Seller ID {seller_id}:")
    print(f"Total Shop Vouchers Quantity: {quantities['shop_vouchers_quantity']}")
    print(f"Total Product Vouchers Quantity: {quantities['product_vouchers_quantity']}")
    print(f"Total Vouchers Quantity: {quantities['total_vouchers_quantity']}")
    print(f"Total Claimed Vouchers: {claimed_count}")

# Example Flask route for monitoring
@app.route('/monitor/vouchers/<int:seller_id>')
def monitor_vouchers(seller_id):
    """
    Flask route to monitor voucher quantities and claimed vouchers for a seller.
    """
    quantities = monitor_voucher_quantities(seller_id)
    claimed_count = monitor_claimed_vouchers(seller_id)

    return {
        "shop_vouchers_quantity": quantities['shop_vouchers_quantity'],
        "product_vouchers_quantity": quantities['product_vouchers_quantity'],
        "total_vouchers_quantity": quantities['total_vouchers_quantity'],
        "claimed_vouchers_count": claimed_count
    }


@app.route('/user/notifications', methods=['GET'])
@login_required  # Ensure the user is logged in
def user_notifications():
    try:
        user_id = current_user.id

        # Count unseen notifications
        unseen_count = db.session.query(UserNotification).filter_by(
            user_id=user_id, seen=False, is_archived=False
        ).count()

        # Fetch active notifications
        notifications = db.session.query(Notification).join(UserNotification).filter(
            UserNotification.user_id == user_id,
            UserNotification.is_archived == False,
            Notification.is_active == True
        ).order_by(Notification.created_at.desc()).all()

        # Mark unseen notifications as seen
        view_at = datetime.now()
        db.session.query(UserNotification).filter_by(
            user_id=user_id, seen=False, is_archived=False
        ).update({
            "seen": True,
            "viewed_at": view_at
        })
        db.session.commit()

        # Render notifications template
        return render_template(
            'user_notifications.html',  # Ensure this template exists
            notifications=notifications,
            unseen_count=unseen_count
        )
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return jsonify({"error": "Could not fetch notifications"}), 500



@app.route('/chat_with_seller/<int:seller_id>')
@login_required
@role_required('user')
def chat_with_seller(seller_id):
    seller_user = Users.query.get_or_404(seller_id)

    # Prevent messaging oneself
    if seller_id == current_user.id:
        flash("You cannot message yourself!", "danger")
        return redirect(url_for('home'))  # Redirect to a safer location

    # Retrieve messages
    messages = Messages.query.filter(
        ((Messages.sender_id == current_user.id) & (Messages.receiver_id == seller_id)) |
        ((Messages.sender_id == seller_id) & (Messages.receiver_id == current_user.id))
    ).order_by(Messages.timestamp.asc()).all()

    # Mark messages as seen
    unseen_messages = [msg for msg in messages if msg.receiver_id == current_user.id and not msg.is_seen]
    for msg in unseen_messages:
        msg.is_seen = True
    db.session.commit()

    return render_template('chat_seller.html', messages=messages, seller_user=seller_user)


@app.route('/chat_seller_send_message/<int:receiver_id>', methods=['POST'])
@login_required
def chat_seller_send_message(receiver_id):
    message_content = request.form.get('message').strip()
    file = request.files.get('file')  # Get the file from the form
    
    # if not content:
    #     flash("Message cannot be empty!", "warning")
    #     return redirect(request.referrer)

    # Validate receiver exists and isn't the sender
    receiver = Users.query.get(receiver_id)
    if not receiver or receiver_id == current_user.id:
        flash("Invalid recipient!", "danger")
        return redirect(url_for('chat_with_seller', seller_id=receiver_id))
    
        # Handle file upload
    file_path = None
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid conflicts
        unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_CHAT_FOLDER'], unique_filename)
        file.save(file_path)  # Save the file to the specific directory

        # Store the relative file path for database storage
        file_path = f"{unique_filename}"

        # Ensure at least message content or file is present
    if not message_content and not file:
        flash("Please enter a message or select a file to send.", 'warning')
        return redirect(url_for('chat_with_seller', seller_id=receiver_id))

    # Save the message
    message = Messages(
        content=message_content,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        file_path=file_path,  # Store the file path
        timestamp=datetime.utcnow()
    )
    db.session.add(message)
    db.session.commit()
    
    flash("Message sent successfully!", "success")
    return redirect(url_for('chat_with_seller', seller_id=receiver_id))


@app.route('/user/user_chat_seller_archive_message/<int:message_id>', methods=['POST'])
@role_required('user')
def user_chat_seller_archive_message(message_id):
    # Get the message by its ID
    message = Messages.query.get_or_404(message_id)

    # Ensure that the current user is either the sender or the receiver of the message
    if message.sender_id != current_user.id and message.receiver_id != current_user.id:
        flash('Message archived successfully.', 'success')
        return redirect(url_for('chat_with_seller', receiver_id=message.receiver_id))

    # Here, instead of deleting, we can archive the message by moving it to another table,
    # or just add a column like 'is_archived' to flag it as archived.
    message.is_archived = True  # Assuming you have an 'is_archived' column in your Message model

    db.session.commit()

    return redirect(url_for('chat_with_seller', seller_id=message.receiver_id))





@app.route('/courier/chat/<int:receiver_id>')
@login_required
@role_required('courier')
def courier_chat(receiver_id):
    receiver = Users.query.get_or_404(receiver_id)  # Get receiver or 404 if not found

    # Ensure receiver is valid and exists
    if not receiver:
        flash("Receiver does not exist.")
        return redirect(url_for('courier_chat', receiver_id=receiver_id))

    # Get all messages between current_user and the receiver
    messages = Messages.query.filter(
        ((Messages.sender_id == current_user.id) & (Messages.receiver_id == receiver_id)) |
        ((Messages.sender_id == receiver_id) & (Messages.receiver_id == current_user.id))
    ).order_by(Messages.timestamp).all()

    # Mark messages as seen
    unseen_messages = [msg for msg in messages if msg.receiver_id == current_user.id and not msg.is_seen]
    for msg in unseen_messages:
        msg.is_seen = True
    db.session.commit()  # Commit the changes to mark messages as seen

    # Get a list of other users for the chat sidebar
    users = (Users.query.filter(Users.id != current_user.id)
            .outerjoin(
                Messages,
                ((Messages.sender_id == Users.id) & (Messages.receiver_id == current_user.id)) |
                ((Messages.receiver_id == Users.id) & (Messages.sender_id == current_user.id))
            )
            .order_by(
                db.desc(db.func.max(Messages.timestamp)),
                db.desc(db.func.sum(db.case((Messages.is_seen == False, 1), else_=0)))
            )
            .group_by(Users.id)
            .all())

    # Display a message if the current user has no image file
    if current_user.image_file is None:
        flash('Please upload a profile picture to continue.', 'warning')

    return render_template('chat_courier.html', messages=messages, current_user=current_user, receiver=receiver, users=users)



@app.route('/courier_send_message', methods=['POST'])
def courier_send_message():
    message_content = request.form.get('message').strip()
    receiver_id = request.form.get('receiver')
    file = request.files.get('file')  # Get the file from the form

    receiver = Users.query.get(receiver_id)
    if not receiver:
        flash("Receiver does not exist.")
        return redirect(url_for('courier_chat', receiver_id=receiver_id))

    # Handle file upload
    file_path = None
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid conflicts
        unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_CHAT_FOLDER'], unique_filename)
        file.save(file_path)  # Save the file to the specific directory

        # Store the relative file path for database storage
        file_path = f"{unique_filename}"

    if not message_content and not file:
        flash("Please enter a message or select a file to send.", 'warning')
        return redirect(url_for('courier_chat', receiver_id=receiver_id))

    # Save message details in the database
    new_message = Messages(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        content=message_content or '',  # Avoid None content if no message text is provided
        file_path=file_path,  # Store the file path
        timestamp=datetime.now()
    )

    db.session.add(new_message)
    db.session.commit()

    return redirect(url_for('courier_chat', receiver_id=receiver.id))


@app.route('/courier/archive_message/<int:message_id>', methods=['POST'])
@role_required('courier')
def courier_archive_message(message_id):
    # Get the message by its ID
    message = Messages.query.get_or_404(message_id)

    if message.sender_id != current_user.id and message.receiver_id != current_user.id:
        flash("You don't have permission to archive this message.")
        return redirect(url_for('courier_chat', receiver_id=message.receiver_id))

    message.is_archived = True  

    db.session.commit()
    flash('Message archived successfully.', 'success')  # Fixed flash message

    return redirect(url_for('courier_chat', receiver_id=message.receiver_id))






@app.route('/seller/income/pending', methods=['GET'])
@login_required
@role_required('seller')
def get_pending_income():
    """
    Fetch pending income data grouped by order date for the seller.
    """
    seller_id = current_user.seller.id

    # Query pending income grouped by order creation date
    pending_income = (
        db.session.query(
            func.date(Order.date_created).label('date'),
            func.coalesce(func.sum(OrderItem.price * OrderItem.quantity), 0).label('total_income')
        )
        .join(OrderItem, Order.id == OrderItem.order_id)
        .filter(
            OrderItem.seller_id == seller_id,
            OrderItem.status == 'Pending'
        )
        .group_by(func.date(Order.date_created))
        .order_by(func.date(Order.date_created))
        .all()
    )

    # Ensure 'date' is a proper datetime object
    data = {
        'timestamps': [
            record.date if isinstance(record.date, str) else record.date.strftime('%Y-%m-%d') 
            for record in pending_income
        ],
        'incomes': [float(record.total_income) for record in pending_income]
    }
    for record in pending_income:
        print(type(record.date), record.date)


    return jsonify(data)



@app.route('/apply_voucher', methods=['POST'])
@login_required
def apply_voucher():
    """Apply a voucher to the current user's cart."""
    if 'applied_voucher_code' in session:
        flash("Please clear the current voucher before applying a new one.", "warning")
        return redirect(url_for('checkout'))
    
    code = request.form.get('voucher_code')
    voucher = Voucher.query.filter_by(code=code).first()

    if not voucher or not voucher.is_active or voucher.expiration_date < datetime.utcnow():
        flash("This voucher is invalid or expired.", "danger")
        return redirect(url_for('checkout'))
    
    user_voucher = UserVoucher.query.filter_by(user_id=current_user.id, voucher_id=voucher.id).first()
    if not user_voucher or user_voucher.is_archived or not user_voucher.claimed:
        flash("This voucher is not available for your account.", "danger")
        return redirect(url_for('checkout'))
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Your cart is empty.", "danger")
        return redirect(url_for('checkout'))
    
    eligible_items = []
    eligible_total = 0
    
    if voucher.voucher_type == 'product':  # Check for product-level vouchers
        eligible_items = [
            item for item in cart_items
            if item.product_id in [vp.id for vp in voucher.products]
        ]
        eligible_total = sum(item.price * item.quantity for item in eligible_items)

    elif voucher.voucher_type == 'shop':  # Check for shop-level vouchers
        eligible_items = [
            item for item in cart_items
            if Product.query.get(item.product_id).seller_id == voucher.seller_id
        ]
        eligible_total = sum(item.price * item.quantity for item in eligible_items)

    if not eligible_items:
        flash("No eligible items in your cart for this voucher.", "warning")
        return redirect(url_for('checkout'))

    if eligible_total >= voucher.min_price:
        discount_applied_items, total_discount = _apply_shop_voucher_discount(voucher, eligible_items)
        session['discounted_items'] = discount_applied_items
        session['applied_discount'] = total_discount
        session['applied_voucher_code'] = code
        session['applied_voucher_type'] = voucher.voucher_type  # Store voucher type
        flash(f"Voucher '{voucher.voucher_name}' applied successfully to eligible items!", "success")
    else:
        flash("This voucher requires a minimum spend with eligible items.", "warning")
        return redirect(url_for('checkout'))
    
    db.session.commit()  # Commit changes to mark items as discounted in the session
    return redirect(url_for('checkout'))

def _apply_shop_voucher_discount(voucher, eligible_items):
    """Apply shop voucher discount to eligible items individually."""
    discount_applied_items = []
    total_discount = 0

    # Calculate total price of eligible items
    eligible_total = sum(item.price * item.quantity for item in eligible_items)

    for item in eligible_items:
        # Apply percentage discount
        if voucher.discount_type == 'percentage':
            item_discount = item.price * (voucher.discount_amount / 100) * item.quantity
        else:  # Apply fixed discount
            # Apply the fixed discount proportionally to each item based on its contribution to the total eligible price
            item_discount = min(voucher.discount_amount * (item.price * item.quantity) / eligible_total, item.price * item.quantity)

        # Update the price after applying the discount
        total_discount += item_discount
        final_price = item.price * item.quantity - item_discount
        item.price = final_price / item.quantity  # Update price per item
        # Update discount status

        # Add to list for session
        discount_applied_items.append({
            'product_id': item.product_id,
            'price': final_price / item.quantity,
            'quantity': item.quantity,
        })

        db.session.add(item)  # Ensure the item is updated in the session

    db.session.commit()  # Commit all changes
    return discount_applied_items, total_discount

@app.route('/finalize_order', methods=['POST'])
@login_required
def finalize_order():
    """Finalize the order by inserting discounted items into the OrderItem table."""
    discounted_items = session.get('discounted_items', [])
    applied_voucher_code = session.get('applied_voucher_code')
    
    for item in discounted_items:
        order_item = OrderItem(
            user_id=current_user.id,
            product_id=item['product_id'],
            quantity=item['quantity'],
            price=item['price'],
            discounted_price=item['price'] if item['discounted'] else None,
            order_status='Pending',
            created_at=datetime.utcnow()
        )
        db.session.add(order_item)

    db.session.commit()  # Commit all changes to finalize order and archive voucher

    session.pop('applied_discount', None)
    session.pop('applied_voucher_code', None)
    session.pop('discounted_items', None)
    flash("Order finalized successfully!", "success")
    return redirect(url_for('order_summary'))

    
@app.route('/clear_voucher', methods=['POST'])
@login_required
def clear_voucher():
    """Clear the voucher and reset original prices."""
    
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    for item in cart_items:
        # Query ProductVariation based on product_id, color, and size
        product_variation = ProductVariation.query.filter_by(
            product_id=item.product_id, 
            color=item.color, 
            size=item.size
        ).first()

        # If a matching ProductVariation is found, update the price
        if product_variation:
            item.price = product_variation.price * item.quantity  # Multiply by quantity
            
        else:
            # Optionally, handle the case where the ProductVariation is not found.
            # If no variation found, you might set a default price (e.g., from Product table).
            product = Product.query.filter_by(id=item.product_id).first()
            if product:
                item.price = product.price * item.quantity  # Use the base product price if no variation found

    db.session.commit()
    
    # Remove applied voucher and discount session data
    session.pop('applied_discount', None)
    session.pop('applied_voucher_code', None)
    
    flash('Voucher has been cleared and original prices restored.', 'success')
    return jsonify(success=True)

@app.route('/checkout')
@login_required
def checkout():
    if not current_user.is_authenticated:
        flash('Please log in to proceed with checkout.', 'danger')
        return redirect(url_for('login'))

    # Fetch the updated cart items for the user
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    # Check if the cart is empty
    if not cart_items:
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('shop'))

    # Group cart items by seller to calculate shipping fees per seller (JAVIER)
    # seller_orders = {}
    # for item in cart_items:
    #     product = Product.query.get(item.product_id)
    #     seller_id = product.seller_id

    #     if seller_id not in seller_orders:
    #         seller_orders[seller_id] = []
    #     seller_orders[seller_id].append(item)

    # # Calculate subtotal for all cart items and shipping fees for each seller
    # subtotal = sum(item.price * item.quantity for item in cart_items)
    # total_shipping_fee = len(seller_orders) * 45.00  # Flat fee of 45.00 per seller
    # total_amount = subtotal + total_shipping_fee (JAVIER)

    seller_orders = {}
    products = Product.query.filter(Product.id.in_([item.product_id for item in cart_items])).all()
    product_dict = {product.id: product for product in products}

    for item in cart_items:
        product = product_dict.get(item.product_id)
        seller_id = product.seller_id
        seller_orders.setdefault(seller_id, []).append(item)

    subtotal = sum(item.price * item.quantity for item in cart_items)
    total_shipping_fee = len(seller_orders) * 45.00

    session['subtotal'] = subtotal
    session['total_shipping_fee'] = total_shipping_fee  

    # Apply voucher discount
    applied_discount = session.get('applied_discount', 0)
    discounted_total = subtotal + total_shipping_fee - applied_discount

    available_user_vouchers = UserVoucher.query.filter_by(user_id=current_user.id, claimed=True, is_archived=False).all()
    available_vouchers = [uv.voucher for uv in available_user_vouchers if uv.voucher.is_active and uv.voucher.expiration_date > datetime.utcnow()]


    user_addresses = UserAddress.query.filter_by(user_id=current_user.id).all()
    default_address = UserAddress.query.filter_by(user_id=current_user.id, is_default=True).first()

    if not user_addresses:
        flash('Please add a shipping address before proceeding to checkout.', 'danger')
        return redirect(url_for('account_address'))

    # Pass cart items, products, subtotal, shipping fee, and total amount to the checkout template
    return render_template('checkout.html',
                           cart=cart_items,
                           products=product_dict,
                           subtotal=subtotal,
                           shipping_fee=total_shipping_fee,
                            discounted_total=discounted_total,
                        #    total=total_amount,
                           address=user_addresses,
                           default_address=default_address,
                           available_vouchers=available_vouchers,
                           applied_discount=applied_discount)


@app.route('/buy_now/<int:product_id>', methods=['POST'])
def buy_now(product_id):
    try:
        if not current_user.is_authenticated:
            flash('Please log in to proceed with checkout.', 'danger')
            return redirect(url_for('login'))

        quantity = int(request.form.get('quantity', 1))
        selected_color = request.form.get('selected_color')
        selected_size = request.form.get('selected_size')

        # Check for price validity before converting to float
        price_str = request.form.get('price', None)
        if not price_str or price_str == '':
            flash('Error: Price not found or invalid.', 'danger')
            return redirect(url_for('product', product_id=product_id))

        try:
            price = float(price_str)  # Convert to float here
        except ValueError:
            flash('Error: Invalid price format.', 'danger')
            return redirect(url_for('product', product_id=product_id))


        # Fetch product and variation
        product = Product.query.get(product_id)
        if not product:
            flash('Product not found.', 'danger')
            return redirect(url_for('shop'))

        product_variation = ProductVariation.query.filter_by(
            product_id=product.id,
            color=selected_color,
            size=selected_size
        ).first()

        if not product_variation:
            flash('Selected product variation not available.', 'danger')
            return redirect(url_for('product', product_id=product_id))

        price = product_variation.price

        # Save checkout details in session
        session['checkout'] = {
            'product_id': product_id,
            'quantity': quantity,
            'color': selected_color,
            'size': selected_size,
            'price': price,
        }

        # Clear any applied voucher
        session.pop('applied_voucher_code', None)
        session.pop('applied_discount', None)


        user_addresses = UserAddress.query.filter_by(user_id=current_user.id).all()
        default_address = UserAddress.query.filter_by(user_id=current_user.id, is_default=True).first()

        if not user_addresses:
            flash('Please add a shipping address before proceeding to checkout.', 'danger')
            return redirect(url_for('account_address'))
        
        return redirect(url_for('checkout_single', 
                            product_id=product_id, 
                            quantity=quantity,
                            color=selected_color, 
                            size=selected_size, 
                            price=price,
                            address=user_addresses,
                            default_address=default_address))
    
    except Exception as e:
        flash('Error processing product variation.', 'danger')
        return redirect(url_for('shop'))


@app.route('/checkout_single', methods=['GET', 'POST'])
def checkout_single(voucher_code=None):
    if not current_user.is_authenticated:
        flash('Please log in to proceed with checkout.', 'danger')
        return redirect(url_for('login'))

    # Retrieve checkout data from session
    checkout_data = session.get('checkout')
    if not checkout_data:
        flash('Checkout session expired or invalid.', 'danger')
        return redirect(url_for('shop'))

    product_id = checkout_data['product_id']
    quantity = checkout_data['quantity']
    color = checkout_data['color']
    size = checkout_data['size']
    price = checkout_data['price']
    subtotal = quantity * price  # Initial subtotal without discount

    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('shop'))

    applied_discount = 0

    # Fetch available vouchers for the user
    available_user_vouchers = UserVoucher.query.filter_by(
        user_id=current_user.id, claimed=True, is_archived=False
    ).all()
    available_vouchers = [
        uv.voucher for uv in available_user_vouchers
        if uv.voucher.is_active and uv.voucher.expiration_date > datetime.utcnow()
    ]

    discounted_total = subtotal  # Default total is the full price

    # Handle voucher application or clearing
    if request.method == 'POST':
        if 'voucher_code' in request.form:
            voucher_code = request.form.get('voucher_code')

            if voucher_code:
                # Apply the voucher if valid
                voucher = Voucher.query.filter_by(code=voucher_code).first()
                if voucher:
                    user_voucher = UserVoucher.query.filter_by(user_id=current_user.id, voucher_id=voucher.id).first()
                    if user_voucher and user_voucher.claimed and not user_voucher.is_archived:
                        if voucher.is_active:
                            if voucher.voucher_type == 'shop':
                                if subtotal >= voucher.min_price:
                                        if voucher.discount_type == 'percentage':
                                            applied_discount += subtotal * (voucher.discount_amount / 100)
                                        elif voucher.discount_type == 'value':
                                            applied_discount += min(voucher.discount_amount, subtotal)

                            elif voucher.voucher_type == 'product':
                                if voucher.seller_id == product.seller_id and product in voucher.products:
                                    if subtotal >= voucher.min_price:
                                        if voucher.discount_type == 'percentage':
                                            applied_discount += subtotal * (voucher.discount_amount / 100)
                                        elif voucher.discount_type == 'value':
                                            applied_discount += min(voucher.discount_amount, subtotal)
                                    else:
                                        flash(f"Product voucher requires a minimum spent of {voucher.min_price}. You current total is  {subtotal}.", 'danger')

                            if applied_discount > 0:
                                discounted_total = subtotal - applied_discount
                                session['applied_voucher_code'] = voucher_code  # Save voucher code to session
                                flash(f'Voucher applied successfully: {voucher.voucher_name}', 'success')
                            else:
                                flash('Voucher is not eligible for this purchase.', 'danger')
                        else:
                            flash('Voucher is not active or has expired.', 'danger')
                else:
                    flash('Invalid or expired voucher.', 'danger')
            # Clear voucher if no voucher code is selected
            else:
                session.pop('applied_voucher_code', None)
                applied_discount = 0
                voucher_code = None
                discounted_total = subtotal

                # Reset product selection to default values
                checkout_data['color'] = product.variations[0].color  # Reset to first available color
                checkout_data['size'] = product.variations[0].size  # Reset to first available size
                checkout_data['price'] = product.variations[0].price  # Reset to default price
                session['checkout'] = checkout_data  # Save reset data in session

                flash('Voucher cleared successfully. Selections reset to default.', 'info')

    # Recalculate totals after discount (if any)
    discounted_total = round(subtotal - applied_discount, 2) if applied_discount else round(subtotal, 2)

    shipping_fee = 45.00  # Fixed shipping fee
    final_total = discounted_total + shipping_fee

    session['checkout'] = {
        'product_id': product_id,
        'quantity': quantity,
        'color': color,
        'size': size,
        'price': price,
        'discounted_total': discounted_total,
        'applied_discount': applied_discount,
    }

    return render_template(
        'checkout_single.html',
        product=product,
        quantity=quantity,
        color=checkout_data['color'],  # Use the reset color
        size=checkout_data['size'],  # Use the reset size
        price=checkout_data['price'],  # Use the reset price
        subtotal=subtotal,
        discounted_total=discounted_total,  # Product total after discount
        applied_discount=applied_discount,
        shipping_fee=shipping_fee,
        total_price=final_total,
        user_addresses=UserAddress.query.filter_by(user_id=current_user.id).all(),
        default_address=UserAddress.query.filter_by(user_id=current_user.id, is_default=True).first(),
        available_vouchers=available_vouchers,
        voucher_code=voucher_code,  # This should reflect the applied voucher
        voucher_locked=bool(voucher_code and applied_discount > 0)  # Lock the selection only if the voucher is applied and valid
    )



@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    if not current_user.is_authenticated:
        flash('Please log in to confirm your order.', 'danger')
        return redirect(url_for('login'))

    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash('Your cart is empty.', 'danger')
        return redirect(url_for('shop'))

    default_address = UserAddress.query.filter_by(user_id=current_user.id, is_default=True).first()
    if not default_address:
        flash('Please set a default address before confirming your order.', 'danger')
        return redirect(url_for('checkout'))

    # Retrieve totals
    subtotal = session.get('subtotal', 0)
    total_shipping_fee = session.get('total_shipping_fee', 0)
    final_total = subtotal + total_shipping_fee

    # Create orders
    order_ids = []
    seller_orders = {}
    for item in cart_items:
        seller_orders.setdefault(item.product.seller_id, []).append(item)

    for seller_id, items in seller_orders.items():
        order = Order(
            user_id=current_user.id,
            address_id=default_address.id,
            total_amount=final_total
        )
        db.session.add(order)
        db.session.flush()  # Get the order ID

        # Create order items for each seller
        for item in items:
            discounted = item.discounted if hasattr(item, 'discounted') else False  # Default to False if not set
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                discounted_price=final_total,
                seller_id=seller_id,
                color=item.color,
                size=item.size
            )
            db.session.add(order_item)

        order_ids.append(order.id)

    # Clear the cart
    CartItem.query.filter_by(user_id=current_user.id).delete()

    applied_voucher_code = session.get('applied_voucher_code')
    if applied_voucher_code:
        voucher = Voucher.query.filter_by(code=applied_voucher_code).first()
        if voucher:
            user_voucher = UserVoucher.query.filter_by(user_id=current_user.id, voucher_id=voucher.id).first()
            if user_voucher:
                user_voucher.is_archived = True  # Archive the voucher upon order confirmation

    # Clear the voucher and session data
    session.pop('applied_discount', None)
    session.pop('applied_voucher_code', None)

    db.session.commit()  # Commit all changes

    flash('Your orders have been placed successfully!', 'success')
    return redirect(url_for('order_summary', order_ids=','.join(map(str, order_ids))))



@app.route('/place_order', methods=['POST'])
def place_order():
    # Extract data from the form submission
    product_id = request.form.get('product_id')
    quantity = request.form.get('quantity', type=int)
    selected_color = request.form.get('selected_color')
    selected_size = request.form.get('selected_size')

    final_total = session.get('checkout', {}).get('discounted_total')
    applied_discount = session.get('checkout', {}).get('applied_discount')

    shipping_fee = 45.00  # Shipping fee (fixed)

    # Find the default address for the current user
    default_address = UserAddress.query.filter_by(user_id=current_user.id, is_default=True).first()

    if not default_address:
        flash('No default address found. Please add or select a default address.', 'danger')
        return redirect(url_for('user_profile'))  # Redirect to the user profile or address management page

    # Calculate the total price including shipping
    print(f"TOTAL PRICE GALING CHECKOUT SINGLE: {final_total}")
    total_price_with_shipping = final_total + shipping_fee
    print(f"Total Price (with shipping): {total_price_with_shipping}")

    # Create a new Order instance
    new_order = Order(
        user_id=current_user.id,
        total_amount=total_price_with_shipping,  # Store the total amount with shipping
        address_id=default_address.id,
        date_created=datetime.utcnow()
    )

    # Add the order to the session and flush to get the order ID
    db.session.add(new_order)
    db.session.flush()  # Flush so we can get new_order.id before committing

    # Get the product and seller details
    product = Product.query.get(product_id)
    seller_id = product.seller_id if product else None

    if not product or not seller_id:
        flash('Invalid product or seller information.', 'danger')
        return redirect(url_for('shop'))  # Redirect to the shop if the product is not found

    # Get the applied voucher code from session
    applied_voucher_code = session.get('applied_voucher_code')
    discounted_price = final_total  # Start with the non-discounted price

    if applied_voucher_code:
        # If a voucher is applied, calculate the discount
        voucher = Voucher.query.filter_by(code=applied_voucher_code).first()
        if voucher:
            # Apply the voucher discount logic
            if voucher.discount_type == 'percentage':
                discounted_price -= final_total * (voucher.discount_amount / 100)
            elif voucher.discount_type == 'value':
                discounted_price -= min(voucher.discount_amount, final_total)

    # Ensure the discounted price is not negative
    discounted_price = max(0, discounted_price)

    # Create a new OrderItem instance
    new_order_item = OrderItem(
        order_id=new_order.id,  
        product_id=product_id,
        quantity=quantity,
        price=final_total,  # This is the original price before any discount
        discounted_price=discounted_price,  # This is the final price after discount
        seller_id=seller_id,
        color=selected_color,  # Store the selected color
        size=selected_size     # Store the selected size
    )

    # Add the order item to the session
    db.session.add(new_order_item)

    # Archive the voucher if it's used
    if applied_voucher_code:
        user_voucher = UserVoucher.query.filter_by(user_id=current_user.id, voucher_id=voucher.id).first()
        if user_voucher:
            user_voucher.is_archived = True  # Archive the voucher upon order confirmation

    # Clear the voucher and session data
    session.pop('applied_discount', None)
    session.pop('applied_voucher_code', None)

    # Commit the changes to the database
    db.session.commit()

    # Flash a success message
    flash('Order placed successfully!', 'success')

    # Redirect to a relevant page, e.g., order confirmation or product page
    return redirect(url_for('user_ToPay'))  # Replace 'shop' with your target function




# FLUTTER ROUTES START HERE :)))
jwt_secret_key = app.config["JWT_SECRET_KEY"]


@app.route('/test', methods=['GET'])
def test_connection():
    return jsonify({"message": "Your Flask server is working!"})


# Reuse for requried
@app.route("/api/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()  # Extract user data from token
    return jsonify({"message": "Welcome!", "user": current_user}), 200



# @jwt_required() -- Protect this route

@app.route("/api/login", methods=['POST'])
def api_login():
   
    data = request.get_json()  # Expecting JSON input
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400

    user = Users.query.filter_by(email=email).first()

    # Check if user exists, password matches, and is validated
    if user and bcrypt.check_password_hash(user.password, password):

        if user.is_banned:
            return jsonify({"message": "Your account has been banned. Please contact support.", "status": "banned"}), 403
        
        if not user.is_validated:
            return jsonify({"message": "Account not validated. Please contact admin.", "status": "unvalidated"}), 403

        # Log in the user
        access_token = create_access_token(identity={"user_id": user.id, "role": user.role})


        # Return JSON response
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user_id": user.id,
            "role": user.role,  # Send user role for navigation
            "email": user.email
        }), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 401
    
    
    
    
@app.route("/admin/login/record")
@login_required
@role_required('admin')
def loginRecord():
    login_attempts = LoginAttempt.query.order_by(LoginAttempt.timestamp.desc()).all()
    return render_template('LoginRecord.html', title="Login Record", login_attempts=login_attempts)