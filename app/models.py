from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import case
# from sqlalchemy.orm import column_property
from sqlalchemy.ext.hybrid import hybrid_property
from app import db, login_manager
from datetime import datetime, timedelta
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base


meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

Base = declarative_base(metadata=meta)


class User(UserMixin, db.Model):
    """
    Create a User 
    """
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8','mysql_collate':'utf8_general_ci'}

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
    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8','mysql_collate':'utf8_general_ci'}

    id = db.Column(db.Integer, primary_key=True) 
    description = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return self.id
    

class Listing(db.Model):

    __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8','mysql_collate':'utf8_general_ci'}

    id = db.Column(db.Integer, primary_key=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True) 
    listing_date = db.Column(db.Date, index=True) 
    source_id = db.Column(db.Integer, db.ForeignKey('listing_source.id'))   
    description = db.Column(db.String(200))
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
