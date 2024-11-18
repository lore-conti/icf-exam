from models import db, User
import bcrypt
from config import Config
from users import users  # Import the user dictionary

def create_user(email, password):
    """Create a new user and add to the database."""
    if Config.ENV != 'development':
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

def get_user_by_email(email):
    """Retrieve a user by their email."""
    if Config.ENV == 'development':
        return {"email": email, "password": users.get(email)} if email in users else None
    return User.query.filter_by(email=email).first()

def validate_user(email, password):
    """Validate a user's email and password."""
    user = get_user_by_email(email)
    if Config.ENV == 'development' and user:
        return bcrypt.checkpw(password.encode("utf-8"), user["password"])
    if user and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return True
    return False
