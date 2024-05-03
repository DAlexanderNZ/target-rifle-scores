from flask import session
from flask_login import LoginManager, UserMixin
import secrets
from app import app
from database import database


login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = secrets.token_hex()

class User(UserMixin, database):
    """ User class for flask_login. """
    def __init__(self, user_id, email, password, first_name, last_name):
        self.id = user_id
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
    
    def is_authenticated(self):
        """ Check if the user is authenticated. """
        return True
    
    def is_active(self):
        """ Check if the user is active. """
        return True
    
    def is_anonymous(self):
        """ Check if the user is anonymous. """
        return False
    
    def get_id(self):
        """ Get the user's id. """
        return self.id

def create_secret_key():
    """ Create a new secret key for each instance of the app. """
    return secrets.token_hex()

@login_manager.user_loader
def load_user(user_id):
    """ Load the user from the database. """
    return User(user_id)