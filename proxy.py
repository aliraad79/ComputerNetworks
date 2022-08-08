import socket
import os

from datetime import datetime
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
PROXY_PORT = int(os.getenv("PROXY_PORT"))
