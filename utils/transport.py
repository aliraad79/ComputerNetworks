import struct
import socket


def send_message(socket_connection: socket.socket, message_bytes: bytes):
    transport_message = struct.pack("Q", len(message_bytes)) + message_bytes
    socket_connection.sendall(transport_message)


def receive_message(socket_connection: socket.socket) -> bytes:
    receive_buffer = b""

    # Q: unsigned long long integer(8 bytes)
    payload_size = struct.calcsize("Q")
    while len(receive_buffer) < payload_size:
        packet = socket_connection.recv(payload_size)
        if not packet:
            break
        receive_buffer += packet
    packed_msg_size = receive_buffer[:payload_size]
    receive_buffer = receive_buffer[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]

    while len(receive_buffer) < msg_size:
        receive_size = min(4 * 1024, msg_size - len(receive_buffer))
        receive_buffer += socket_connection.recv(receive_size)
    current_message = receive_buffer[:msg_size]
    assert len(receive_buffer) == msg_size
    return current_message


def receive_message_chunked(socket_connection: socket.socket) -> list[bytes]:
    receive_buffer = b""
    received_size = 0
    # Q: unsigned long long integer(8 bytes)
    payload_size = struct.calcsize("Q")
    while len(receive_buffer) < payload_size:
        packet = socket_connection.recv(payload_size)
        if not packet:
            break
        receive_buffer += packet
    packed_msg_size = receive_buffer[:payload_size]
    receive_buffer = receive_buffer[payload_size:]
    msg_size = struct.unpack("Q", packed_msg_size)[0]

    while len(receive_buffer) < msg_size:
        receive_size = min(4 * 1024, msg_size - len(receive_buffer))
        new_received_data = socket_connection.recv(receive_size)

        receive_buffer += new_received_data
        received_size += len(new_received_data)

        while len(receive_buffer) > 1024:
            yield receive_buffer[:1024]
            receive_buffer = receive_buffer[1024:]

    while len(receive_buffer) > 1024:
        yield receive_buffer[:1024]
        receive_buffer = receive_buffer[1024:]

    return receive_buffer
