from sqlalchemy import CheckConstraint
from . import db

class BookCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(500), nullable=False)
    genres = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    pages = db.Column(db.Integer, CheckConstraint('pages > 0 AND pages <= 9999'), nullable=False)
    isbn = db.Column(db.String(13), nullable=False)
    desc = db.Column(db.String(5000), nullable=False)
    rate = db.Column(db.Float, nullable=True)
    review = db.Column(db.String(100), nullable=True)

    def to_dict(self):
        new_date = self.date.strftime("%d-%m-%Y")

        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'cover': self.cover,
            'genres': self.genres,
            'date': new_date,
            'pages': self.pages,
            'rate': self.rate
        }
    
    def full_to_dict(self):
        new_date = self.date.strftime("%d-%m-%Y")

        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'cover': self.cover,
            'genres': self.genres,
            'publisher': self.publisher,
            'date': new_date,
            'pages': self.pages,
            'isbn': self.isbn,
            'rate': self.rate,
            'review': self.review,
            'desc': self.desc
        }