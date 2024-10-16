from linked_list import Node
from utils import write_received_book

def handle_client(client_socket, book_id, shared_list):
    """
    Handle a client connection for receiving book data.

    :param client_socket: Socket object for the client connection
    :param book_id: Unique identifier for the book being received
    :param shared_list: Shared data structure to store received lines
    """
    print(f"Handling client {book_id}")
    client_socket.setblocking(False)
    buffer = ""

    try:
        buffer = ''
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            buffer += data.decode('utf-8', errors='ignore')
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                node = Node(line, book_id)
                shared_list.append(node)
        print(f"Added node from connection {book_id}: {line}")
        shared_list.append(Node(buffer, book_id))
    except Exception as e:
        print(f"Error handling client {book_id}: {e}")
    finally:
        cleanup(client_socket, book_id, shared_list)

    print(f"Finished handling client {book_id}")

def process_incoming_data(client_socket, buffer):
    """
    Receive data from the client socket and append it to the buffer.

    :param client_socket: Socket object for the client connection
    :param buffer: Current buffer of received data
    :return: Updated buffer with new data, or empty string if connection closed
    """
    try:
        data = client_socket.recv(1024)
        if not data:
            return buffer + ""
        return buffer + data.decode('utf-8', errors='ignore')
    except BlockingIOError:
        return buffer

def process_buffer(buffer, book_id, shared_list):
    """
    Process the buffer, extracting complete lines and adding them to the shared list.

    :param buffer: Current buffer of received data
    :param book_id: Unique identifier for the book being received
    :param shared_list: Shared data structure to store received lines
    :return: Remaining buffer after processing complete lines
    """
    while '\n' in buffer:
        line, buffer = buffer.split('\n', 1)
        node = Node(line, book_id)
        shared_list.append(node)
        print(f"Added node from connection {book_id}: {line}")
    return buffer

def cleanup(client_socket, book_id, shared_list):
    """
    Perform cleanup operations after client disconnection.

    :param client_socket: Socket object for the client connection
    :param book_id: Unique identifier for the book being received
    :param shared_list: Shared data structure containing received lines
    """
    client_socket.close()
    print(f"Connection {book_id} closed.")
    write_received_book(book_id, shared_list)
