from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from . import models, schemas

def get_films(db: Session):
    return db.query(models.Film).order_by(models.Film.rating).all()


def get_film(db: Session, film_id: int):
    return db.query(models.Film).filter(models.Film.id == film_id).first()

def get_film_by_title(db: Session, title: str):
    return db.query(models.Film).filter(models.Film.title == title).first()


def check_title_exist(db: Session, title: str):
    object = db.query(models.Film).filter(models.Film.title == title).first()
    if object == None:        
        return True
    return False

def update_review(db: Session, id:int, data):
    db.query(models.Film).filter(models.Film.id == id).update({models.Film.rating: data.rating.data, models.Film.your_review: data.review.data}, synchronize_session="fetch")
    db.commit()
    return True

def delete_film(db:Session, id: int):
    db.query(models.Film).filter(models.Film.id == id).delete()
    db.commit()
    return True

def add_film(db:Session, data: schemas.FilmBaseAll):
    db_film = models.Film(**data.dict())
    db.add(db_film)
    db.commit()
    db.refresh(db_film)
    return 