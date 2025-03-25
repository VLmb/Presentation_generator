from ctypes.wintypes import SIZEL
from idlelib.configdialog import FontPage

from init_database import db
from datetime import datetime

class Presentation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), nullable=False)
    name_of_presentation = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.String(50))
    updated_at = db.Column(db.String(50))
    slides = db.relationship('Slide', backref='presentation', lazy=True)


class Slide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    presentation_id = db.Column(db.Integer, db.ForeignKey('presentation.id'), nullable=False)
    theme = db.Column(db.String(200), nullable = False)
    title = db.Column(db.String(200), nullable=False)
    title_font = db.Column(db.Integer)
    title_font_size = db.Column(db.Integer)
    content = db.Column(db.Text, nullable=False)
    content_font = db.Column(db.Integer)
    content_font_size = db.Column(db.Integer)
    images = db.Column(db.JSON)  # Список URL изображений

# Главная таблица:
# - ID
# - Username
# - Name Of Presentation
# - Created at
# - Update at
#
# Таблица со слайдами:
# - ID
# - Presentation ID
# - Title
# - Title Font
# - Title Font Size
# - Content
# - Content Font
# - Content Font Size
# - Images url

