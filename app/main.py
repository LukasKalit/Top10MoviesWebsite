#WTForms
from starlette_wtf import CSRFProtectMiddleware, csrf_protect
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

#core import
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse

#Jinja2
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

#SQL
from sqlalchemy.orm import Session

#Others
from typing import List
import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

#my imports
from .import crud, models, schemas
from .database import SessionLocal, engine




API_KEY = os.getenv("API_KEY")

models.Base.metadata.create_all(bind=engine)

app = FastAPI(middleware=[
    Middleware(SessionMiddleware, secret_key="don't look at me"),
    Middleware(CSRFProtectMiddleware, csrf_secret="don't look at me")
])

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Main site, list of films
@app.get("/", response_model=List[schemas.FilmBaseAll])
def home(request:Request, db: Session = Depends(get_db)):

    #Empty database exception
    film_list = crud.get_films(db)
    if film_list == []:
        film_example = schemas.FilmBaseAll(
            id= None,
            title= "Your database is empty. Fill database with your films",
            date_of_publication= "empty data",
            rating= 0,
            your_review= "empty data",
            description= "empty data",
            image_url= "empty data")
        film_list = [film_example]

    return templates.TemplateResponse("index.html", {"request":request, "data":film_list})

#Edit film in database
@app.get("/edit/{id}")
async def update(id:str, request:Request, db:Session = Depends(get_db)):
    #WTForm assigment
    form = models.EditForm(request)

    #Taking information about film from database
    try:
        id = int(id)
        edited_film = crud.get_film(db, id)
    except:
        return HTTPException(status_code=404, detail="No data in database")
    
    return templates.TemplateResponse("edit.html", {"request":request, "data":edited_film, "form":form})

@app.post("/edit/{id}", response_model=schemas.FilmBase)
@csrf_protect
async def update(id:int, request:Request, db:Session = Depends(get_db)):
    #WTForm assigment
    form = await models.EditForm.from_formdata(request)

    #WTForm validation
    if await form.validate_on_submit():
        form.querry_errors = ""
        check_success_update = crud.update_review(db, id, data=form)
        if not check_success_update:
            return HTTPException(status_code=406, detail="can't update film")
        else:
            response = RedirectResponse(url='/')
            response.status_code = 302
            return response
    
    try:
        id = int(id)
        edited_film = crud.get_film(db, id)
    except:
        return HTTPException(status_code=404, detail="No data in database")

    return templates.TemplateResponse("edit.html", {"request":request, "data":edited_film, "form":form})

#Deleting film form database
@app.get("/delete/{id}")
def delete(id:str, request:Request, db:Session = Depends(get_db)):

    try:
        id = int(id)
        check_success_delete = crud.delete_film(db, id)
    except:
        return HTTPException(status_code=404, detail="No data in database")

    if not check_success_delete:
        return HTTPException(status_code=406, detail="can't update film")
    else:
        response = RedirectResponse(url='/')
        response.status_code = 302
        return response


#Serching film from TMDB API
@app.get("/add_movie/")
def add_movie(request:Request, db:Session = Depends(get_db)):
    #WTForm assigment
    form = models.AddMovieForm(request)

    return templates.TemplateResponse("add.html", {"request":request, "form":form})


@app.post("/add_movie/")
@csrf_protect
async def add_movie(request:Request, db:Session = Depends(get_db)):
    #WTForm assigment
    form = await models.AddMovieForm.from_formdata(request)

    #WTForm validation
    if await form.validate_on_submit():

        #Taking information about movie from TMDB
        TMDB_request = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language=en-US&query={form.title.data}&page=1&include_adult=false'
        TMDB_response = requests.get(TMDB_request)

        if TMDB_response.status_code == 200:
            json_object = json.loads(TMDB_response.content.decode('utf-8'))
                
            return templates.TemplateResponse("select.html", {"request":request, "json_obj":json_object['results']})
        else:
            print("error") 

    return templates.TemplateResponse("add.html", {"request":request, "form":form})

#Adding in background movie to database and redirecting
@app.get("/add_redirect/{external_id}")
def add_redirect(requst:Request,  external_id:int, db: Session = Depends(get_db)):

        TMDB_request = f"https://api.themoviedb.org/3/movie/{external_id}?api_key={API_KEY}&language=en-US"
        TMDB_response = requests.get(TMDB_request)
        json_object = json.loads(TMDB_response.content.decode('utf-8'))

        film_data = schemas.FilmBaseAll(
            id= None,
            title= json_object['title'],
            date_of_publication= json_object['release_date'],
            rating= None,
            your_review= "Add review",
            description= json_object['overview'],
            image_url= json_object['poster_path'])

        Duplicated = crud.check_title_exist(db=db, title=json_object['title'])
        if Duplicated:
            crud.add_film(db=db, data=film_data)
            film_in_db = crud.get_film_by_title(db=db, title=film_data.title)
            response = RedirectResponse(url=f'/edit/{film_in_db.id}')
            response.status_code = 302
            return response        
        else:
            print("film already exist")
            response = RedirectResponse(url='/')
            response.status_code = 302
            return response   


