import threading
import time

class PatternAnalysisThread(threading.Thread):
    output_event = threading.Event()
    output_lock = threading.Lock()

    def __init__(self, shared_linked_list, pattern, interval=5, thread_id=0):
        super().__init__()
        self.shared_linked_list = shared_linked_list
        self.pattern = pattern
        self.interval = interval
        self.thread_id = thread_id
        self.stop_event = threading.Event()
        self.last_processed_node = None
        self.book_counter = {}
        self.book_map = {}

    def run(self):
        last_output_time = time.time()
        print(f"Thread-{self.thread_id} Analysis start")

        while not self.stop_event.is_set():
            acquired = self.shared_linked_list.shared_list_lock.acquire(blocking=False)
            if acquired:
                try:
                    self.count_pattern_occurrences()
                finally:
                    self.shared_linked_list.shared_list_lock.release()

            current_time = time.time()
            if current_time - last_output_time >= self.interval:
                self.try_output_results()
                last_output_time = current_time

    def count_pattern_occurrences(self):
        current_node = (self.last_processed_node.next_frequent_search
                        if self.last_processed_node and self.last_processed_node.next_frequent_search
                        else (self.last_processed_node.next
                              if self.last_processed_node
                              else self.shared_linked_list.head))

        previous_node_with_pattern = None

        while current_node:
            book_id = current_node.book_id
            words = current_node.data.split()
            count = words.count(self.pattern)

            if book_id not in self.book_map:
                self.book_map[book_id] = current_node.book_title

            if count:
                if previous_node_with_pattern and not previous_node_with_pattern.next_frequent_search:
                    previous_node_with_pattern.next_frequent_search = current_node
                previous_node_with_pattern = current_node

                if book_id in self.book_counter:
                    self.book_counter[book_id] += count
                else:
                    self.book_counter[book_id] = count

            self.last_processed_node = current_node
            current_node = current_node.next_frequent_search if current_node.next_frequent_search else current_node.next

    def try_output_results(self):
        with PatternAnalysisThread.output_lock:
            if not PatternAnalysisThread.output_event.is_set():
                sorted_books = sorted(self.book_counter.items(), key=lambda x: x[1], reverse=True)
                print(f"Current time: {time.strftime('%H:%M:%S', time.localtime())}")
                if len(sorted_books) > 0:
                    print(f"Thread {self.thread_id} Print Patterns:")
                    for i, (book_id, count) in enumerate(sorted_books):
                        print(f"{i+1} - {self.book_map[book_id]} - Count: {count}")
                    print("\n")
                PatternAnalysisThread.output_event.set()
                threading.Timer(1, PatternAnalysisThread.output_event.clear).start()
