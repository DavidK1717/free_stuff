from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from datetime import datetime, date
from . import admin
from app.admin.forms import ListingForm, ListingSourceForm, AddUserForm, EditUserForm
from .. import db
from ..models import User, ListingSource, Listing, get_listing_sources
from oauth2client.service_account import ServiceAccountCredentials
import gspread


def check_admin():
    # prevent non-admins from accessing the page
    if not current_user.is_admin:
        abort(403)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


# Listing Views

@admin.route('/listings', methods=['GET', 'POST'])
@login_required
def list_listings():
    """
    List all Listings
    """
    check_admin()

    listings = current_user.own_listings()

    return render_template('admin/listings/listings.html',
                           listings=listings, title="Listings")


@admin.route('/listings/add', methods=['GET', 'POST'])
@login_required
def add_listing():
    """
    Add a listing to the database
    """
    check_admin()

    add_listing = True

    form = ListingForm()
    if form.validate_on_submit():
        listing = Listing(description=form.description.data, author=current_user,
                          listing_date=form.listing_date.data, name=form.name.data, email=form.email.data,
                          address_1=form.address_1.data, address_2=form.address_2.data,
                          post_code=form.post_code.data, outgoing=form.outgoing.data,
                          source_id=form.source_id.data.id)

        db.session.add(listing)

        # flush not commit yet to get new db values for ss update
        db.session.flush()

        # spreadsheet update
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("Listings").sheet1

        row = [listing.id, current_user.username, form.listing_date.data.isoformat(), form.source_id.data.description,
               form.description.data, form.name.data, form.email.data, form.address_1.data, form.address_2.data,
               form.post_code.data, form.outgoing.data, json_serial(listing.created_date),
               json_serial(listing.modified_date)]
        index = 2
        sheet.insert_row(row, index)

        # add listing to the database

        db.session.commit()
        flash('You have successfully added a new listing.')

        # redirect to listings page
        return redirect(url_for('admin.list_listings'))

    # load listing template
    return render_template('admin/listings/listing.html', action="Add",
                           add_listing=add_listing, form=form,
                           title="Add Listing")


