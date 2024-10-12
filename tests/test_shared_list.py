import unittest
import threading
import uuid
import random
import time
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

class TestSharedLinkedListThreadSafety(unittest.TestCase):
    def setUp(self):
        self.shared_list = SharedLinkedList()

    def test_concurrent_appends(self):
        num_threads = 10
        operations_per_thread = 1000
        
        def append_random_data():
            for _ in range(operations_per_thread):
                book_id = uuid.uuid4()
                self.shared_list.append(f"Data {random.randint(1, 1000)}", None, f"Book {random.randint(1, 10)}", book_id)
        
        threads = [threading.Thread(target=append_random_data) for _ in range(num_threads)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        self.assertEqual(len(self.shared_list), num_threads * operations_per_thread)

    def test_concurrent_reads_and_writes(self):
        num_read_threads = 5
        num_write_threads = 5
        operations_per_thread = 1000
        
        def append_data():
            for i in range(operations_per_thread):
                book_id = uuid.uuid4()
                self.shared_list.append(f"Data {i}", None, f"Book {i % 10}", book_id)
        
        def read_data():
            for _ in range(operations_per_thread):
                with self.shared_list.shared_list_lock:
                    _ = len(self.shared_list)
                    current = self.shared_list.head
                    while current:
                        _ = current.data
                        current = current.next
        
        write_threads = [threading.Thread(target=append_data) for _ in range(num_write_threads)]
        read_threads = [threading.Thread(target=read_data) for _ in range(num_read_threads)]
        
        all_threads = write_threads + read_threads
        random.shuffle(all_threads)
        
        for thread in all_threads:
            thread.start()
        
        for thread in all_threads:
            thread.join()
        
        self.assertEqual(len(self.shared_list), num_write_threads * operations_per_thread)

    def test_stress_test(self):
        num_threads = 20
        operations_per_thread = 5000
        
        def mixed_operations():
            for _ in range(operations_per_thread):
                operation = random.choice(['append', 'read', 'traverse'])
                if operation == 'append':
                    book_id = uuid.uuid4()
                    self.shared_list.append(f"Data {random.randint(1, 1000)}", None, f"Book {random.randint(1, 10)}", book_id)
                elif operation == 'read':
                    with self.shared_list.shared_list_lock:
                        if self.shared_list.head:
                            _ = self.shared_list.head.data
                elif operation == 'traverse':
                    with self.shared_list.shared_list_lock:
                        current = self.shared_list.head
                        while current:
                            _ = current.data
                            current = current.next
        
        threads = [threading.Thread(target=mixed_operations) for _ in range(num_threads)]
        
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        end_time = time.time()
        
        print(f"Stress test completed in {end_time - start_time:.2f} seconds")
        print(f"Final list length: {len(self.shared_list)}")

if __name__ == '__main__':
    unittest.main()
