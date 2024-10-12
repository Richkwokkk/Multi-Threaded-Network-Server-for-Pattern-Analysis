import unittest
from unittest.mock import patch, MagicMock
import threading
import time
import os
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

        self.server.write_received_book(book_head)

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

if __name__ == '__main__':
    unittest.main()
