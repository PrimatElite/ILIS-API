from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..config import Config


engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


DeclarativeBase = declarative_base()
