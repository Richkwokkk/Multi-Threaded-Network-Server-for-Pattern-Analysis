import socket
import threading
import uuid
from linked_list import SharedLinkedList
from pattern_analysis import PatternAnalysisThread

class Server:
    def __init__(self, host, port, pattern):
        self.host = host
        self.port = port
        self.pattern = pattern
        self.shared_list = SharedLinkedList()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.pattern_analysis_threads = self.initialize_pattern_analysis_threads()
        self.active_connections = []
        self.connection_count = 0
        self.stop_event = threading.Event()

    def initialize_pattern_analysis_threads(self, num_threads=2):
        threads = []
        for i in range(num_threads):
            pattern_thread = PatternAnalysisThread(self.shared_list, self.pattern, thread_id=i)
            threads.append(pattern_thread)
        return threads

    def handle_client(self, client_socket):
        book_id = uuid.uuid4()
        first_data = client_socket.recv(1024).decode('utf-8')
        book_title = first_data[:first_data.find('\n')]

        with self.shared_list.shared_list_lock:
            book_head = self.shared_list.append(data=first_data, book_title=book_title, book_id=book_id, book_head=None)

        client_socket.sendall(b'READ\n')

        while True:
            data = client_socket.recv(1024)
            with self.shared_list.shared_list_lock:
                try:
                    self.shared_list.append(data=data.decode('utf-8'), book_head=book_head, book_title=book_title, book_id=book_id)
                except UnicodeDecodeError:
                    continue
            client_socket.sendall(b'READ\n')
            if len(data) < 1024:
                break

        client_socket.close()
        self.write_received_book(book_head)

    def write_received_book(self, book_head):
        self.connection_count += 1
        filename = f"book_{self.connection_count:02}.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            current = book_head
            while current:
                file.write(current.data + '\n')
                current = current.book_next
        print(f"Written received book to {filename}")

    def run_server(self):
        self.server.listen(10)
        print(f"Server started on port {self.port}")
        for thread in self.pattern_analysis_threads:
            thread.start()

        while not self.stop_event.is_set():
            try:
                client_socket, _ = self.server.accept()
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_handler.start()
            except socket.timeout:
                continue

    def stop_server(self):
        self.stop_event.set()
        for conn in self.active_connections:
            conn.close()
        for thread in self.pattern_analysis_threads:
            thread.stop_event.set()
            thread.join()
        self.server.close()