@admin.route('/listings/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_listing(id):
    """
    Edit a listing
    """
    check_admin()

    add_listing = False

    listing = Listing.query.get_or_404(id)
    form = ListingForm(obj=listing)
    if form.validate_on_submit():
        listing_date = form.listing_date.data
        listing.source_id = form.source_id.data.id
        listing.description = form.description.data
        author = current_user
        listing.name = form.name.data
        listing.email = form.email.data
        listing.address_1 = form.address_1.data
        listing.address_2 = form.address_2.data
        listing.post_code = form.post_code.data
        listing.outgoing = form.outgoing.data
        listing.modified_date = datetime.utcnow()

        # spreadsheet update
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("Listings").sheet1

        # find correct row
        cell = sheet.find(str(id), in_column=1)
        rownum = cell.row
        # delete row
        sheet.delete_row(rownum)
        # insert modified row at same place

        row = [listing.id, current_user.username, form.listing_date.data.isoformat(), form.source_id.data.description,
               form.description.data, form.name.data, form.address_1.data, form.email.data, form.address_2.data,
               form.post_code.data, form.outgoing.data, json_serial(listing.created_date),
               json_serial(listing.modified_date)]

        sheet.insert_row(row, rownum)

        db.session.commit()
        flash('You have successfully edited the listing.')

        # redirect to the listings page
        return redirect(url_for('admin.list_listings'))

    form.description.data = listing.description
    form.name.data = listing.name
    form.email.data = listing.email
    form.listing_date.data = listing.listing_date
    form.address_1.data = listing.address_1
    form.address_2.data = listing.address_2
    form.post_code.data = listing.post_code
    form.outgoing.data = listing.outgoing
    form.source_id.data = listing.source_id
    return render_template('admin/listings/listing.html', action="Edit",
                           add_listing=add_listing, form=form,
                           listing=listing, title="Edit Listing")


@admin.route('/listings/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_listing(id):
    """
    Delete a listing from the database
    """
    check_admin()

    listing = Listing.query.get_or_404(id)
    db.session.delete(listing)

    # delete from ss

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("Listings").sheet1

    # find correct row
    cell = sheet.find(str(id), in_column=1)
    rownum = cell.row
    # delete row
    sheet.delete_row(rownum)

    db.session.commit()
    flash('You have successfully deleted the listing.')

    # redirect to the listings page
    return redirect(url_for('admin.list_listings'))

    # return render_template(title="Delete Listing")


# User Views

@admin.route('/users')
@login_required
def list_users():
    """
    List all users
    """
    check_admin()

    users = User.query.all()
    return render_template('admin/users/users.html',
                           users=users, title='Users')


@admin.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    """
    Add a user to the database
    """
    check_admin()

    add_user = True

    form = AddUserForm()

    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    password=form.password.data,
                    is_admin=form.is_admin.data)

        db.session.add(user)

        db.session.commit()
        flash('You have successfully added a new user.')

        # redirect to listings page
        return redirect(url_for('admin.list_users'))

    # load listing template
    return render_template('admin/users/user.html', action="Add",
                           add_user=add_user, form=form,
                           title="Add User")


@admin.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    """
    Edit a user
    """
    check_admin()

    add_user = False

    user = User.query.get_or_404(id)
    form = EditUserForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.is_admin = form.is_admin.data

        db.session.commit()
        flash('You have successfully edited the user.')

        return redirect(url_for('admin.list_users'))

    form.username.data = user.username
    form.email.data = user.email
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    user.is_admin = form.is_admin.data

    return render_template('admin/users/user.html', action="Edit",
                           add_user=add_user, form=form,
                           user=user, title="Edit Users")


@admin.route('/users/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    """
    Delete a user from the database
    """
    check_admin()

    user = User.query.get_or_404(id)
    db.session.delete(user)

    db.session.commit()
    flash('You have successfully deleted the user.')

    # redirect to the user page
    return redirect(url_for('admin.list_users'))


# Listing sources

@admin.route('/lstingsources', methods=['GET', 'POST'])
@login_required
def list_listing_sources():
    """
    List all listing sources
    """
    check_admin()

    listingsources = ListingSource.query.all()

    return render_template('admin/listings/listingsources.html',
                           listingsources=listingsources, title="Listing Sources")


@admin.route('/listingsources/add', methods=['GET', 'POST'])
@login_required
def add_listing_source():
    """
    Add a listing source to the database
    """
    check_admin()

    add_listing_source = True

    form = ListingSourceForm()

    if form.validate_on_submit():
        listingsource = ListingSource(description=form.description.data)

        db.session.add(listingsource)

        db.session.commit()
        flash('You have successfully added a new listing source.')

        # redirect to listings page
        return redirect(url_for('admin.list_listing_sources'))

    # load listing template
    return render_template('admin/listings/listingsource.html', action="Add",
                           add_listing_source=add_listing_source, form=form,
                           title="Add Listing Source")


@admin.route('/listingsources/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_listing_source(id):
    """
    Edit a listing source
    """
    check_admin()

    add_listing_source = False

    listingsource = ListingSource.query.get_or_404(id)
    form = ListingSourceForm(obj=listingsource)
    if form.validate_on_submit():
        listingsource.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the listing.')

        return redirect(url_for('admin.list_listing_sources'))

    form.description.data = listingsource.description

    return render_template('admin/listings/listingsource.html', action="Edit",
                           add_listing_source=add_listing_source, form=form,
                           listingsource=listingsource, title="Edit Listing source")


@admin.route('/listingsources/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_listing_source(id):
    """
    Delete a listing source from the database
    """
    check_admin()

    listingsource = ListingSource.query.get_or_404(id)
    db.session.delete(listingsource)

    db.session.commit()
    flash('You have successfully deleted the listing source.')

    # redirect to the listing source page
    return redirect(url_for('admin.list_listing_sources'))
