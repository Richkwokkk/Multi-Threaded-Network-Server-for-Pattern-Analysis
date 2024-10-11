import threading

class PatternAnalysisThread(threading.Thread):
    def __init__(self, shared_list, pattern):
        threading.Thread.__init__(self)
        self.shared_list = shared_list
        self.pattern = pattern
        self.lock = threading.Lock()
        self.output_lock = threading.Lock()
        self.output_event = threading.Event()

    def run(self):
        count = self.count_pattern_occurrences()
        self.try_output_results(count)

    def count_pattern_occurrences(self):
        count = 0
        current_node = self.shared_list.head
        while current_node:
            count += current_node.data.count(self.pattern)
            current_node = current_node.next
        return count

    def try_output_results(self, count):
        with self.output_lock:
            if not self.output_event.is_set():
                print(f"Pattern: {self.pattern} - Count: {count}")
                self.output_event.set()
                interval = 10
                threading.Timer(interval, self.output_event.clear).start()
