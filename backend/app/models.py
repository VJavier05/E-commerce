
from datetime import datetime, timezone, timedelta, date
from app import db, login_manager
from flask_login import UserMixin
from sqlalchemy import Nullable, Table, Column, Integer, ForeignKey


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))



pickup_orderitem = db.Table('pickup_orderitem',
    db.Column('pickup_id', db.Integer, db.ForeignKey('pickups.id'), primary_key=True),
    db.Column('order_item_id', db.Integer, db.ForeignKey('order_items.id'), primary_key=True)
)

class Users(db.Model, UserMixin):

    __tablename__ = 'users'


    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20),nullable=False,default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(50), default='user')  # Default role is 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_online = db.Column(db.Boolean, default=False) #bago


    date_of_birth = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    id_picture = db.Column(db.LargeBinary, nullable=False)  # Store image as binary data

    is_validated = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)


    is_disapproved = db.Column(db.Boolean, default=False)  # New column for archiving disapproved users


    disapproval_reason = db.Column(db.String(255), nullable=True) 


    is_banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.String(255), nullable=True)
    
    # Relationships
    admin = db.relationship('Admin', backref='user', uselist=False)
    seller = db.relationship('Seller', backref='user', uselist=False)
    addresses = db.relationship('UserAddress', backref='user', lazy=True) 
    courier = db.relationship('Courier', back_populates='user', uselist=False)
    reviews = db.relationship('Review', back_populates='user', cascade="all, delete-orphan")

    user_notification = db.relationship("UserNotification", back_populates="user")
    user_vouchers = db.relationship("UserVoucher", back_populates="user")



class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120))
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, nullable=False)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    user = db.relationship('Users', backref='login_attempts')



class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    total_admin_income = db.Column(db.Float, default=0.0) 
    total_shipping_income = db.Column(db.Float, default=0.0)
    # Additional fields specific to admins if needed


class Seller(db.Model):
    __tablename__ = 'sellers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    shop_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    barangay = db.Column(db.String(100), nullable=False)
    street = db.Column(db.String(150), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    business_id = db.Column(db.LargeBinary, nullable=True)  # Now storing binary data for the business ID file
    policy_accepted = db.Column(db.Boolean, nullable=False, default=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    image_file = db.Column(db.String(20),nullable=False,default='default.jpg')

    total_income = db.Column(db.Float, default=0.0)
    


    def __repr__(self):
        return f'<Shop {self.shop_name}>'





class UserAddress(db.Model):
    __tablename__ = 'user_addresses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key for the Users table
    address_name = db.Column(db.String(255), nullable=False)

    street = db.Column(db.String(255), nullable=False)
    barangay = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(100), nullable=False)

    postal_code = db.Column(db.String(20), nullable=False)
    telephone_no = db.Column(db.String(20), nullable=True) 

    is_default = db.Column(db.Boolean, default=False)

    def __init__(self, user_id, address_name ,street, barangay, city, province, region ,postal_code, telephone_no=None):
        self.user_id = user_id
        self.address_name = address_name
        self.street = street
        self.barangay = barangay
        self.city = city
        self.province = province
        self.region = region
        self.postal_code = postal_code
        self.telephone_no = telephone_no



class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    material = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False)  # Add seller_id field

    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # New column for tracking when the product was added


    # Relationship to ProductVariation
    variations = db.relationship('ProductVariation', backref='product', cascade='all, delete-orphan', lazy=True)

     # Relationship to ProductImage
    images = db.relationship('ProductImage', backref='product', cascade='all, delete-orphan', lazy=True)

    seller = db.relationship('Seller', backref='products')  # Add relationship to Seller
    reviews = db.relationship('Review', back_populates='product', cascade="all, delete-orphan")
    notification = db.relationship("Notification", back_populates="product")




# ProductVariation table: Holds the variation information for each product
class ProductVariation(db.Model):
    __tablename__ = 'product_variation'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

