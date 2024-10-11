import socket
from node import Node

def handle_client(client_socket, shared_list, shared_list_lock, connection_count):
    book_title = client_socket.recv(1024).decode('utf-8')
    book_head = Node(book_title)

    client_socket.sendall(b'ACK')

    while True:
        data = client_socket.recv(1024)
        if len(data) < 1024:
            break

        with shared_list_lock:
            shared_list.append(data.decode('utf-8'), book_head)

        client_socket.sendall(b'ACK')

    client_socket.close()
    write_received_book(book_head, connection_count)

def write_received_book(book_head, connection_count):
    filename = f"book_{connection_count:02}.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        current = book_head
        while current:
            file.write(current.data + '\n')
            current = current.book_next
    print(f"Written received book to {filename}")
