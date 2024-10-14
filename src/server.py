import socket
import threading
import argparse
from .linked_list import SharedLinkedList
from .pattern_analysis import analyze_data

class Server:
    def __init__(self, port, pattern):
        self.port = port
        self.pattern = pattern
        self.shared_list = SharedLinkedList(pattern)
        self.book_id = 0
        self.book_id_counter_lock = threading.Lock()
        self.output_lock = threading.Lock()

    def run_server(self):
        for i in range(2):
            thread = threading.Thread(target=analyze_data, args=(self.shared_list, self.output_lock, 5))
            thread.daemon = True
            self.pattern_analysis_threads.append(thread)
            thread.start()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('', self.port))
        self.server.listen()
        print(f"Server started on port {self.port}")

        try:
            while True:
                connection, address = self.server.accept()
                with self.book_id_counter_lock:
                    self.book_id[0] += 1
                    id = self.book_id[0]
                print(f"Accepted connection {id} from {address}")
                client_thread = threading.Thread(target=self.handle_client, args=(connection, id, self.shared_list))
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.server.close()

def write_received_book(book_id, shared_list):
        head = shared_list.get_head(book_id)
        if head is None:
            print(f"No head found for book {book_id}")
            return

        filename = f"book_{book_id:02d}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                node = head
                while node and node.book_id == book_id:
                    f.write(node.data + '\n')
                    node = node.book_next
            print(f"Book {book_id} written to {filename}")
        except Exception as e:
            print(f"Failed to write book {book_id} to file: {e}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Start the server.")
    parser.add_argument('-l', type=int, required=True, help='The listen port for the server.')
    parser.add_argument('-p', type=str, required=True, help='The search pattern.')
    args = parser.parse_args()

    if args.l <= 1024:
        parser.error("The listen port must be greater than 1024.")
    return args

def main():
    args = parse_arguments()
    server = Server(args.l, args.p)
    server.run_server()
