import threading

class Node:
    def __init__(self, data, book_title, book_id):
        self.data = data
        self.next = None
        self.book_next = None
        self.next_frequent_search = None
        self.book_title = book_title
        self.book_id = book_id

class SharedLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.shared_list_lock = threading.Lock()

    def append(self, data, book_head, book_title, book_id):
        new_node = Node(data=data, book_title=book_title, book_id=book_id) 

        if not self.head:
            self.head = new_node
        else:
            self.tail.next = new_node

        if book_head:
            temp = book_head
            while temp.book_next:
                temp = temp.book_next
            temp.book_next = new_node

        self.tail = new_node

        print(f"Added node: {data}")

        return new_node

    def __len__(self):
        count = 0
        current = self.head
        while current:
            count += 1
            current = current.next
        return count
