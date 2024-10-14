import threading

class Node:
    def __init__(self, line, book_id):
        # 初始化节点,存储行内容和书籍ID
        self.line = line
        self.book_id = book_id
        self.next = None  # 指向下一个节点
        self.book_next = None  # 指向同一本书的下一个节点
        self.next_frequent_search = None  # 用于频繁搜索的链接(未使用)

class SharedLinkedList:
    def __init__(self, pattern):
        # 初始化共享链表
        self.head = None  # 整个链表的头节点
        self.tail = None  # 整个链表的尾节点
        self.books = {}  # 存储每本书的信息
        self.pattern = pattern  # 搜索模式
        self.pattern_counts = {}  # 每本书中模式出现的次数
        self.shared_list_lock = threading.Lock()  # 线程锁,用于同步

    def append(self, node):
        # 添加新节点到链表
        with self.shared_list_lock:
            # 添加到主链表
            if self.head is None:
                self.head = node
                self.tail = node
            else:
                self.tail.next = node
                self.tail = node

        # 处理书籍特定的链表
        book = self.books.get(node.book_id)
        if book is None:
            # 如果是新书,创建书籍信息
            book = {'title': node.line.strip(), 'head': node, 'tail': node}
            self.books[node.book_id] = book
            self.pattern_counts[node.book_id] = 0
        else:
            # 如果书已存在,更新尾节点
            book['tail'].book_next = node
            book['tail'] = node

        # 更新模式计数
        if self.pattern in node.line:
            self.pattern_counts[node.book_id] += 1

    def sort_books(self):
        # 根据模式出现次数对书籍进行排序
        with self.shared_list_lock:
            sorted_books = []
            for id, book in self.books.items():
                count = self.pattern_counts.get(id, 0)
                sorted_books.append((id, book['title'], count))

            sorted_books.sort(key=lambda x: x[2], reverse=True)

            return sorted_books
        
    def get_head(self, book_id):
        # 获取指定书籍的头节点
        with self.shared_list_lock:
            book = self.books.get(book_id)
            if book:
                return book['head']
            return None
