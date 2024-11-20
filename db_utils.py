from models import db, User
import bcrypt
from config import Config
from users import users  # Import the user dictionary

USERS_FILE = "users.py"


def initialize_db(app):
    """Initialize the database or configure development environment."""
    with app.app_context():
        if Config.ENV == "development":
            # Log for development environment
            app.logger.info(
                "Development mode: No database initialization required. Using users.py."
            )
        else:
            # Check and create tables if necessary for production
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if not tables:
                db.create_all()
                app.logger.info("Database initialized: Tables created.")
            else:
                app.logger.info("Database already initialized: Tables exist.")


def create_user(email, password):
    """Create a new user and add to the appropriate storage."""
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    if Config.ENV == "development":
        # Check if the email already exists in the in-memory users dictionary
        if email in users:
            raise ValueError("User already exists in development environment.")

        # Add user to the in-memory dictionary
        users[email] = hashed_password

        # Persist changes to the users.py file
        with open(USERS_FILE, "w") as file:
            file.write("users = {\n")
            for user_email, user_password in users.items():
                file.write(f'    "{user_email}": {user_password!r},\n')
            file.write("}\n")
    else:
        # Add to production database
        try:
            if User.query.filter_by(email=email).first():
                raise ValueError("User already exists.")
            new_user = User(email=email, password=hashed_password.decode("utf-8"))
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


def get_user_by_email(email):
    """Retrieve a user by their email."""
    if Config.ENV == "development":
        if email in users:
            return {"email": email, "password": users[email]}
        return None
    return User.query.filter_by(email=email).first()


def validate_user(email, password):
    """Validate a user's email and password."""
    user = get_user_by_email(email)
    if Config.ENV == "development" and user:
        return bcrypt.checkpw(password.encode("utf-8"), user["password"])
    if user and bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
        return True
    return False
