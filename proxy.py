import socket
import os

from datetime import datetime
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
PROXY_PORT = int(os.getenv("PROXY_PORT"))

ddos_list = {}  # (address, port) : [last_check, allowance]
black_list = []

rate = 20
per = 60
last_check = datetime.now()


def prevent_ddos_attack(address, data):
    for i in data.decode("utf-8").split("\0"):
        if address not in ddos_list.keys():
            ddos_list[address] = [last_check, rate]

        current = datetime.now()
        time_passed = (current - ddos_list[address][0]).seconds
        ddos_list[address][0] = current
        ddos_list[address][1] += time_passed * (rate / per)

        if ddos_list[address][1] > rate:
            ddos_list[address][1] = rate

        allowance = ddos_list[address][1]
        if allowance < 1.0:
            # Block attacker ip
            print(f"{address} IP is blocked")
            black_list.append(address)
        else:
            # It is fine
            ddos_list[address][1] -= 1.0


def proxy_request(server_socket, client_socket, data):
    server_socket.sendall(data)
    server_data = server_socket.recv(1024)
    client_socket.sendall(server_data)


def thread_runner(client_socket: socket.socket, server_socket: socket.socket,  address):
    while True:
        data = client_socket.recv(1024)
        print(f"Proxy Received: {data}")
        if data == "":
            break

        if address in black_list:
            print(f"{address} is Blocked")
            break

        try:
            if data.decode("utf-8").startswith("Ping"):
                prevent_ddos_attack(address, data)
            else:
                proxy_request(server_socket, client_socket, data)
        except:
            proxy_request(server_socket, client_socket, data)
