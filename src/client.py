import sys
import socket

class Reader:
    def __init__(self, server_host, server_port, book_file):
        self.server_host = server_host
        self.server_port = server_port
        self.book_file = book_file

    def send_book(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.server_host, self.server_port))

                with open(self.book_file, 'r', encoding='utf-8') as file:
                    book_title = file.readline().strip() + '\n'
                    client_socket.sendall(book_title.encode('utf-8'))

                    ack = client_socket.recv(1024)
                    if ack != b'READ\n':
                        raise ValueError(f"Did not receive acknowledgment for the book title!")
                    else:
                        print(f"Acknowledgment received for book title: {book_title.strip()}")

                    for line in file:
                        client_socket.sendall(line.encode('utf-8'))

                        ack = client_socket.recv(1024)
                        if ack != b'READ\n':
                            raise ValueError(f"Did not receive acknowledgment for line: {line.strip()}")
                        else:
                            print(f"Acknowledgment received for line: {line.strip()}")

                print("Book content sent successfully.")
        except Exception as e:
            raise

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python client.py <SERVER_HOST> <SERVER_PORT> <BOOK_FILE_PATH>")
        sys.exit(1)

    SERVER_HOST = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    BOOK_FILE = sys.argv[3]

    reader = Reader(SERVER_HOST, SERVER_PORT, BOOK_FILE)
    try:
        reader.send_book()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)
