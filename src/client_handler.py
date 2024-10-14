from .linked_list import Node
from .server import write_received_book

def handle_client(client_socket, book_id, shared_list):
    client_socket.setblocking(False)
    buffer = ""

    try:
        while True:
            buffer = process_incoming_data(client_socket, buffer)
            if not buffer:
                break
            process_buffer(buffer, book_id, shared_list)
    except Exception as e:
        print(f"Error handling client {book_id}: {e}")
    finally:
        cleanup(client_socket, book_id, shared_list)

def process_incoming_data(client_socket, buffer):
    try:
        data = client_socket.recv(1024)
        if not data:
            return ""
        return buffer + data.decode('utf-8', errors='ignore')
    except BlockingIOError:
        return buffer

def process_buffer(buffer, book_id, shared_list):
    while '\n' in buffer:
        line, buffer = buffer.split('\n', 1)
        line = line.strip()
        node = Node(line, book_id)
        shared_list.append(node)
        print(f"Added node from connection {book_id}: {line}")
    return buffer

def cleanup(client_socket, book_id, shared_list):
    client_socket.close()
    print(f"Connection {book_id} closed.")
    write_received_book(book_id, shared_list)
