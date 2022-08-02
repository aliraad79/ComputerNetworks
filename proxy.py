import socket
import os

from threading import Thread
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
PROXY_PORT = int(os.getenv("PROXY_PORT"))


def thread_runner(server_socket: socket.socket, client_socket: socket.socket):
    while True:
        data = client_socket.recv(1024)
        print(f"Proxy Received: {data}")
        if data == "":
            break
        req_type = data.decode("utf-8").split()[0]

        if req_type == "Ping":
            client_socket.sendall(b"Pong")
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
                    conn, _ = client_socket.accept()
                    Thread(target=thread_runner, args=(server_socket, conn)).start()
        except ConnectionResetError:
            server_socket.close()
