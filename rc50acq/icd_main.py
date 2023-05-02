import json
import asyncio
import random
from rc50 import RC50
import datetime
import logging
import time
import os
import socket
from websockets import connect  # type: ignore


class Engine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        self.dispense_count = 0
        self.program_in_progress = False
        self.dispense_test_in_process = False
        self.dispense_in_process = False

        self.alerts = {
            "lowLevel": datetime.datetime(2022, 1, 1),
            "pressure": datetime.datetime(2022, 1, 1),
            "general": datetime.datetime(2022, 1, 1),
        }

        self.state = {}
        self.config = {}
        self.data = {}

        self.change_func_list = {}

        # self.RC50_config = {"host": "192.168.1.5", "port": 8088}
        self.RC50_config = {"host": "0.0.0.0", "port": 8088}

    async def do_initialize(self):
        self.logger.info("do_initialize() running")

        self.logger.info("Initializing WebSocket")
        self.websocket = await connect("ws://rc50ws:3002", ping_interval=None)
        self.logger.info("Initialized WebSocket")

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(300)

        self.logger.info("binding to socket")

        self.sock.bind((self.RC50_config["host"], self.RC50_config["port"]))
        # self.sock.bind(("192.168.1.5", 8088))
        self.sock.listen()

        client: socket.socket
        address: tuple

        self.logger.info("waiting for connections")

        try:
            client, address = self.sock.accept()

            self.logger.info("connecting to RC50")
            self.reservoir = RC50(logger=self.logger, conn=client, addr=address)
            self.curr_data = self.reservoir.snapshot()
            if not (self.reservoir.conn):
                self.logger.info("do_initialize(): RC50 unable to connect")
                exit()
            self.logger.info("do_initialize(): connected to RC50")
            return
        except Exception as e:
            self.logger.error(e)

    async def do_shutdown(self):
        self.reservoir.close()
        return

    def active(self):
        return True

    async def sendHub(self, msg):
        try:
            self.logger.info(json.dumps(msg, default=str))
            await self.websocket.send(json.dumps(msg, default=str))
            self.logger.info(f"sendHub() message sent at {datetime.datetime.now()}")
        except Exception as e:
            self.logger.debug(f"sendHub(): could not send message because of {e}")
        else:
            self.logger.info("sendHub(): succsesfully sent message")

    async def process_dataframe(self):
        old_data = self.curr_data
        self.program_in_progress = old_data["runMode"]
        if not self.program_in_progress:
            now = datetime.datetime.now()
            new_data = self.reservoir.monitor_device(
                [
                    "S_PRESSURE",
                    "R_PRESSURE_STATUS",
                    "R_MODE",
                    "S_LOW_LEVEL_STATUS",
                    "R_TARGET_PRESSURE",
                    "R_PRESSURE_RANGE",
                    "R_PRESSURE_UNIT",
                    "R_CH1_DISPENSING",
                ]
            )

            if old_data["ch1Dispensing"] == True and new_data["ch1Dispensing"] == False:
                self.dispense_count = self.dispense_count + 1

            status = self.reservoir.check_status(self.alerts)
            if status == False:
                if old_data != new_data:
                    if (now - self.alerts["general"]).total_seconds() > 5:
                        await self.sendHub(
                            {
                                **new_data,
                                "dispenseCount": self.dispense_count,
                                "type": "alert",
                            }
                        )
                        self.alerts["general"] = now
                else:
                    if (now - self.alerts["general"]).total_seconds() > 60:
                        await self.sendHub(
                            {
                                **new_data,
                                "dispenseCount": self.dispense_count,
                                "type": "alert",
                            }
                        )
                        self.alerts["general"] = now
            else:
                if status["type"] == "lowLevel":
                    self.alerts["lowLevel"] = now
                elif status["type"] == "pressure":
                    self.alerts["pressure"] = now
                await self.sendHub(
                    {**new_data, "dispenseCount": self.dispense_count, "type": "alert"}
                )

        else:
            now = datetime.datetime.now()
            new_data = self.reservoir.monitor_device(
                [
                    "S_PRESSURE",
                    "R_PRESSURE_STATUS",
                    "R_MODE",
                    "S_LOW_LEVEL_STATUS",
                    "R_CH1_DISPENSING",
                ]
            )
            if old_data["ch1Dispensing"] == True and new_data["ch1Dispensing"] == False:
                self.dispense_count = self.dispense_count + 1
            status = self.reservoir.check_status(self.alerts)
            if status == False:
                if (now - self.alerts["general"]).total_seconds() > 1:
                    await self.sendHub(
                        {
                            **new_data,
                            "dispenseCount": self.dispense_count,
                            "type": "alert",
                        }
                    )
                    self.alerts["general"] = now
            else:
                if status["type"] == "lowLevel":
                    self.alerts["lowLevel"] = now
                elif status["type"] == "pressure":
                    self.alerts["pressure"] = now
                await self.sendHub(
                    {**new_data, "dispenseCount": self.dispense_count, "type": "alert"}
                )
        self.curr_data = new_data
        return

    async def on_program_change(self, status):
        if status:
            self.logger.info("on_program_change(): program started")
            self.program_in_progress = True
            self.dispense_test_in_process = False
            self.dispense_in_process = False
            self.reservoir.reinitialize()
        else:
            self.logger.info("on_program_change(): program ended")
            self.program_in_progress = False
        return

    # async def on_dispense_change(self, status):
    #     if self.dispense_test_in_process:
    #         if status:
    #             self.logger.info("on_dispense_change(): test dispense started")
    #             pass
    #         else:
    #             self.logger.info("on_dispense_change(): test dispense ended")
    #             pass

    #     else:
    #         if status:
    #             self.dispense_in_process = True
    #             self.dispense_count = self.dispense_count + 1
    #             self.logger.info("on_dispense_change(): dispense started")

    #         else:
    #             self.logger.info("on_dispense_change(): dispense ended")
    #             await self.sendHub(self.reservoir.snapshot())
    #             self.logger.info("Sent data to IoT Hub")
    #             pass
    #         return


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
