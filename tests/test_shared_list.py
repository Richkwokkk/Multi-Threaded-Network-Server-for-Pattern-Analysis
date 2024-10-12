import unittest
import threading
import uuid
from src.linked_list import SharedLinkedList, Node

class TestSharedLinkedList(unittest.TestCase):
    def setUp(self):
        self.shared_list = SharedLinkedList()

    def test_append_single_thread(self):
        book_id = uuid.uuid4()
        node = self.shared_list.append("Test Data", None, "Test Book", book_id)
        
        self.assertEqual(self.shared_list.head, node)
        self.assertEqual(self.shared_list.tail, node)
        self.assertEqual(node.data, "Test Data")
        self.assertEqual(node.book_title, "Test Book")
        self.assertEqual(node.book_id, book_id)

    def test_append_multiple_nodes(self):
        book_id = uuid.uuid4()
        node1 = self.shared_list.append("Data 1", None, "Book 1", book_id)
        node2 = self.shared_list.append("Data 2", node1, "Book 1", book_id)
        node3 = self.shared_list.append("Data 3", node1, "Book 1", book_id)

        self.assertEqual(self.shared_list.head, node1)
        self.assertEqual(self.shared_list.tail, node3)
        self.assertEqual(node1.next, node2)
        self.assertEqual(node2.next, node3)
        self.assertEqual(node1.book_next, node2)
        self.assertEqual(node2.book_next, node3)

    def test_append_multiple_books(self):
        book_id1 = uuid.uuid4()
        book_id2 = uuid.uuid4()
        node1 = self.shared_list.append("Book 1 Data 1", None, "Book 1", book_id1)
        node2 = self.shared_list.append("Book 2 Data 1", None, "Book 2", book_id2)
        node3 = self.shared_list.append("Book 1 Data 2", node1, "Book 1", book_id1)

        self.assertEqual(self.shared_list.head, node1)
        self.assertEqual(self.shared_list.tail, node3)
        self.assertEqual(node1.next, node2)
        self.assertEqual(node2.next, node3)
        self.assertEqual(node1.book_next, node3)
        self.assertIsNone(node2.book_next)

    def test_thread_safety(self):
        def append_nodes(book_id, book_title, num_nodes):
            book_head = None
            for i in range(num_nodes):
                book_head = self.shared_list.append(f"Data {i}", book_head, book_title, book_id)

        threads = []
        num_threads = 10
        nodes_per_thread = 100

        for i in range(num_threads):
            book_id = uuid.uuid4()
            thread = threading.Thread(target=append_nodes, args=(book_id, f"Book {i}", nodes_per_thread))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        node_count = 0
        current = self.shared_list.head
        while current:
            node_count += 1
            current = current.next

        self.assertEqual(node_count, num_threads * nodes_per_thread)

        book_counts = {}
        current = self.shared_list.head
        while current:
            if current.book_id not in book_counts:
                book_counts[current.book_id] = 1
            else:
                book_counts[current.book_id] += 1
            current = current.next

        for count in book_counts.values():
            self.assertEqual(count, nodes_per_thread)

if __name__ == '__main__':
    unittest.main()
