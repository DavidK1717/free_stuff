from app import create_app, db
from app.models import User, ListingSource, Listing


app = create_app()
application = app


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'ListingSource': ListingSource,
            'Listing': Listing}