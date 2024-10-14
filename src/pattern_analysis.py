import time
from contextlib import contextmanager

@contextmanager
def acquire_lock(lock):
    acquired = lock.acquire(blocking=False)
    try:
        yield acquired
    finally:
        if acquired:
            lock.release()

def format_results(results):
    return "\n".join(
        f"{idx}. '{title}' - {count} occurrences"
        for idx, (_, title, count) in enumerate(results, start=1)
    )

def analyze_data(shared_list, output_lock, interval=2):
    while True:
        time.sleep(interval)
        with acquire_lock(output_lock) as acquired:
            if not acquired:
                continue
            
            results = shared_list.sort_books()
            if not results:
                continue
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            formatted_results = format_results(results)
            
            print(f"\nAnalysed Results at {timestamp}:")
            print(formatted_results)
            print()
