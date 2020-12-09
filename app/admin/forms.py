from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, BooleanField, DateTimeField, HiddenField, IntegerField,PasswordField, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from ..models import Listing, ListingSource, User


def source_options():
    return ListingSource.query    


class ListingForm(FlaskForm):
    
    listing_date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email')
    source_id = QuerySelectField(label='Source', 
                                 query_factory = source_options,
                                 allow_blank=False, get_label='description')
    address_1 = StringField('Address line 1')
    address_2 = StringField('Address line 2')
    post_code = StringField('Post code')
    description = StringField('Description',
                              validators=[Length(min=5, max=140)])
    outgoing = BooleanField('Outgoing', default=False)                         
    submit = SubmitField('Submit')  

class ListingSourceForm(FlaskForm):
    description = TextAreaField('Description',
                            validators=[DataRequired(), Length(min=5, max=100)])
    submit = SubmitField('Submit')  

class AddUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
                                        DataRequired(),
                                        EqualTo('confirm_password')
                                        ])
    confirm_password = PasswordField('Confirm Password')
    is_admin = BooleanField('Admin', default=False)   
    submit = SubmitField('Submit')  

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username is already in use.')

class EditUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    is_admin = BooleanField('Admin', default=False)   
    submit = SubmitField('Submit')          
