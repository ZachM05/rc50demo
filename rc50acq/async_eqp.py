import json
import logging
import random
import socket
import time
from typing import *
import re
from logging import Logger
from datetime import datetime

ipAddrRe = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"

cmds: List[str] = [
    # "S_STATUS",
    "S_TEM_HUM",
    "S_LOW_LEVEL_STATUS",
    "S_PRESSURE",
    # 'W_MODE',
    # 'W_CH1_MODE',
    # 'W_CH2_MODE',
    # 'W_CH1_TIMER',
    # 'W_CH2_TIMER',
    # 'W_TARGET_PRESSURE',
    # 'W_PRESSURE_RANGE',
    # 'W_PRESSURE_UNIT',
    # 'W_LOW_LEVEL_COUNT',
    # 'W_CH1_PURGE',
    # 'W_CH2_PURGE',
    # 'W_CH1_DISPENSING',
    # 'W_CH2_DISPENSING',
    # 'W_PRESSURE_STATUS',
    "R_MODE",
    "R_CH1_MODE",
    "R_CH2_MODE",
    "R_CH1_TIMER",
    "R_CH2_TIMER",
    "R_TARGET_PRESSURE",
    "R_PRESSURE_RANGE",
    "R_PRESSURE_UNIT",
    "R_LOW_LEVEL_COUNT",
    "R_CH2_PURGE",
    "R_CH1_PURGE",
    "R_CH1_DISPENSING",
    "R_CH2_DISPENSING",
    "R_PRESSURE_STATUS",
    # 'R_MACHINE_INFO_LOG',
    # 'R_RUN_STOP_LOG',
    # 'R_ERROR_MESSAGE_LOG',
    # 'R_PARAMETER_LOG'
]

data_snapshot = {
    "S_STATUS": True,
    "S_TEM_HUM": [28.03, 19.02],
    "S_PRESSURE": -0.01,
    "R_MODE": False,
    "R_CH1_MODE": "TIMER",
    "R_CH2_MODE": "TIMER",
    "R_CH1_TIMER": 10.0,
    "R_CH2_TIMER": 2.0,
    "R_TARGET_PRESSURE": 1.72,
    "R_PRESSURE_RANGE": 0.2,
    "R_PRESSURE_UNIT": "PSI",
    "R_LOW_LEVEL_COUNT": 15,
    "R_CH2_PURGE": False,
    "R_CH1_PURGE": False,
    "R_CH1_DISPENSING": False,
    "R_CH2_DISPENSING": False,
    "R_PRESSURE_STATUS": False,
}


