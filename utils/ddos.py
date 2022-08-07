import socket
import os

from dotenv import load_dotenv


load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    try:
        for i in range(18):
            s.sendall(b"Ping\0")
    except ConnectionResetError:
        s.close()
