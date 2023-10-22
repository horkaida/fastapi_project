import motor.motor_asyncio
from fastapi import FastAPI, Form
from typing import Annotated
import uuid
from fastapi.responses import RedirectResponse, HTMLResponse

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://root:example@localhost:27017')
db = client.link_shortener

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
async def get_short_url(long_url:Annotated[str, Form()]):
    short_url = str(uuid.uuid4())
    new_link = await db.link.insert_one({"short_url":short_url, "long_url":long_url})
    return short_url

@app.get("/{short_url}")
async def get_destination_url(short_url:str):
    link_data = await db.link.find_one({"short_url":short_url})
    return RedirectResponse(link_data['long_url'])


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
async def get_short_url(long_url:Annotated[str, Form()], premium_short_url:Annotated[str, Form()]):
    if await db.link.find_one({"short_url":premium_short_url}):
        return "This URL already exists"
    else:
        new_link = await db.link.insert_one({"short_url":premium_short_url, "long_url":long_url})
        return premium_short_url