from fastapi import FastAPI, Form
from typing import Annotated
import uuid
from fastapi.responses import RedirectResponse, HTMLResponse

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
                <input type="submit" value="Submit" />
            </form>
        </body>
    </html>
    """

@app.post("/")
async def get_short_url(long_url:Annotated[str, Form()]):
    short_url = str(uuid.uuid4())
    dict_urls[short_url] = long_url
    return short_url

@app.get("/{short_url}")
async def get_destination_url(short_url:str):
    print(dict_urls[short_url])
    return RedirectResponse(dict_urls[short_url])
