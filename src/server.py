import socket
import threading
import uuid
import select
import time
from .linked_list import SharedLinkedList
from .pattern_analysis import PatternAnalysisThread

class Server:
    def __init__(self, host, port, pattern):
        self.host = host
        self.port = port
        self.pattern = pattern
        self.server = None
        self.shared_list = SharedLinkedList()
        self.stop_event = threading.Event()
        self.connection_count = 0
        self.connection_count_lock = threading.Lock()
        self.file_write_lock = threading.Lock()
        self.pattern_analysis_threads = self.initialize_pattern_analysis_threads()
        self.book_counter = 0
        self.book_counter_lock = threading.Lock()

    def initialize_pattern_analysis_threads(self, num_threads=2):
        threads = []
        for i in range(num_threads):
            pattern_thread = PatternAnalysisThread(self.shared_list, self.pattern, thread_id=i)
            threads.append(pattern_thread)
        return threads

    def handle_client(self, client_socket):
        book_id = uuid.uuid4()
        book_head = None
        book_title = None
        buffer = b''
        start_time = time.time()
        timeout = 30
        connection_successful = False

        client_socket.setblocking(0)

        try:
            while not self.stop_event.is_set() and (time.time() - start_time) < timeout:
                ready = select.select([client_socket], [], [], 0.1)
                if ready[0]:
                    try:
                        data = client_socket.recv(1024)
                    except BlockingIOError:
                        continue

                    if not data:
                        break

                    buffer += data
                    lines = buffer.split(b'\n')
                    buffer = lines.pop()

                    for line in lines:
                        decoded_line = line.decode('utf-8', errors='ignore').strip()
                        if decoded_line:
                            with self.shared_list.shared_list_lock:
                                if not book_head:
                                    book_title = decoded_line
                                    book_head = self.shared_list.append(data=decoded_line, book_title=book_title, book_id=book_id, book_head=None)
                                else:
                                    self.shared_list.append(data=decoded_line, book_head=book_head, book_title=book_title, book_id=book_id)
                            
                            try:
                                client_socket.sendall(b'READ\n')
                            except BrokenPipeError:
                                print("Client disconnected unexpectedly.")
                                return
            if (time.time() - start_time) >= timeout:
                print(f"Client handling timed out after {timeout} seconds")
            else:
                connection_successful = True
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
            if book_head and connection_successful:
                with self.book_counter_lock:
                    self.book_counter += 1
                    book_number = self.book_counter
                self.write_received_book(book_head, book_number)
            with self.connection_count_lock:
                self.connection_count += 1

    def write_received_book(self, book_head, book_number):
        filename = f"book_{book_number:02}.txt"
        with self.file_write_lock:
            with open(filename, 'w', encoding='utf-8') as file:
                current = book_head
                while current:
                    file.write(current.data + '\n')
                    current = current.book_next
        print(f"Written received book to {filename}")

    def run_server(self, max_connections=None):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.setblocking(0)
        self.server.listen(10)
        print(f"Server started on {self.host}:{self.port}")
        for thread in self.pattern_analysis_threads:
            thread.start()

        while not self.stop_event.is_set():
            try:
                client_socket, _ = self.server.accept()
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_handler.start()
                if max_connections and self.get_connection_count() >= max_connections:
                    break
            except BlockingIOError:
                time.sleep(0.1)
                continue
        
        for thread in threading.enumerate():
            if thread != threading.current_thread():
                thread.join()
        
        return True

    def stop_server(self):
        self.stop_event.set()
        if self.server:
            self.server.close()
        for thread in self.pattern_analysis_threads:
            if thread.is_alive():
                thread.stop_event.set()
                thread.join()
        self.server = None

    def get_connection_count(self):
        return self.connection_count