class ProductImage(db.Model):
    __tablename__ = 'product_image'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)



class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Foreign key to User model
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # Foreign key to Product model
    quantity = db.Column(db.Integer, default=1, nullable=False)
    color = db.Column(db.String(50), nullable=True)  # Optional: for product color variations
    size = db.Column(db.String(50), nullable=True)  # Optional: for product size variations
    price = db.Column(db.Float, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='cart_items')

    def __repr__(self):
        return f'<CartItem {self.product_id} - Qty: {self.quantity}>'
    


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Float, nullable=False)
    discounted_price = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False)

    color = db.Column(db.String(50), nullable=True)  
    size = db.Column(db.String(10), nullable=True)  
    status = db.Column(db.String(20), default='Pending')
    cancel_reason = db.Column(db.String(255))
    
    # Relationship with the Product model
    
    product = db.relationship('Product', backref='order_items')
    seller = db.relationship('Seller', backref='orders')

    def update_seller_income(self, seller_shipping_fee):
        """
        Update the seller's income, admin's 5% commission from product sales,
        and admin's shipping fee based on each seller's shipping fee.
        """
        # print(f"Updating income for order_item: {self.id}")
        if self.status == 'Delivered':  # When order item is delivered
            # Calculate seller's income (only product portion, not shipping)
            income = self.price * self.quantity

              # Calculate 5% commission for the admin from the product sales portion
            admin_commission = income * 0.05  # 5% of this item's product sales only

            net_income = income - admin_commission
            # print(f"Calculated income: {income}, Admin commission: {admin_commission}, Net income: {net_income}")


            if self.seller.total_income is None:
                self.seller.total_income = 0.0  # Initialize to 0.0 if None
            self.seller.total_income += net_income  # Update seller's income
            # print(f"Seller total income updated to: {self.seller.total_income}")

            
            courier = self.order.courier  # Access the courier assigned to this order
            # print(f"Courier: {courier.id}")

            courier_cut = seller_shipping_fee * 0.40  # Courier gets 20% of the shipping fee
            admin_shipping_income = seller_shipping_fee - courier_cut  # Remaining shipping income for admin

            if courier and hasattr(courier, 'total_shipping_income'):  # Ensure courier exists and has total_income
                if courier.total_shipping_income is None:
                    courier.total_shipping_income = 0.0  # Initialize if None
                courier.total_shipping_income += courier_cut
                # print(f"Updated courier income: {courier.total_shipping_income}")
          
            
            # Update the admin's total income and shipping income
            admin = Admin.query.first()  # Assuming there's only one admin
            if admin:
                if admin.total_admin_income is None:
                    admin.total_admin_income = 0.0
                if admin.total_shipping_income is None:
                    admin.total_shipping_income = 0.0
                
                # Update admin's commission and shipping income
                admin.total_admin_income += admin_commission
                admin.total_shipping_income += admin_shipping_income  # Add seller's shipping fee
                # print(f"Admin income updated: Admin total income = {admin.total_admin_income}, Shipping income = {admin.total_shipping_income}")


            db.session.commit()    # Commit the transaction to save changes

    def __repr__(self):
        return f'<OrderItem {self.product_id} - Qty: {self.quantity}>'
    

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Assuming you have a User model

    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    address_id = db.Column(db.Integer, db.ForeignKey('user_addresses.id'), nullable=False)  # Link to UserAddress
    courier_id = db.Column(db.Integer, db.ForeignKey('couriers.id'), nullable=True, default=None)  # Link to Courier

    total_amount = db.Column(db.Float, nullable=False)

    
    # Relationship with the OrderItem model
    user = db.relationship('Users', backref='orders')
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

    # ADDED A RELATION HERE (INCASE ERROR DEL)
    address = db.relationship('UserAddress', backref='orders')

    def __repr__(self):
        return f'<Order {self.id} - Total: {self.total_amount}>'


