import json
import socket
from typing import Any, List
from logging import Logger
from datetime import datetime

cmds: List[str] = [
    "S_STATUS",
    "S_TEM_HUM",
    "S_LOW_LEVEL_STATUS",
    "S_PRESSURE",
    "S_SYS_STATUS",
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
    "R_MCUID",
]

data_snapshot = {
    "S_STATUS": True,
    "S_TEM_HUM": [28.03, 19.02],
    "S_PRESSURE": -0.01,
    "S_SYS_STATUS": "READY",
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


def str2bool(str):
    return str in ["true", "TRUE", "True"]


class RC50:
    def __init__(self, logger: Logger, conn: socket.socket, addr: tuple) -> None:
        self.host = addr[0]
        self.port = addr[1]
        self.data = {}
        self.logger = logger
        self.conn = conn
        self.server_status = True
        self.startup: datetime = datetime.utcnow()
        self.__initialize__()
        self.messageTime = {
            "change": datetime.now,
            "dispense": datetime.now,
        }

    def __initialize__(self) -> None:
        self.logger.info("__initialize__(): initializing values")

        for cmd in cmds:
            COMMAND_ATTEMPTS = 1
            response = self.send_commands(cmd)
            try:
                if cmd == "S_LOW_LEVEL_STATUS":
                    if "FULL" in response:
                        self.data[cmd] = "FULL"
                    elif "LOWER" in response:
                        self.data[cmd] = "LOWER"
                    else:
                        self.data[cmd] = "EMPTY"

                if cmd == "S_LOW_LEVEL_STATUS":
                    continue

                json_response = json.loads(response)
                json_values = (
                    [*json_response[cmd].values()]
                    if len(json_response[cmd].values()) > 1
                    else [*json_response[cmd].values()][0]
                )
                self.data[cmd] = json_values

                if not response:
                    self.logger.info(
                        f"__initialize__(): command: {cmd}, no response at {datetime.now()}"
                    )
            except json.decoder.JSONDecodeError:
                while COMMAND_ATTEMPTS <= 4:
                    COMMAND_ATTEMPTS += 1
                    self.logger.error(
                        f"exception from command {cmd}, response: {response}, trying attempt #: {COMMAND_ATTEMPTS}"
                    )
                    response = self.send_commands(cmd)
                    if cmd == "S_LOW_LEVEL_STATUS":
                        if "FULL" in response:
                            self.data[cmd] = "FULL"
                        elif "LOWER" in response:
                            self.data[cmd] = "LOWER"
                        else:
                            self.data[cmd] = "EMPTY"

                    if cmd == "S_LOW_LEVEL_STATUS":
                        continue
                    json_response = json.loads(response)
                    json_values = (
                        [*json_response[cmd].values()]
                        if len(json_response[cmd].values()) > 1
                        else [*json_response[cmd].values()][0]
                    )
                    self.data[cmd] = json_values

                    if not response:
                        self.logger.info(
                            f"__initialize__(): command: {cmd}, no response at {datetime.now()}"
                        )
            except KeyError:
                while COMMAND_ATTEMPTS <= 4:
                    COMMAND_ATTEMPTS += 1
                    self.logger.error(
                        f"exception from command {cmd}, response: {response}, trying attempt #: {COMMAND_ATTEMPTS}"
                    )
                    response = self.send_commands(cmd)
                    if cmd == "S_LOW_LEVEL_STATUS":
                        if "FULL" in response:
                            self.data[cmd] = "FULL"
                        elif "LOWER" in response:
                            self.data[cmd] = "LOWER"
                        else:
                            self.data[cmd] = "EMPTY"

                    if cmd == "S_LOW_LEVEL_STATUS":
                        continue
                    json_response = json.loads(response)
                    json_values = (
                        [*json_response[cmd].values()]
                        if len(json_response[cmd].values()) > 1
                        else [*json_response[cmd].values()][0]
                    )
                    self.data[cmd] = json_values

                    if not response:
                        self.logger.info(
                            f"__initialize__(): command: {cmd}, no response at {datetime.now()}"
                        )
            except Exception as e:
                self.logger.error(f"exception from command {cmd}: {e}")
            else:
                self.logger.info(f"{cmd}: {response}")

    def reinitialize(self):
        for cmd in cmds:
            response = self.send_commands(cmd)

            if cmd == "S_LOW_LEVEL_STATUS":
                if "FULL" in response:
                    self.data[cmd] = "FULL"
                elif "LOWER" in response:
                    self.data[cmd] = "LOWER"
                else:
                    self.data[cmd] = "EMPTY"

            try:
                if cmd == "S_LOW_LEVEL_STATUS":
                    continue
                json_response = json.loads(response)
                json_values = (
                    [*json_response[cmd].values()]
                    if len(json_response[cmd].values()) > 1
                    else [*json_response[cmd].values()][0]
                )
                self.data[cmd] = json_values
            except Exception as e:
                self.logger.error(
                    f"__initialize__(): could not parse {cmd}: {response} because of {e}"
                )
            if not response:
                self.logger.error(
                    f"__initialize__(): command: {cmd}, no response at {datetime.now()}"
                )

    def __close__(self) -> None:
        try:
            self.conn.close()
        except Exception as e:
            self.logger.error(f"__close__(): exception caught during execution: {e}")

    def close(self) -> None:
        self.server_status = False
        self.__close__()
        return

    def __check_pressure_range__(self, pressure: int) -> bool:
        if self.data["R_PRESSURE_UNIT"].lower() == "bar":
            return 0 <= pressure < 7
        else:
            return 0 <= pressure < 100

    def send_commands(self, *args: str, **kwargs: dict) -> Any:
        if self.conn:
            if args:
                for arg in args:
                    if str(arg) not in cmds:
                        self.logger.info("send_commands(): command not valid")
                        pass
                    else:
                        self.conn.send("{0}".format(arg).encode())
                        try:
                            data = self.conn.recv(1024)
                            if data:
                                return data.decode()
                            if not data:
                                return False
                        except socket.timeout as e:
                            self.logger.error(
                                f"send_commands(): no response from device, closing socket"
                            )
                            return False
                        except Exception as e:
                            self.logger.error(
                                f"send_commands(): failed to send command with exception: {e}"
                            )
                            return False
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
                        except socket.timeout as e:
                            self.logger.error(
                                f"send_commands(): no response from device, closing socket"
                            )
                            return False
                        except Exception as e:
                            self.logger.error(
                                f"send_commands(): failed to send command with exception: {e}"
                            )
                            return False

        else:
            self.logger.info("send_commands(): no devices are connected")

    def update_value(self, cmd):
        COMMAND_ATTEMPTS = 1
        response = self.send_commands(cmd)
        try:
            if not response:
                return False

            elif cmd == "S_LOW_LEVEL_STATUS":
                if "FULL" in response:
                    self.data[cmd] = "FULL"
                    return {cmd: self.data[cmd]}
                elif "LOWER" in response:
                    self.data[cmd] = "LOWER"
                    return {cmd: self.data[cmd]}
                else:
                    self.data[cmd] = "EMPTY"
                    return {cmd: self.data[cmd]}

            json_response = json.loads(response)
            try:
                if cmd == "S_TEM_HUM":
                    value = [*json_response[cmd].values()]
                else:
                    value = [*json_response[cmd].values()][0]
            except Exception as e:
                value = self.data[cmd]
            if value != self.data[cmd]:
                self.data[cmd] = value
                return {cmd: self.data[cmd]}
            else:
                return {cmd: self.data[cmd]}
        except json.decoder.JSONDecodeError as e:
            while COMMAND_ATTEMPTS <= 4:
                COMMAND_ATTEMPTS += 1
                self.logger.exception(
                    f"exception from command {cmd}, response: {response} trying attempt #: {COMMAND_ATTEMPTS}"
                )
                response = self.send_commands(cmd)

                if not response:
                    return False

                elif cmd == "S_LOW_LEVEL_STATUS":
                    if "FULL" in response:
                        self.data[cmd] = "FULL"
                        return {cmd: self.data[cmd]}
                    elif "LOWER" in response:
                        self.data[cmd] = "LOWER"
                        return {cmd: self.data[cmd]}
                    else:
                        self.data[cmd] = "EMPTY"
                        return {cmd: self.data[cmd]}

                json_response = json.loads(response)
                try:
                    if cmd == "S_TEM_HUM":
                        value = [*json_response[cmd].values()]
                    else:
                        value = [*json_response[cmd].values()][0]
                except Exception as e:
                    value = self.data[cmd]
                if value != self.data[cmd]:
                    self.data[cmd] = value
                    return {cmd: self.data[cmd]}
                else:
                    return {cmd: self.data[cmd]}
            return False
        except Exception as e:
            self.logger.exception(
                f"exception from command {cmd}, response {response}: {e}"
            )

    def snapshot(self) -> dict:
        return {
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "host": self.host,
            "mcuId": self.data["R_MCUID"],
            "systemPressure": self.data["S_PRESSURE"],
            "systemStatus": self.data["S_STATUS"],
            "runStatus": self.data["S_SYS_STATUS"],
            "temperature": self.data["S_TEM_HUM"][0],
            "humidity": self.data["S_TEM_HUM"][1],
            "pressureUnit": self.data["R_PRESSURE_UNIT"],
            "pressureStatus": self.data["R_PRESSURE_STATUS"],
            "targetPressure": self.data["R_TARGET_PRESSURE"],
            "pressureRange": self.data["R_PRESSURE_RANGE"],
            "runMode": self.data["R_MODE"],
            "ch1Mode": self.data["R_CH1_MODE"],
            "ch2Mode": self.data["R_CH2_MODE"],
            "lowLevelCount": self.data["R_LOW_LEVEL_COUNT"],
            "lowLevelStatus": self.data["S_LOW_LEVEL_STATUS"],
            "ch1Dispensing": self.data["R_CH1_DISPENSING"],
            "ch2Dispensing": self.data["R_CH2_DISPENSING"],
            "type": "dispense" if self.data["R_CH1_DISPENSING"] == True else "update",
        }

    def monitor_device(
        self,
        monitored_values: List = [
            "S_PRESSURE",
            "R_PRESSURE_STATUS",
            "S_STATUS",
            "R_MODE",
            "S_LOW_LEVEL_STATUS",
        ],
    ) -> Any:
        for cmd in monitored_values:
            data = self.update_value(cmd)
            if not data:
                return False
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
