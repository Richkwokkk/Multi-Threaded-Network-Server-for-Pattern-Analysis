import unittest
from unittest.mock import patch, MagicMock
import socket
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.client import Reader

class TestReader(unittest.TestCase):
    def setUp(self):
        self.server_host = 'localhost'
        self.server_port = 12345
        self.book_file = 'test_book.txt'

    @patch('socket.socket')
    def test_send_book(self, mock_socket):
        mock_client_socket = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_client_socket

        mock_client_socket.recv.return_value = b'READ\n'

        test_content = "Book Title\nLine 1\nLine 2\nLine 3\n"
        mock_open = unittest.mock.mock_open(read_data=test_content)

        with patch('builtins.open', mock_open):
            reader = Reader(self.server_host, self.server_port, self.book_file)
            reader.send_book()

        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)

        mock_client_socket.connect.assert_called_once_with((self.server_host, self.server_port))

        expected_calls = [
            unittest.mock.call(b'Book Title\n'),
            unittest.mock.call(b'Line 1\n'),
            unittest.mock.call(b'Line 2\n'),
            unittest.mock.call(b'Line 3\n')
        ]
        mock_client_socket.sendall.assert_has_calls(expected_calls)

        self.assertEqual(mock_client_socket.recv.call_count, 4)

    @patch('socket.socket')
    def test_send_book_error_handling(self, mock_socket):
        mock_client_socket = MagicMock()
        mock_client_socket.recv.return_value = b'ERROR\n'
        mock_socket.return_value.__enter__.return_value = mock_client_socket

        test_content = "Book Title\nLine 1\nLine 2\nLine 3\n"
        mock_open = unittest.mock.mock_open(read_data=test_content)

        with patch('builtins.open', mock_open):
            reader = Reader(self.server_host, self.server_port, self.book_file)
            with self.assertRaisesRegex(ValueError, "Did not receive acknowledgment for the book title!"):
                reader.send_book()

    def test_reader_initialization(self):
        reader = Reader(self.server_host, self.server_port, self.book_file)
        self.assertEqual(reader.server_host, self.server_host)
        self.assertEqual(reader.server_port, self.server_port)
        self.assertEqual(reader.book_file, self.book_file)

if __name__ == '__main__':
    unittest.main()
