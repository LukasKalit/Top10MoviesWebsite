from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "sqlite:C:\Users\Łukasz\Git\FastApi-SQL\PersonalLibrarysql_app.db"
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:lk1234589@127.0.0.1:5433/TopMoviesDatabase'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()