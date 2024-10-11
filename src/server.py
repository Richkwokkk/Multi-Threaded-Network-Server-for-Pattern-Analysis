import argparse
import socket
import threading
from pattern_analysis import PatternAnalysisThread
from shared_list import SharedList
from client import handle_client

class Server:
    def __init__(self, host, port, pattern):
        self.host = host
        self.port = port
        self.pattern = pattern
        self.shared_list = SharedList()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.pattern_analysis_thread = self.initialize_pattern_analysis_thread()
        self.connection_count = 0
        self.active_connections = []
        self.stop_event = threading.Event()
        self.shared_list_lock = threading.Lock()

    def initialize_pattern_analysis_thread(self):
        pattern_thread = PatternAnalysisThread(self.shared_list, self.pattern)
        return pattern_thread

    def run_server(self):
        self.server.listen(10)
        print(f"Server started on port {self.port}")
        self.pattern_analysis_thread.start()

        while not self.stop_event.is_set():
            try:
                client_socket, addr = self.server.accept()
                self.active_connections.append(client_socket)
                client_handler = threading.Thread(target=handle_client, args=(client_socket, self.shared_list, self.shared_list_lock, self.connection_count))
                client_handler.start()
            except socket.timeout:
                continue

    def stop_server(self):
        self.stop_event.set()

        for conn in self.active_connections:
            conn.close()

        self.server.close()
        self.pattern_analysis_thread.join()
        print("Server stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the server.")
    parser.add_argument('-l', type=int, default=12345, help='The listen port for the server.')
    parser.add_argument('-p', type=str, required=True, help='The search pattern.')
    args = parser.parse_args()

    server = Server('0.0.0.0', args.l, args.p)

    try:
        server.run_server()
    except KeyboardInterrupt:
        print("\nShutting down the server...")
        server.stop_server()
