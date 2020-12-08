from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import case
# from sqlalchemy.orm import column_property
from sqlalchemy.ext.hybrid import hybrid_property
from app import db, login_manager
from datetime import datetime, timedelta


class User(UserMixin, db.Model):
    """
    Create a User 
    """

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    listings = db.relationship('Listing', backref='author', lazy='dynamic')

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def own_listings(self):
        return Listing.query.filter_by(user_id=self.id)        


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class ListingSource(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    description = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return self.id
    

class Listing(db.Model):  
    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True) 
    listing_date = db.Column(db.Date, index=True) 
    source_id = db.Column(db.Integer, db.ForeignKey('listing_source.id'))   
    description = db.Column(db.String(128))
    name = db.Column(db.String(50))
    email = db.Column(db.String(40))
    address_1 = db.Column(db.String(50))
    address_2 = db.Column(db.String(50))
    post_code = db.Column(db.String(10))    
    outgoing = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    modified_date= db.Column(db.DateTime, default=datetime.utcnow)
    source_name = db.column_property(
        db.select(
            [ListingSource.description],
            ListingSource.id == source_id
        )
    )       
    
    def __repr__(self):
        return '<Listing {}>'.format(self.description)   

    @hybrid_property
    def address(self):
        if self.address_2 != '':
            return self.address_1 + ", " + self.address_2 + ", " + self.post_code    
        else:
            return self.address_1 + ", " + self.post_code         

    @address.expression
    def address(cls):
        return case([
            (cls.address_2 != '', cls.address_1 + ", " + cls.address_2 + ", " + cls.post_code),
        ], else_ = cls.address_1 + ", " + cls.post_code)     


def get_listing_sources():
    return ListingSource.query.order_by(ListingSource.description)          
