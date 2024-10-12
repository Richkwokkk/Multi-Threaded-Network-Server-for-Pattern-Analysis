import threading
import time

class PatternAnalysisThread(threading.Thread):
    output_lock = threading.Lock()
    last_output_time = 0

    def __init__(self, shared_linked_list, pattern, interval=5, thread_id=None):
        super().__init__()
        self.shared_list = shared_linked_list
        self.pattern = pattern
        self.interval = interval
        self.stop_event = threading.Event()
        self.book_counter = {}
        self.book_map = {}
        self.thread_id = thread_id

    def run(self):
        while not self.stop_event.is_set():
            self.analyze_data()
            self.output_results()
            time.sleep(self.interval)

    def analyze_data(self):
        with self.shared_list.shared_list_lock:
            current = self.shared_list.head
            while current:
                if self.pattern.lower() in current.data.lower():
                    if current.book_id not in self.book_counter:
                        self.book_counter[current.book_id] = 1
                        self.book_map[current.book_id] = current.book_title
                    else:
                        self.book_counter[current.book_id] += 1
                current = current.next

    def output_results(self):
        current_time = time.time()
        with PatternAnalysisThread.output_lock:
            if current_time - PatternAnalysisThread.last_output_time >= self.interval:
                PatternAnalysisThread.last_output_time = current_time
                sorted_books = sorted(self.book_counter.items(), key=lambda x: x[1], reverse=True)
                print(f"\nPattern Analysis Report (Thread {self.thread_id})")
                print(f"Search Pattern: '{self.pattern}'")
                print("Results:")
                if sorted_books:
                    for i, (book_id, count) in enumerate(sorted_books, 1):
                        print(f"{i}. {self.book_map[book_id]} - Occurrences: {count}")
                else:
                    print("No matches found.")
                print("-" * 40)
