import json
import asyncio
import random
from async_eqp import RC50
import datetime
import logging
import time
import os
import socket
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

        self.dispense_count = 0
        self.program_in_progress = False
        self.dispense_test_in_process = False
        self.dispense_in_process = False
        
        self.alerts = {
            'lowLevel': datetime.datetime(2022, 1, 1),
            'pressure': datetime.datetime(2022, 1, 1),
            'general': datetime.datetime(2022, 1, 1)
            }

        self.state = {}
        self.config = {}
        self.data = {}

        self.change_func_list = {}

        self.RC50_config = {
            "host": "0.0.0.0",
            "port": 8088
        }

    async def do_initialize(self):
        self.logger.info("do_initialize() running")

        self.logger.info("do_initialize() connecting to RC50")
        self.reservoir = RC50(self.RC50_config['host'], self.RC50_config['port'], self.logger)
        if not (self.reservoir.conn):
            self.logger.info("do_initialize(): RC50 unable to connect")
            exit()
        self.logger.info("do_initialize(): connected to RC50")
        return

    async def do_shutdown(self):
        self.reservoir.close()
        return

    def active(self):
        return True

    async def sendHub(self, msg):
        try:
            print(msg)
            self.logger.info(f'sendHub() message sent at {datetime.datetime.now()}')
        except Exception as e:
            self.logger.debug(f'sendHub(): could not send message because of {e}')
        else:
            self.logger.info('sendHub(): succsesfully sent message')

    async def process_dataframe(self):
        old_data = self.reservoir.monitor_device(['R_MODE'])
        self.program_in_progress = old_data['runMode']
        if not self.program_in_progress:
            now = datetime.datetime.now()
            new_data = self.reservoir.monitor_device(['S_PRESSURE', 'R_PRESSURE_STATUS', 'R_MODE', 'S_LOW_LEVEL_STATUS', 'R_TARGET_PRESSURE', 'R_PRESSURE_RANGE', 'R_PRESSURE_UNIT'])
            status = self.reservoir.check_status(self.alerts)
            if status == False:
                if old_data != new_data:
                    if (now - self.alerts['general']).total_seconds() > 5:
                        await self.sendHub({
                                **new_data,
                                'type': 'alert'
                            })
                        self.alerts['general'] = now
                        return
                else: 
                    if (now - self.alerts['general']).total_seconds() > 60:
                        await self.sendHub({
                                **new_data,
                                'type': 'alert'
                            })
                        self.alerts['general'] = now
                        return
            else:
                if status['type'] == 'lowLevel':
                    self.alerts['lowLevel'] = now
                elif status['type'] == 'pressure':
                    self.alerts['pressure'] = now
                await self.sendHub({
                        **new_data,
                        'type': 'alert'
                    })
        else:
            now = datetime.datetime.now()
            new_data = self.reservoir.monitor_device(['S_PRESSURE', 'S_LOW_LEVEL_STATUS', 'R_CH1_DISPENSING'])
            status = self.reservoir.check_status(self.alerts)
            if status == False:
                if (now - self.alerts['general']).total_seconds() > 1:
                    await self.sendHub({
                            **new_data,
                            'type': 'alert'
                        })
                    self.alerts['general'] = now
                    return
            else:
                if status['type'] == 'lowLevel':
                    self.alerts['lowLevel'] = now
                elif status['type'] == 'pressure':
                    self.alerts['pressure'] = now
                await self.sendHub({
                        **new_data,
                        'type': 'alert'
                    })
        return

async def main():
    try:
        engine = Engine()
        await engine.do_initialize()
        while True:
            await engine.process_dataframe()
    except Exception as e:
        print("Unexpected error %s " % e)
        raise
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()