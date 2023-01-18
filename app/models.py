from starlette_wtf import StarletteForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms.validators	import DataRequired, Optional, Length, NumberRange

class EditForm(StarletteForm):
    rating = IntegerField('Full Name', [DataRequired(), NumberRange(0,10,"Number must be between 0 to 10") ] )
    review = TextAreaField('Mailing Address', [Optional(), Length(max=200)])

class AddMovieForm(StarletteForm):
    title = StringField('Movie Title', [DataRequired()])





from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, REAL
from sqlalchemy.orm import relationship

from .database import Base


class Film(Base):
    __tablename__= "films"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    date_of_publication = Column(String, index=True)
    rating = Column(REAL, index=True)
    your_review = Column(String, index=True)
    description = Column(String, index=True)
    image_url = Column(String, index=True)