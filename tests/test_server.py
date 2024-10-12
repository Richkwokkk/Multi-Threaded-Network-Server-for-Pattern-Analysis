import unittest
from unittest.mock import patch, MagicMock
import threading
import time
import os
import socket
import multiprocessing
from src.server import Server
from src.linked_list import SharedLinkedList, Node
from src.pattern_analysis import PatternAnalysisThread

class TestServer(unittest.TestCase):
    def setUp(self):
        self.host = 'localhost'
        self.port = 12345
        self.pattern = 'test'
        self.server = Server(self.host, self.port, self.pattern)

    def tearDown(self):
        self.server.stop_server()
        self.clean_up_files()

    def clean_up_files(self):
        for i in range(1, 5):
            filename = f"book_{i:02}.txt"
            if os.path.exists(filename):
                os.remove(filename)
                print(f"Removed file: {filename}")

    def test_server_initialization(self):
        self.assertEqual(self.server.host, self.host)
        self.assertEqual(self.server.port, self.port)
        self.assertEqual(self.server.pattern, self.pattern)
        self.assertIsInstance(self.server.shared_list, SharedLinkedList)
        self.assertEqual(len(self.server.pattern_analysis_threads), 2)

    @patch('socket.socket')
    @patch('select.select')
    def test_handle_client(self, mock_select, mock_socket):
        mock_client = MagicMock()
        mock_client.recv.side_effect = [b'Book Title\n', b'Line 1\n', b'Line 2\n', b'']
        mock_select.return_value = ([mock_client], [], [])
        
        self.server.handle_client(mock_client)
        
        self.assertEqual(len(self.server.shared_list), 3)
        self.assertEqual(self.server.shared_list.head.data, 'Book Title')
        self.assertEqual(self.server.shared_list.head.next.data, 'Line 1')
        self.assertEqual(self.server.shared_list.head.next.next.data, 'Line 2')

    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_write_received_book(self, mock_open):
        book_head = Node('Book Title', 'Test Book', 'test_id')
        book_head.book_next = Node('Line 1', 'Test Book', 'test_id')
        book_head.book_next.book_next = Node('Line 2', 'Test Book', 'test_id')

        self.server.write_received_book(book_head, 1)

        mock_open.assert_called_once_with('book_01.txt', 'w', encoding='utf-8')
        handle = mock_open()
        handle.write.assert_any_call('Book Title\n')
        handle.write.assert_any_call('Line 1\n')
        handle.write.assert_any_call('Line 2\n')

    def test_pattern_analysis(self):
        self.server.shared_list.append('Book 1 Title', None, 'Book 1 Title', '1')
        self.server.shared_list.append('This is a test line', None, 'Book 1 Title', '1')
        self.server.shared_list.append('Another test line', None, 'Book 1 Title', '1')
        self.server.shared_list.append('Book 2 Title', None, 'Book 2 Title', '2')
        self.server.shared_list.append('No match here', None, 'Book 2 Title', '2')

        analysis_thread = PatternAnalysisThread(self.server.shared_list, self.server.pattern)
        analysis_thread.start()
        time.sleep(0.1)
        analysis_thread.stop_event.set()
        analysis_thread.join()

        self.assertEqual(len(analysis_thread.book_counter), 1)
        self.assertEqual(analysis_thread.book_counter['1'], 2)
        self.assertEqual(analysis_thread.book_map['1'], 'Book 1 Title')

    def test_multiple_simultaneous_connections(self):
        num_connections = 10
        test_data = "Book Title\nLine 1\nLine 2\nLine 3\n"
        client_success = [False] * num_connections
        client_lock = threading.Lock()

        def simulate_client(port, client_id):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                    client.settimeout(10)  # Increase timeout to 10 seconds
                    client.connect(('localhost', port))
                    client.sendall(test_data.encode('utf-8'))
                    for _ in range(4):  # 4 lines in test_data
                        ack = client.recv(1024)
                        if ack != b'READ\n':
                            print(f"Client {client_id}: Unexpected acknowledgment: {ack}")
                            return
                    print(f"Client {client_id}: Successfully sent data")
                    with client_lock:
                        client_success[client_id] = True
            except Exception as e:
                print(f"Client {client_id}: Error: {e}")

        server_thread = threading.Thread(target=self.server.run_server, args=(num_connections,))
        server_thread.start()

        time.sleep(2)

        client_threads = []
        for i in range(num_connections):
            client_thread = threading.Thread(target=simulate_client, args=(self.server.port, i))
            client_threads.append(client_thread)
            client_thread.start()

        for thread in client_threads:
            thread.join(timeout=15)

        self.server.stop_server()
        server_thread.join(timeout=5)

        self.assertEqual(self.server.get_connection_count(), num_connections,
                         f"Expected {num_connections} connections, but got {self.server.get_connection_count()}")
        
        files_created = 0
        for i in range(1, num_connections + 1):
            filename = f"book_{i:02}.txt"
            if os.path.exists(filename):
                files_created += 1
                with open(filename, 'r') as f:
                    content = f.read()
                    self.assertEqual(content.strip(), test_data.strip(),
                                     f"Incomplete content in {filename}")
            else:
                print(f"File not found: {filename}")

        self.assertEqual(files_created, num_connections,
                         f"Expected {num_connections} files, but got {files_created}")

        for i in range(1, num_connections + 1):
            filename = f"book_{i:02}.txt"
            if os.path.exists(filename):
                os.remove(filename)

        print(f"Test completed. Actual items: {len(self.server.shared_list)}, "
              f"Connections: {self.server.get_connection_count()}, "
              f"Files created: {files_created}, Successful clients: {sum(client_success)}")

if __name__ == '__main__':
    unittest.main()
