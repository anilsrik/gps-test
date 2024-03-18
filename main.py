import logging

from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Request, Header
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
import sqlalchemy as sa
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GpsCoords(BaseModel):
    lat: str
    long: str


app = FastAPI()

DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
   db = SessionLocal()
   try:
      yield db
   finally:
      db.close()

# A SQLAlchemny ORM Place
class DBCoords(Base):
    __tablename__ = 'geocoords'
    __table_args__ = {'schema' : 'public'}
    id = sa.Column(sa.Integer(), primary_key=True, index=True)
    user_id = sa.Column(sa.Integer())
    lat = sa.Column(sa.String())
    long = sa.Column(sa.String())
    user_agent = sa.Column(sa.String())


# A SQLAlchemny ORM Place
class DBUsers(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema' : 'public'}
    id = sa.Column(sa.Integer(), primary_key=True, index=True)
    name = sa.Column(sa.String())
    authkey = sa.Column(sa.String())



def verify_token(req: Request):
    token = req.headers["Authorization"]
    # Here your code for verifying the token or whatever you use
    if token != "a510e951d4b9b39d0167b26cc42ddf6a":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    return True


def get_user_id(db: Session, authkey: str):
    return db.query(DBUsers).where(DBUsers.authkey == authkey).first()

def create_place(db: Session, useragent: str, user_id: int, gpscoords: GpsCoords):
    db_coords = DBCoords()
    db_coords.lat = gpscoords.lat
    db_coords.long = gpscoords.long
    db_coords.user_agent = useragent[0:200]
    db_coords.user_id = user_id
    db.add(db_coords)
    db.commit()
    db.refresh(db_coords)
    return gpscoords


@app.post("/coords/", response_model=GpsCoords)
async def log_gps_cords(coords: GpsCoords, request: Request, user_agent: Annotated[str | None, Header()] = None, db: Session = Depends(get_db)):
    authkey = request.headers["Authorization"]
    logger.info("---------" + authkey)
    db_user = get_user_id(db, authkey)

    if db_user:
        create_place(db,useragent=user_agent, user_id=db_user.id, gpscoords=coords)
        return coords
    else:
         raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )
    
    