class Courier(db.Model):
    __tablename__ = 'couriers'
    
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(db.Boolean, default=True)
    service_area = db.Column(db.String(255), nullable=True)
    vehicle_type = db.Column(db.String(50), nullable=True)
    vehicle_registration_no = db.Column(db.String(50), nullable=True)
   
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)  # Foreign key to Users
    contact_number = db.Column(db.String(20), nullable=True)
    # New address fields
    street = db.Column(db.String(255), nullable=True)
    barangay = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    province = db.Column(db.String(100), nullable=True)
    region = db.Column(db.String(100), nullable=True)

    total_shipping_income = db.Column(db.Float, default=0.0)

    # Relationship with Order
    orders = db.relationship('Order', backref='courier', lazy=True)
    user = db.relationship('Users', back_populates='courier') 


    def __repr__(self):
        return f'<Courier {self.name}>'
    


class Pickup(db.Model):
    __tablename__ = 'pickups'

    id = db.Column(db.Integer, primary_key=True)
    scheduled_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="Pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at = db.Column(db.DateTime, nullable=True)


    delivery_image = db.Column(db.LargeBinary, nullable=True)

    # Relationships
    courier_id = db.Column(db.Integer, db.ForeignKey('couriers.id'), nullable=True)
    courier = db.relationship('Courier', backref=db.backref('pickups', lazy=True))
    
    # Link to OrderItems through the association table
    order_items = db.relationship('OrderItem', secondary=pickup_orderitem, backref=db.backref('pickups', lazy=True))



class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # e.g., 1 to 5 stars
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    verified_purchase = db.Column(db.Boolean, default=False)  # Indicates if the review is from a verified purchase
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Constraints and Indexes
    __table_args__ = (
        db.CheckConstraint('rating BETWEEN 1 AND 5', name='valid_rating'),
        db.Index('idx_product_reviews', 'product_id'),
        db.Index('idx_user_reviews', 'user_id'),
    )

    # Relationships
    user = db.relationship('Users', back_populates='reviews')
    product = db.relationship('Product', back_populates='reviews')
    images = db.relationship('ReviewImage', back_populates='review', cascade='all, delete-orphan')


    def __repr__(self):
        return f'<Review {self.title} - Rating: {self.rating}>'


class ReviewImage(db.Model):
    __tablename__ = 'review_images'

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)

    review = db.relationship('Review', back_populates='images')

    def __repr__(self):
        return f'<ReviewImage {self.image_path}>'















#bago


class StockHistory(db.Model):
    __tablename__ = 'stock_history'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    stock_change = db.Column(db.Integer, nullable=False)  # Positive or negative stock changes
    previous_stocks = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # When the change happened
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)  # Link to the order

    # Relationships for easy querying
    product = db.relationship('Product', backref=db.backref('stock_history', lazy=True))
    seller = db.relationship('Seller', backref=db.backref('stock_changes', lazy=True))
    user = db.relationship('Users', backref=db.backref('stock_changes', lazy=True))
    order = db.relationship('Order', backref=db.backref('stock_history', lazy=True))

    def __repr__(self):
        return f"<StockHistory product_id={self.product_id}, stock_change={self.stock_change}, date={self.date}>"


