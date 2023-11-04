from fastapi import FastAPI, Form
from typing import Annotated, Optional
from fastapi.responses import RedirectResponse, HTMLResponse

from common import short_url_to_long, create_short_url
from mongo_db import db

app = FastAPI()

dict_urls = {}
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