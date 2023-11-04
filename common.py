import uuid

from mongo_db import db

async def create_short_url(long_url, user_id=None ):
    short_url = str(uuid.uuid4())
    data = {"short_url": short_url, "long_url": long_url}
    if user_id:
        data.update({'user_id': user_id})
    await db.link.insert_one(data)
    return short_url


async def short_url_to_long(short_url:str):
    link_data = await db.link.find_one({"short_url":short_url})
    if not link_data:
        return 'does not exist'
    return link_data['long_url']


async def get_all_user_urls(user_id):
    link_data = await db.link.find({"user_id":user_id})
    return link_data