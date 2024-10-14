from .linked_list import Node
from .server import write_received_book

def handle_client(self, client_socket, book_id, shared_list):
        client_socket.setblocking(False)
        buffer = ""

        try:
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    buffer += data.decode('utf-8', errors='ignore')
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        node = Node(line, book_id)
                        shared_list.append(node)
                        print(f"Added node from connection {book_id}: {line}")
                except BlockingIOError:
                    continue

        except Exception as e:
            print(f"Error handling client {book_id}: {e}")
        finally:
            client_socket.close()
            print(f"Connection {book_id} closed.")
            write_received_book(book_id, shared_list)