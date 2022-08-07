import socket
import os

from datetime import datetime
from threading import Thread
from dotenv import load_dotenv
from utils.transport import send_message, receive_message

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
PROXY_PORT = int(os.getenv("PROXY_PORT"))

ddos_list = {}  # (address, port) : [last_check, allowance]
black_list = []

rate = 20
per = 60
last_check = datetime.now()


def proxy_request(server_socket_conn: socket.socket, client_socket_conn: socket.socket, data: bytes):
    send_message(server_socket_conn, data)
    server_data = receive_message(server_socket_conn)
    send_message(client_socket_conn, server_data)


def prevent_ddos(address, data):
    for _ in data.decode("utf-8").split("\0"):
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
            # Block ip
            print(f"{address} IP is blocked")
            black_list.append(address)
        else:
            # It is ok
            ddos_list[address][1] -= 1.0


def thread_runner(server_socket_conn: socket.socket, client_socket_conn: socket.socket, address):
    while True:
        data = receive_message(client_socket_conn)
        print(f"Proxy Received: {data}")
        if data == "":
            break

        if address in black_list:
            print(f"{address} is Blocked")
            break

        try:
            if data.decode("utf-8").startswith("Ping"):
                prevent_ddos(address, data)
            else:
                proxy_request(server_socket_conn, client_socket_conn, data)
        except:
            proxy_request(server_socket_conn, client_socket_conn, data)


if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.connect((HOST, PORT))

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.bind((HOST, PROXY_PORT))
                client_socket.listen(10)

                while True:
                    conn, addr = client_socket.accept()
                    Thread(
                        target=thread_runner, args=(server_socket, conn, addr)
                    ).start()
        except ConnectionResetError:
            server_socket.close()
