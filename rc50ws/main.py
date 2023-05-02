import datetime
import json
from websockets import serve, WebSocketServerProtocol
import asyncio
import logging
import motor.motor_asyncio
from pymongo import DESCENDING
from dateutil import parser


class Server:
    def __init__(self, logger):
        self.logger = logger

        self.logger.info("__init__(): initializing motor client")
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            "mongodb://root:rootpassword@rc50db:27017/?authSource=admin&readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
        )
        self.collection = self.client.rc50data.rc50data
        self.logger.info("__init__(): initializied motor client")

    clients = set()

    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        self.logger.info(f"{ws.remote_address} joined")

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)
        self.logger.info(f"{ws.remote_address} left")

    async def send_to_clients(self, message: str) -> None:
        if self.clients:
            try:
                data = json.loads(message)
                start = await self.collection.find_one(sort=[("timestamp", -1)])
                if start:
                    # dispenseCount = start['dispenseCount'] if 'dispenseCount' in start else 1

                    msgData = {
                        **data,
                        # 'dispenseCount': dispenseCount,
                        "timestamp": parser.parse(data["timestamp"]),
                    }

                    result = await self.collection.insert_one(msgData)
                    self.logger.info("result %s" % repr(result.inserted_id))
                    await asyncio.wait(
                        [
                            asyncio.create_task(
                                client.send(
                                    json.dumps(
                                        {
                                            **data,
                                            # 'dispenseCount': dispenseCount
                                        }
                                    )
                                )
                            )
                            for client in self.clients
                        ]
                    )
                else:
                    result = await self.collection.insert_one(
                        {
                            **data,
                            # 'dispenseCount': 0,
                            "timestamp": parser.parse(data["timestamp"]),
                        }
                    )
                    self.logger.info("result %s" % repr(result.inserted_id))
                    await asyncio.wait(
                        [
                            asyncio.create_task(
                                client.send(
                                    json.dumps(
                                        {
                                            **data,
                                            # 'dispenseCount': 0
                                        }
                                    )
                                )
                            )
                            for client in self.clients
                        ]
                    )
            except Exception as e:
                self.logger.info(f"send_to_clients(): Error {e}")

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        async for message in ws:
            await self.send_to_clients(message)

    async def ws_handler(self, ws: WebSocketServerProtocol, uri: str) -> None:
        await self.register(ws)
        try:
            await self.distribute(ws)
        finally:
            await self.unregister(ws)


class WebSocket:
    def __init__(self, host: str, port: int, logger: logging.Logger = None):
        self.host = host
        self.port = port
        self.logger = logger
        self.server = False
        self.server = Server()

    async def connect(self):
        await serve(self.server.ws_handler, self.host, self.port, ping_interval=None)
        self.server = True


if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    logger.addHandler(ch)

    server = Server(logger)

    start_server = serve(server.ws_handler, "0.0.0.0", 3002, ping_interval=None)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.run_forever()
