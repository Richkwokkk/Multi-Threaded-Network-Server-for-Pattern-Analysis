import socket
import threading
import argparse
from .linked_list import SharedLinkedList
from .pattern_analysis import analyze_data
from .client_handler import handle_client

def parse_arguments():
    """
    Parse command-line arguments for the server.

    Returns:
        argparse.Namespace: Parsed arguments containing 'l' (listen port) and 'p' (search pattern).
    """
    parser = argparse.ArgumentParser(description="Start the server.")
    parser.add_argument('-l', type=int, required=True, help='The listen port for the server.')
    parser.add_argument('-p', type=str, required=True, help='The search pattern.')
    args = parser.parse_args()

    if args.l <= 1024:
        parser.error("The listen port must be greater than 1024.")
    return args

def start_analysis_threads(shared_list, output_lock):
    """
    Start two daemon threads for data analysis.

    Args:
        shared_list (SharedLinkedList): The shared linked list containing data to analyze.
        output_lock (threading.Lock): Lock for synchronizing output.
    """
    for _ in range(2):
        thread = threading.Thread(target=analyze_data, args=(shared_list, output_lock))
        thread.daemon = True
        thread.start()

def main():
    """
    Main function to run the server.
    """
    # Parse command-line arguments
    args = parse_arguments()
    port = args.l
    pattern = args.p

    # Initialize shared resources
    shared_list = SharedLinkedList(pattern)
    output_lock = threading.Lock()
    book_id_counter_lock = threading.Lock()
    book_id = 0

    # Start analysis threads
    start_analysis_threads(shared_list, output_lock)

    # Set up the server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((socket.gethostname(), port))
    server.listen()
    print(f"Server started on port {port}")

    try:
        while True:
            print("Waiting for a connection...")
            connection, address = server.accept()
            
            # Increment book_id in a thread-safe manner
            with book_id_counter_lock:
                book_id += 1
                id = book_id
            
            print(f"Accepted connection {id} from {address}")
            
            # Start a new thread to handle the client
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
