from init_database import db
from datetime import datetime


class Presentation(db.Model):
    __tablename__ = 'presentation'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False, index=True)
    name_of_presentation = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    slides = db.relationship('Slide', backref='presentation', lazy='select', cascade="all, delete-orphan")


class Slide(db.Model):
    __tablename__ = 'slide'
    id = db.Column(db.Integer, primary_key=True)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentation.id'), nullable=False, index=True)
    theme = db.Column(db.String(200), nullable=False, default="Default Theme")
    title = db.Column(db.String(200), nullable=False, default="Untitled Slide")
    title_font = db.Column(db.String(100), default="Arial")
    title_font_size = db.Column(db.Integer, default=24)
    content = db.Column(db.Text, nullable=True)
    content_font = db.Column(db.String(100), default="Arial")
    content_font_size = db.Column(db.Integer, default=14)
    images = db.Column(db.JSON, nullable=True)