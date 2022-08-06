import os
import pickle
import socket
import time
import cv2

from threading import Thread
from transport import send_message, receive_message


class VideoPlayerClient:
    def __init__(self):
        pass

    def start(self, socket_connection):
        while True:
            frame_bytes = receive_message(socket_connection)
            if frame_bytes.decode('utf-8', errors='ignore') == "close-video-stream":
                cv2.destroyAllWindows()
                break
            frame = pickle.loads(frame_bytes)
            frame_image = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            cv2.imshow("Receiving...", frame_image)
            key = cv2.waitKey(10)
            if key == ord('q'):
                send_message(socket_connection, bytes("exit", 'utf-8'))
            elif key == ord('p'):
                send_message(socket_connection, bytes("pause", 'utf-8'))
                while True:
                    cv2.imshow("Receiving...", frame_image)
                    key = cv2.waitKey(10)
                    if key == ord('r'):
                        send_message(socket_connection, bytes("resume", 'utf-8'))
                        break
                    elif key == ord('q'):
                        send_message(socket_connection, bytes("exit", 'utf-8'))


class VideoPlayerServer:
    def __init__(self):
        self.paused = False
        self.finished = False

    def start(self, socket_connection: socket.socket, video):
        sender_thread = Thread(target=self.start_streaming, args=(socket_connection, video))
        receiver_thread = Thread(target=self.start_handling_user_commands, args=(socket_connection,))

        sender_thread.start()
        receiver_thread.start()

        sender_thread.join()
        self.finished = True
        receiver_thread.join()
        send_message(socket_connection, bytes("close-video-stream", 'utf-8'))

    def start_handling_user_commands(self, socket_connection: socket.socket):
        while True:
            data = receive_message(socket_connection).decode("utf-8")
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

    def start_streaming(self, socket_connection, video):
        cap = cv2.VideoCapture(os.path.join("videos", video.name))
        while cap.isOpened():
            if self.paused:
                time.sleep(0.1)
                continue

            if self.finished:
                break

            ret, frame = cap.read()
            if not ret:
                break
            ret, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 25])
            message_bytes = pickle.dumps(buffer)
            send_message(socket_connection, message_bytes)

        self.finished = True
        cap.release()
