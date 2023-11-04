import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://root:example@mongo_host:27017')
db = client.link_shortener