from node import Node

class SharedList:
    def __init__(self):
        self.head = None

    def append(self, data, book_head):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            book_head.book_next = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

            if book_head.book_next:
                temp = book_head.book_next
                while temp.book_next:
                    temp = temp.book_next
                temp.book_next = new_node
            else:
                book_head.book_next = new_node

        print(f"Added node: {data}")
