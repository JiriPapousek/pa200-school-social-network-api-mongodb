import os
import motor.motor_asyncio

MONGODB_CONNECTION_STR = os.getenv("CUSTOMCONNSTR_MONGODB")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_CONNECTION_STR)
db = client.pa200db