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
    server.bind(('0.0.0.0', port))
    server.listen()
    print(f"Server started on port {port}")

    try:
        while True:
            print("Waiting for a connection...")
            connection, address = server.accept()
            with book_id_counter_lock:
                book_id += 1
                id = book_id
            print(f"Accepted connection {id} from {address}")
            client_thread = threading.Thread(target=handle_client, args=(connection, id, shared_list))
            print(f"Starting client thread for connection {id}")
            client_thread.start()
            print(f"Client thread for connection {id} started")
    except KeyboardInterrupt:
        print("Server shutting down...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        server.close()
