from hashlib import md5
import bson
from fastapi.responses import RedirectResponse, HTMLResponse

from common import short_url_to_long, create_short_url
from mongo_db import db

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI()

def create_hash_password(password: str):
    return md5(password.encode('utf-8')).hexdigest()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


async  def get_user_by_token(token: str):
    user_dict = await db.users.find_one({'_id': bson.ObjectId(token)})
    if user_dict:
         return UserInDB(**user_dict)


async def fake_decode_token(token):
    user = await  get_user_by_token(token)
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = await fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = await db.users.find_one({"username": form_data.username})
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = create_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = str(user_dict["_id"])
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    return current_user


@app.get("/", response_class=HTMLResponse)
async def read_items():
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <form method="POST">
                <input type="text" name="long_url" value="https://www.google.com" />
                <input type="submit">
                <p>
                <a href="/premium/">Try our premium option </a>
                <p>
            </form>
        </body>
    </html>
    """

@app.post("/")
async def generate_short_url(long_url:Annotated[str, Form()]):
    result = await create_short_url(long_url)
    return result

@app.get("/{short_url}")
async def get_destination_url(short_url:str):
    link_data = await short_url_to_long(short_url)
    return RedirectResponse(link_data)


@app.post("/{short_url}")
async def update_short_url(short_url:str, new_long_url:Annotated[str, Form()]):
    original_link = await db.link.find_one({"short_url":short_url})
    new_long_url = {"long_url": new_long_url}
    result = await db.link.update_one({"_id":original_link['_id']}, {"$set": new_long_url })
    return result



@app.get("/premium/", response_class=HTMLResponse)
async def read_items():
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <form method="POST">
                <input type="text" name="long_url" value="" placeholder="type your URL" />
                <input type="text" name="premium_short_url" value="" placeholder="type your custom URL" />
                <input type="submit">
            </form>
        </body>
    </html>
    """
@app.post("/premium/", response_class=HTMLResponse)
async def add_short_url(long_url:Annotated[str, Form()], premium_short_url:Annotated[str, Form()]):
    if await db.link.find_one({"short_url":premium_short_url}):
        return "This URL already exists"
    else:
        new_link = await db.link.insert_one({"short_url":premium_short_url, "long_url":long_url})
        return premium_short_url