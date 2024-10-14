import time

def analyze_data(shared_list, output_lock, interval):
    while True:
        time.sleep(interval)
        acquired = output_lock.acquire(blocking=False)
        if acquired:
            try:
                results = shared_list.sort_books()
                if results:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    print(f"\nAnalysed Results at {timestamp}:")
                    for idx, (id, title, count) in enumerate(results, start=1):
                        print(f"{idx}. '{title}' - {count} occurrences")
                    print()
            finally:
                output_lock.release()
        else:
            continue
