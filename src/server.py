import socket
import threading
import argparse
from .linked_list import SharedLinkedList
from .pattern_analysis import analyze_data
from .client_handler import handle_client

def parse_arguments():
    parser = argparse.ArgumentParser(description="Start the server.")
    parser.add_argument('-l', type=int, required=True, help='The listen port for the server.')
    parser.add_argument('-p', type=str, required=True, help='The search pattern.')
    args = parser.parse_args()

    if args.l <= 1024:
        parser.error("The listen port must be greater than 1024.")
    return args

def start_analysis_threads(shared_list, output_lock):
    for _ in range(2):
        thread = threading.Thread(target=analyze_data, args=(shared_list, output_lock))
        thread.daemon = True
        thread.start()

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

def main():
    args = parse_arguments()
    port = args.l
    pattern = args.p

    shared_list = SharedLinkedList(pattern)
    output_lock = threading.Lock()
    book_id_counter_lock = threading.Lock()
    book_id = 0

    start_analysis_threads(shared_list, output_lock)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', port))
    server.listen()
    print(f"Server started on port {port}")

    try:
        while True:
            connection, address = server.accept()
            with book_id_counter_lock:
                book_id += 1
                id = book_id
            print(f"Accepted connection {id} from {address}")
            client_thread = threading.Thread(target=handle_client, args=(connection, id, shared_list))
            client_thread.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.close()