class RC50:
    def __init__(self, host: str, port: int, logger: Logger) -> None:
        assert re.match(ipAddrRe, host), "Server IP Address must be within valid range"
        self.host = host
        self.port = port
        self.data = {}
        self.logger = logger
        self.__initialize__()

    def __start_server__(self) -> bool:
        self.logger.info(f"__start_server__(): starting server")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.sock.bind((self.host, self.port))
            self.sock.listen()
            self.logger.info(f"__start_server__(): server successfully started")
            self.conn, self.addr = self.sock.accept()
            self.logger.info(f"__start_server__(): client successfully connected")
            self.sock.settimeout(10)
            self.server_status = True
        except Exception as e:
            self.logger.info(f"__start_server__(): server failed to start")
            self.logger.info(e)
            return False
        else:
            return True

    def __initialize__(self) -> None:
        if not self.__start_server__():
            return self.logger.info("__initialize__(): server not alive")

        self.logger.info("__initialize__(): initializing values")

        for cmd in cmds:
            if cmd[0] != "W":
                try:
                    response = self.send_commands(cmd)
                    json_response = json.loads(response)
                    json_values = (
                        [*json_response[cmd].values()]
                        if len(json_response[cmd].values()) > 1
                        else [*json_response[cmd].values()][0]
                    )
                    self.data[cmd] = json_values
                except Exception as e:
                    self.logger.info(
                        f"__initialize__(): could not parse {cmd}: {response} because of {e}"
                    )
                if not response:
                    self.logger.info(
                        f"__initialize__(): command: {cmd}, no response at {datetime.now()}"
                    )

    def reinitialize(self):
        for cmd in cmds:
            if cmd[0] != "W":
                response = self.send_commands(cmd)
                try:
                    json_response = json.loads(response)
                    json_values = (
                        [*json_response[cmd].values()]
                        if len(json_response[cmd].values()) > 1
                        else [*json_response[cmd].values()][0]
                    )
                    self.data[cmd] = json_values
                except Exception as e:
                    self.logger.info(
                        f"__initialize__(): could not parse {cmd}: {response} because of {e}"
                    )
                if not response:
                    self.logger.info(
                        f"__initialize__(): command: {cmd}, no response at {datetime.now()}"
                    )

    def __close__(self) -> None:
        if not self.server_status:
            return
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            self.logger.info(f"__close__(): exception caught during execution: {e}")
        else:
            self.server_status = False
            return

    def close(self) -> None:
        self.__close__()
        return

    def __check_pressure_range__(self, pressure: int) -> bool:
        if self.data["R_PRESSURE_UNIT"].lower() == "bar":
            return 0 <= pressure < 7
        else:
            return 0 <= pressure < 100

    def send_commands(self, *args: str, **kwargs: dict) -> str:
        if self.conn:
            if args:
                for arg in args:
                    if str(arg) not in cmds:
                        self.logger.info("send_commands(): command not valid")
                        pass
                    else:
                        self.conn.sendall("{0}".format(arg).encode())
                        try:
                            data = self.conn.recv(1024)
                            # print(arg, data)
                            if data:
                                return data.decode()
                            if not data:
                                return False
                        except Exception as e:
                            self.logger.info(
                                f"send_commands(): failed to send command with exception: {e}"
                            )
                            return False
                    time.sleep(0.05)
            if kwargs:
                self.logger.info(kwargs)
                for comm, value in kwargs.items():
                    if str(comm) not in cmds:
                        self.logger.info("send_commands(): command not valid")
                        pass
                    else:
                        self.conn.sendall("{0} {1}".format(comm, value).encode())
                        data = self.conn.recv(1024)
                        try:
                            data = self.conn.recv(1024)
                            if data:
                                return data.decode()
                            if not data:
                                return False
                        except Exception as e:
                            self.logger.info(
                                f"send_commands(): failed to send command with exception: {e}"
                            )
                            return False
        else:
            self.logger.info("send_commands(): no devices are connected")

    def update_value(self, cmd) -> float:
        response = self.send_commands(cmd)
        json_response = json.loads(response)
        if cmd == "S_TEM_HUM":
            value = [*json_response[cmd].values()]
        else:
            value = [*json_response[cmd].values()][0]
        if value != self.data[cmd]:
            self.data[cmd] = value
            return self.data[cmd]
        else:
            return self.data[cmd]

    def snapshot(self) -> dict:
        return {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "systemPressure": self.data["S_PRESSURE"],
            # 'systemStatus': self.data['S_STATUS'],
            "temperature": self.data["S_TEM_HUM"][0],
            "humidity": self.data["S_TEM_HUM"][1],
            "pressureUnit": self.data["R_PRESSURE_UNIT"],
            "pressureStatus": self.data["R_PRESSURE_STATUS"],
            "targetPressure": self.data["R_TARGET_PRESSURE"],
            "pressureRange": self.data["R_PRESSURE_RANGE"],
            "runMode": self.data["R_MODE"],
            "ch1Mode": self.data["R_CH1_MODE"],
            "ch2Mode": self.data["R_CH1_MODE"],
            "lowLevelCount": self.data["R_LOW_LEVEL_COUNT"],
            "lowLevelStatus": self.data["S_LOW_LEVEL_STATUS"],
            "dispensing": self.data["R_CH1_DISPENSING"],
            "type": "dispense",
        }

    def simulation_snapshot(self) -> dict:
        return {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "systemPressure": random.uniform(11, 15),
            "systemStatus": False,
            "temperature": random.uniform(23.0, 23.5),
            "humidity": random.uniform(56.1, 57.6),
            "pressureUnit": "PSI",
            "pressureStatus": False,
            "targetPressure": 13,
            "pressureRange": 1.5,
            "runMode": False,
            "ch1Mode": "TIMER",
            "ch2Mode": "TIMER",
            "lowLevelCount": 10,
            "lowLevelStatus": "FULL",
            "type": "dispense",
        }

    def monitor_device(self, monitored_values) -> dict:
        for cmd in monitored_values:
            self.update_value(cmd)
        return self.snapshot()

    def check_status(self, history: dict):
        now = datetime.now()
        data_now = self.snapshot()
        if data_now["pressureStatus"] == False:
            if (
                data_now["lowLevelStatus"] != "FULL"
                and (now - history["lowLevel"]).total_seconds() > 5
            ):
                print("no pressure status, not full")
                return {"type": "lowLevel"}
        else:
            if (
                data_now["lowLevelStatus"] != "FULL"
                and (now - history["lowLevel"]).total_seconds() > 5
            ):
                print("pressure status, not full")
                return {"type": "lowLevel"}
            if (
                (
                    data_now["systemPressure"]
                    > (data_now["targetPressure"] + data_now["pressureRange"])
                )
                or (
                    data_now["systemPressure"]
                    < data_now["targetPressure"] - data_now["pressureRange"]
                )
            ) and (now - history["pressure"]).total_seconds() > 5:
                print("pressure status, out of range")
                return {"type": "pressure"}
        return False


def main():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    logger.addHandler(ch)
    try:
        start = time.perf_counter()
        res = RC50("192.168.1.5", 8088, logger)
        print(f"Elapsed time: {(time.perf_counter() - start)*1000}ms")

        # for i in range(20):
        #     start = time.perf_counter()
        #     new = res.monitor_device(['S_PRESSURE', 'R_PRESSURE_STATUS', 'R_MODE', 'S_LOW_LEVEL_STATUS', 'R_TARGET_PRESSURE', 'R_PRESSURE_RANGE', 'R_PRESSURE_UNIT'])
        #     print(new)
        #     print(f'Elapsed time: {(time.perf_counter() - start)*1000}ms')
        #     time.sleep(1)

    finally:
        res.close()


if __name__ == "__main__":
    main()
