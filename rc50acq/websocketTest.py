import json
import asyncio
import random
import datetime
import logging
import time
from websockets import connect

class Engine():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
        self.ws_config = {
            "host": "0.0.0.0",
            "port": 3002
        }

    async def do_initialize(self):
        self.logger.info("do_initialize() running")

        self.logger.info("Initializing WebSocket")
        # self.websocket = await connect('ws://0.0.0.0:3002')
        self.websocket = await connect('ws://rc50ws:3002')
        self.logger.info("Initialized WebSocket")
        return

    async def do_shutdown(self):
        return

    def active(self):
        return True

    async def sendHub(self):
        try:
            await self.websocket.send(json.dumps({
            'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'systemPressure': random.uniform(11, 15),
            'systemStatus': False,
            'temperature': random.uniform(23.0, 23.5),
            'humidity': random.uniform(56.1, 57.6),
            'pressureUnit': 'PSI',
            'pressureStatus': False,
            'targetPressure': 13,
            'pressureRange': 1.5,
            'runMode': False,
            'ch1Mode': 'TIMER',
            'ch2Mode': 'TIMER',
            'lowLevelCount': 10,
            'lowLevelStatus': 'FULL',
            'type': 'dispense'
        }, default=str))
        except Exception as e:
            self.logger.debug(f'sendHub(): could not send message because of {e}')
        else:
            self.logger.info('sendHub(): succsesfully sent message')

async def main():
    try:
        engine = Engine()
        await engine.do_initialize()
        while True:
            await engine.sendHub()
            await asyncio.sleep(10)
        # await connect('ws://0.0.0.0:3002', ping_interval = 1, ping_timeout = 1)
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    except KeyboardInterrupt or SystemExit:
        exit()

  
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()
    # loop.close()
    # while True:
    #     print('Testing!')
    #     time.sleep(300)
    