import threading

class Node:
    def __init__(self, line, book_id):
        self.line = line
        self.book_id = book_id
        self.next = None
        self.book_next = None
        self.next_frequent_search = None

class SharedLinkedList:
    def __init__(self, pattern):
        # Initialize the shared linked list
        self.head = None
        self.tail = None
        self.books = {}
        self.pattern = pattern
        self.pattern_counts = {}
        self.shared_list_lock = threading.Lock()

    def append(self, node):
        # Add a new node to the shared linked list
        with self.shared_list_lock:
            if self.head is None:
                self.head = node
                self.tail = node
            else:
                self.tail.next = node
                self.tail = node

        # Update book-specific linked list
        book = self.books.get(node.book_id)
        if book is None:
            # Create a new book entry if it doesn't exist
            book = {'title': node.line.strip(), 'head': node, 'tail': node}
            self.books[node.book_id] = book
            self.pattern_counts[node.book_id] = 0
        else:
            # Append to existing book's linked list
            book['tail'].book_next = node
            book['tail'] = node

        # Update pattern count for the book
        if self.pattern in node.line:
            self.pattern_counts[node.book_id] += 1

    def sort_books(self):
        # Sort books based on pattern occurrence count
        with self.shared_list_lock:
            sorted_books = []
            for id, book in self.books.items():
                count = self.pattern_counts.get(id, 0)
                sorted_books.append((id, book['title'], count))

            sorted_books.sort(key=lambda x: x[2], reverse=True)

            return sorted_books
        
    def get_head(self, book_id):
        # Get the head node of a specific book's linked list
        with self.shared_list_lock:
            book = self.books.get(book_id)
            if book:
                return book['head']
            return None
