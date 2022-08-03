import socket
import os

from dotenv import load_dotenv


load_dotenv()

HOST = os.getenv("HOST")
PROXY_PORT = int(os.getenv("PROXY_PORT"))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PROXY_PORT))
    try:
        for i in range(21):
            s.sendall(b"Ping\0")
    except ConnectionResetError:
        s.close()
