import struct
import cv2
import pickle
import os
from threading import Thread
import queue
import time


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
                if not packet: break
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
            key = cv2.waitKey(1)
            if key == 13:
                cv2.destroyAllWindows()
                return


class VideoPlayerServer:
    def __init__(self):
        self.queue = queue.Queue()
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

    def start_handling_user_commands(self, conn):
        while True:
            data = conn.recv(1024).decode("utf-8")
            print(f"Received message in server video player: {data}")
            if self.finished:
                return
            if data == "":
                continue
            elif data == "pause":
                self.queue.put("pause")
            elif data == "resume":
                self.queue.put("resume")
            elif data == "exit":
                self.queue.put("exit")

    def start_streaming(self, conn, video):
        cap = cv2.VideoCapture(os.path.join("videos", video.name))
        while cap.isOpened():
            if self.paused:
                time.sleep(0.1)
                continue

            ret, frame = cap.read()
            ret, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
            a = pickle.dumps(buffer)
            message = struct.pack("Q", len(a)) + a
            conn.sendall(message)
            # cv2.imshow('Sending...',frame)
            # key = cv2.waitKey(10)
            while not self.queue.empty():
                command = self.queue.get()
                if command == "exit":
                    cap.release()
                    return
                elif command == "pause":
                    self.paused = True
                elif command == "resume":
                    self.paused = False
