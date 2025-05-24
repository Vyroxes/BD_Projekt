from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .book_collection import BookCollection
from .wishlist import WishList
from .token_blacklist import TokenBlacklist
from .subscription import Subscription