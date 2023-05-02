import json
import socket
from threading import Thread
from logging import Logger
import logging
import time
from typing import List, Optional, Tuple, Callable

# from azure.iot.device import IoTHubModuleClient
# from azure.iot.device.exceptions import OperationCancelled, ConnectionFailedError
from datetime import datetime
from rc50 import RC50
import os

CLOUD_PING_INTERVAL: int = int(os.environ.get("CLOUD_PING_INTERVAL") or 50)
DEVICE_MESSAGE_INTERVAL: int = int(os.environ.get("DEVICE_MESSAGE_INTERVAL") or 10)


def time_diff(d2: datetime, d1: datetime) -> Tuple[int, int, int, int]:
    s_diff = (d2 - d1).days * 24 * 3600 + (d2 - d1).seconds
    minutes, seconds = divmod(s_diff, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    return (days, hours, minutes, seconds)


class SocketException(Exception):
    pass


class TCPThreadedServer(Thread):
    def __init__(
        self,
        host: str,
        port: int,
        level=logging.DEBUG,
        logger: Optional[Logger] = None,
        ON_CONNECTED: Optional[Callable] = None,
        ON_RECEIVE: Optional[Callable] = None,
        ON_DISCONNECTED: Optional[Callable] = None,
    ):
        self.logger = logger if logger else logging.getLogger("rc50module")
        self.logger.setLevel(level)
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(funcName)s(): %(message)s"
        )
        self.host = host
        self.port = port
        self.CONNECTION_RECV_TIMEOUT = 5
        self.CONNECTION_RECV_BUFFER_SIZE = 1024
        self.ON_CONNECTED = ON_CONNECTED
        self.ON_RECEIVE = ON_RECEIVE
        self.ON_DISCONNECTED = ON_DISCONNECTED
        self.serving = False
        self.client_array: List[RC50] = []
        self.clients = {}
        Thread.__init__(self)
        self.logger.debug("initialized thread")
        self.startup: datetime = datetime.now()

        # self.logger.info("Initializing IoTHubModule Client")
        # self.client: IoTHubModuleClient = (
        #     IoTHubModuleClient.create_from_edge_environment()
        # )
        # self.logger.info("Initialized IoTHubModule Client")

    # run by the Thread object
    def run(self):
        self.logger.debug("server starting...")
        Thread(target=self.cloud_ping, args=()).start()
        self.listen()

    def listen(self):
        # create an instance of socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(300)

        # bind the socket to its host and port
        self.sock.bind((self.host, self.port))
        self.logger.debug(f"server started at {self.host}:{self.port}")

        # start listening for a client
        self.sock.listen()
        self.logger.debug("server waiting for connections...")

        while True:
            try:
                # get the client object and address
                client: socket.socket
                address: tuple

                client, address = self.sock.accept()

                # add client to list
                res = RC50(self.logger, client, address)
                self.client_array.append(res)
                self.clients[res.host] = {
                    "mcuId": res.data["R_MCUID"],
                    "connectTime": res.startup.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "connected": True,
                    "disconnectTime": None,
                }

                client.settimeout(self.CONNECTION_RECV_TIMEOUT)

                self.logger.info(f"client connected from {address}")

                if self.ON_CONNECTED:
                    self.ON_CONNECTED(client, address)

                # start a thread to listen to the client
                threadedClient = Thread(
                    target=self.listen_to_client,
                    args=(res, self.ON_RECEIVE, self.ON_DISCONNECTED),
                )
                threadedClient.start()
                self.cloud_health()

            except socket.timeout as e:
                self.logger.debug(f"Socket timeout error {e}, restarting the socket")
            except Exception as e:
                self.logger.exception(f"Exception {e}, closing the socket")
                if client:
                    client.close()

    def cloud_health(self):
        # self.client.send_message_to_output(
        self.logger.info(
            json.dumps(
                {
                    # "edgeId": os.environ["IOTEDGE_DEVICEID"],
                    # "hubHost": os.environ["IOTEDGE_IOTHUBHOSTNAME"],
                    "devices": [
                        {
                            "host": host,
                            **data,
                        }
                        for host, data in self.clients.items()
                    ],
                    "sourceTime": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "uptime": self.startup.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
                    "type": "health",
                }
            ),
            # "rc50",
        )
        self.logger.info("sent cloud ping")

    def cloud_ping(self):
        while True:
            try:
                self.cloud_health()
                time.sleep(CLOUD_PING_INTERVAL)
            except Exception as e:
                self.logger.error(e)
                self.logger.debug("unable to connect to cloud, restarting container")
                os._exit(1)

    def listen_to_client(
        self, res: RC50, ON_RECEIVE: Callable = None, ON_DISCONNECTED: Callable = None
    ):
        while res.server_status:
            try:
                data = res.monitor_device(
                    [
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
                        "R_CH1_DISPENSING",
                        "R_CH2_DISPENSING",
                        "R_PRESSURE_STATUS",
                    ]
                )
                if data and ON_RECEIVE:
                    ON_RECEIVE(
                        self.logger,
                        #    self.client,
                        res.host,
                        data,
                    )

                if not data:
                    if ON_DISCONNECTED:
                        ON_DISCONNECTED(self.logger, res)
                    self.client_array.remove(res)
                    self.clients[res.host] = {
                        **self.clients[res.host],
                        "connectTime": None,
                        "connected": False,
                        "disconnectTime": datetime.utcnow().strftime(
                            "%Y-%m-%dT%H:%M:%S.%fZ"
                        ),
                    }
                    self.cloud_health()
                time.sleep(DEVICE_MESSAGE_INTERVAL)

            except json.decoder.JSONDecodeError as e:
                self.logger.exception(f"exception {e}")

            # except (OperationCancelled, ConnectionFailedError):
            #     self.logger.exception("Could not connect to IoT Hub, restarting module")
            #     os._exit(1)

            except Exception as e:
                self.logger.error(f"execption from {res.host}: {e}")

                if ON_DISCONNECTED:
                    ON_DISCONNECTED(self.logger, res)

                self.client_array.remove(res)
                return False

    def send_all(self, cmd):
        for client in self.client_array:
            client.send(cmd.encode())


def handle_response(
    logger: Logger,
    # iotHubClient: IoTHubModuleClient,
    address,
    data: dict,
):
    """_summary_

    Args:
        logger (Logger): Current Logger
        iotHubClient (IoTHubModuleClient): IoT Hub Client
        address (_type_): RC50 Host IP Address
        data (dict): Data structure to be sent to IoT Hub
    """
    logger.info(f"response received from {address}: {data}")
    # iotHubClient.send_message_to_output(
    # (
    #     json.dumps(
    #         {
    #             **data,
    #             "edgeId": os.environ["IOTEDGE_DEVICEID"],
    #             "hubHost": os.environ["IOTEDGE_IOTHUBHOSTNAME"],
    #         }
    #     ),
    #     "rc50",
    # )


def handle_disconnect(logger: Logger, res: RC50):
    logger.error(f"client {res.host} disconnected")
    res.close()


if __name__ == "__main__":
    server = TCPThreadedServer(
        host="192.168.1.5",
        port=8088,
        ON_RECEIVE=handle_response,
        ON_DISCONNECTED=handle_disconnect,
    )
    server.start()
    server.join()
