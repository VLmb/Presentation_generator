from init_database import db
from datetime import datetime

class Presentation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    name_of_presentation = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    slides = db.relationship('Slide', backref='presentation', lazy=True)

class Slide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentation.id'), nullable=False)
    theme = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    title_font = db.Column(db.String(100))
    title_font_size = db.Column(db.Integer)
    content = db.Column(db.Text, nullable=False)
    content_font = db.Column(db.String(100))
    content_font_size = db.Column(db.Integer)
    images = db.Column(db.JSON)