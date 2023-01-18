from pydantic import BaseModel


class FilmBase(BaseModel):
    title: str
    rating: int | None = None
    your_review: str | None = None

    class Config:
        orm_mode = True


class FilmBaseAll(FilmBase):

    id: int | None = None
    date_of_publication: str
    description: str
    image_url: str

    class Config:
        orm_mode = True