import socket
import os

from datetime import datetime
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
PROXY_PORT = int(os.getenv("PROXY_PORT"))


ddos_list = {} # (address, port) : [last_check, allowance]
black_list = []

rate = 20
per = 60  # seconds
last_check = datetime.now()


def thread_runner(server_socket: socket.socket, client_socket: socket.socket, address):
    while True:
        data = client_socket.recv(1024)
        print(f"Proxy Received: {data}")
        if data == "":
            break

        if address in black_list:
            print(f"{address} is Blocked")
            break
        if data.decode("utf-8").startswith("Ping"):
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
                    # Block ip
                    print(f"{address} IP is blocked")
                    black_list.append(address)
                else:
                    # It is ok
                    ddos_list[address][1] -= 1.0
        else:
            # Proxy request
            server_socket.sendall(data)
            server_data = server_socket.recv(1024)
            client_socket.sendall(server_data)


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
