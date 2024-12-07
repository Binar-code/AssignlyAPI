from fastapi import FastAPI
from sqlalchemy import create_engine
from models import *
from sqlalchemy.orm import sessionmaker
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import secrets

OK = 200
ACCEPTED = 202
UNAUTHORIZED = 401
NOT_FOUND = 404

DB_URL = "sqlite:///database.db"

tokens = []

engine = create_engine(
    DB_URL, connect_args={"check_same_thread": False}
)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autoflush=True, bind=engine)
db = SessionLocal()

app = FastAPI()


def auth(token):
    is_auth = False
    for item in tokens:
        if item['id'] == token:
            is_auth = True
    
    return is_auth


# Auth
@app.get("/login/{login}/{psw}")
def login(login, psw):
    user = db.query(User).filter(User.login == login).first()
    if (user == None):
        return NOT_FOUND
    
    if (user.password != psw):
        return UNAUTHORIZED

    data = {
        'id': user.id,
        'token': secrets.token_hex()
    }

    json = jsonable_encoder(data)
    tokens.append(data)

    return JSONResponse(content=json)


# Groups list
@app.get('.groups/{token}/{user_id}')
def groups_list(token, user_id):
    if auth(token):
        pass
    else:
        return UNAUTHORIZED
    
    