class Messages(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_archived = db.Column(db.Boolean, default=False)
    is_seen = db.Column(db.Boolean, default=False)  # Track if the message has been seen
    file_path = db.Column(db.String(255), nullable=True)  # Store the file path


    sender = db.relationship('Users', foreign_keys=[sender_id], backref='messages_sent')
    receiver = db.relationship('Users', foreign_keys=[receiver_id], backref='messages_received')

class Notification(db.Model):
    __tablename__ = 'notification'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)  # New title field
    message = db.Column(db.String(255), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=True)
    notification_type = db.Column(db.Enum('message', 'promotion', name='notification_type'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Establish relationship to the association table
    product = db.relationship('Product', back_populates='notification')  # Adjust according to your relationship
    user_notification = db.relationship("UserNotification", back_populates="notification")

class UserNotification(db.Model):
    __tablename__ = 'user_notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    notification_id = db.Column(db.Integer, db.ForeignKey('notification.id'), nullable=False)
    seen = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    viewed_at = db.Column(db.DateTime, default=None)

    # Establish relationships for back-population
    user = db.relationship("Users", back_populates="user_notification")
    notification = db.relationship("Notification", back_populates="user_notification")

class StockNotification(db.Model):
    __tablename__ = 'stock_notification'

    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    message = db.Column(db.String(255), nullable=False)
    seen = db.Column(db.Boolean, default=False)  # Track if the notification has been seen

    # Define relationships for easy querying if needed
    seller = db.relationship('Seller', backref='stock_notifications')
    product = db.relationship('Product', backref='notifications')

    def __repr__(self):
        product_name = self.product.name if self.product else "Unknown Product"
        return f"<StockNotification {product_name} - {self.stock} units left>"

# Define a many-to-many association table for vouchers and products
voucher_product = Table(
    'voucher_product',
    db.Model.metadata,
    Column('voucher_id', Integer, ForeignKey('vouchers.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('product.id'), primary_key=True)
)

# Define a many-to-many association table for vouchers and products
class Voucher(db.Model):
    __tablename__ = 'vouchers'

    id = db.Column(db.Integer, primary_key=True)
    voucher_name = db.Column(db.String(20), nullable=False)
    voucher_type = db.Column(db.String(20), nullable=False)
    code = db.Column(db.String(20), nullable=False, unique=True)
    discount_type = db.Column(db.Enum('percentage', 'value', name='discount_type'), nullable=False)  # Type of discount
    discount_amount = db.Column(db.Float, nullable=False)  # Percentage off or cash value
    min_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    is_archived = db.Column(db.Boolean, default=False)

    # Foreign key to link Voucher to a Seller
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'), nullable=False)
    seller = db.relationship('Seller', backref='vouchers')  # Relationship to Seller

    # Establish relationship to UserVoucher
    user_vouchers = db.relationship("UserVoucher", back_populates="voucher")

    products = db.relationship('Product', secondary=voucher_product, backref='vouchers')


    def __repr__(self):
        return f'<Voucher {self.code} - {self.discount_amount} {self.discount_type}>'

    # Check if voucher is active based on current date
    @property
    def is_active(self):
        now = datetime.utcnow()
        return self.start_date <= now <= self.expiration_date

    # Property to check if the voucher is near expiration (within 1 week)
    @property
    def is_near_expiration(self):
        now = datetime.utcnow()
        return self.expiration_date - now <= timedelta(weeks=1) and now < self.expiration_date

    # Method to archive vouchers that are near expiration
    def archive_if_near_expiration(self):
        if self.is_near_expiration:
            self.is_archived = True
            db.session.commit()

    # Method to archive vouchers if near expiration or quantity is zero
    def archive_if_needed(self):
        if self.quantity == 0:
            self.is_archived = True
            db.session.commit()

class UserVoucher(db.Model):
    __tablename__ = 'user_voucher'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    voucher_id = db.Column(db.Integer, db.ForeignKey('vouchers.id'), nullable=False)
    claimed = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    claimed_at = db.Column(db.DateTime, default=None)

    # Establish relationships for back-population
    user = db.relationship("Users", back_populates="user_vouchers")
    voucher = db.relationship("Voucher", back_populates="user_vouchers")

def archive_near_expiration_vouchers():
    vouchers = Voucher.query.all()
    for voucher in vouchers:
        if voucher.is_near_expiration:
            voucher.is_archived = True
    db.session.commit()

# Function to archive vouchers that are near expiration or have zero quantity
def archive_vouchers():
    vouchers = Voucher.query.all()
    for voucher in vouchers:
        voucher.archive_if_needed()
    db.session.commit()