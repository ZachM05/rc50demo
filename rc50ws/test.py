
import asyncio
import logging
import motor.motor_asyncio
from pymongo import DESCENDING
from dateutil import parser

class DBHandler():
    def __init__(self):

        self.client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://root:rootpassword@0.0.0.0:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false')
        self.collection = self.client.rc50data.rc50data
        
    async def send_to_db(self) -> None:
        try:
            start = await self.collection.find_one(sort = [('timestamp', -1)])
            # dispenseCount = start['dispenseCount'] + 1 if 'dispenseCount' in start else 1
            print(start)
        except Exception as e:
            print(e)
    
if __name__ == '__main__': 

    server = DBHandler()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.send_to_db())
    loop.close()
