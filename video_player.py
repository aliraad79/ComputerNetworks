import os
import pickle
import socket
import struct
import time
from threading import Thread

import cv2


class TransportClient:
    def __init__(self):
        self.receive_buffer = b""

        # Q: unsigned long long integer(8 bytes)
        self.payload_size = struct.calcsize("Q")

    def send_message(self, conn: socket.socket, message):
        pass

    def receive_message(self, socket_connection: socket.socket) -> str:
        while len(self.receive_buffer) < self.payload_size:
            packet = socket_connection.recv(4 * 1024)
            if not packet:
                break
            self.receive_buffer += packet
        packed_msg_size = self.receive_buffer[:self.payload_size]
        self.receive_buffer = self.receive_buffer[self.payload_size:]
        msg_size = struct.unpack("Q", packed_msg_size)[0]
        while len(self.receive_buffer) < msg_size:
            self.receive_buffer += socket_connection.recv(4 * 1024)
        current_message = self.receive_buffer[:msg_size]
        self.receive_buffer = self.receive_buffer[msg_size:]
        return current_message


class VideoPlayerClient:
    def __init__(self):
        pass

    def start(self, socket):
        # used in handling binary data from network connections
        data = b""
        # Q: unsigned long long integer(8 bytes)
        payload_size = struct.calcsize("Q")
        while True:
            while len(data) < payload_size:
                packet = socket.recv(4 * 1024)
                if not packet:
                    break
                data += packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q", packed_msg_size)[0]
            while len(data) < msg_size:
                data += socket.recv(4 * 1024)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frame = pickle.loads(frame_data)
            frame_image = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            cv2.imshow("Receiving...", frame_image)
            key = cv2.waitKey(10)
            if key == ord('q'):
                socket.sendall(bytes("exit", "utf-8"))
                cv2.destroyAllWindows()
                return
            elif key == ord('p'):
                socket.sendall(bytes("pause", "utf-8"))
                while True:
                    cv2.imshow("Receiving...", frame_image)
                    key = cv2.waitKey(10)
                    if key == ord('r'):
                        socket.sendall(bytes("resume", "utf-8"))
                        break
                    elif key == ord('q'):
                        socket.sendall(bytes("exit", "utf-8"))
                        cv2.destroyAllWindows()
                        return


class VideoPlayerServer:
    def __init__(self):
        self.paused = False
        self.finished = False

    def start(self, conn, video):
        sender_thread = Thread(target=self.start_streaming, args=(conn, video))
        receiver_thread = Thread(target=self.start_handling_user_commands, args=(conn,))

        sender_thread.start()
        receiver_thread.start()

        sender_thread.join()
        self.finished = True
        receiver_thread.join()
        conn.sendall(bytes("close-video-stream", "utf-8"))

    def start_handling_user_commands(self, conn):
        while True:
            data = conn.recv(1024).decode("utf-8")
            print(f"Received message in server video player: {data}")
            if self.finished:
                return
            if data == "":
                continue
            elif data == "pause":
                self.paused = True
            elif data == "resume":
                self.paused = False
            elif data == "exit":
                self.finished = True
                return

    def start_streaming(self, conn, video):
        cap = cv2.VideoCapture(os.path.join("videos", video.name))
        while cap.isOpened():
            if self.paused:
                time.sleep(0.1)
                continue

            if self.finished:
                cap.release()
                return

            ret, frame = cap.read()
            ret, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
            a = pickle.dumps(buffer)
            message = struct.pack("Q", len(a)) + a
            try:
                conn.sendall(message)
            except:
                print("video socket closed")

            # cv2.imshow('Sending...',frame)
