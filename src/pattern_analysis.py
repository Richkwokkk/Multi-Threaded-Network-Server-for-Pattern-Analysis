import time
from contextlib import contextmanager

@contextmanager
def acquire_lock(lock):
    """
    A context manager for acquiring and releasing a lock.
    
    Args:
        lock: The lock object to acquire and release.
    
    Yields:
        bool: True if the lock was acquired, False otherwise.
    """
    acquired = lock.acquire(blocking=False)
    try:
        yield acquired
    finally:
        if acquired:
            lock.release()

def format_results(results):
    """
    Format the analysis results into a string.
    
    Args:
        results: A list of tuples containing book information and occurrence count.
    
    Returns:
        str: A formatted string of the results.
    """
    return "\n".join(
        f"{idx}. '{title}' - {count} occurrences"
        for idx, (_, title, count) in enumerate(results, start=1)
    )

def analyze_data(shared_list, output_lock, interval=2):
    """
    Continuously analyze data from a shared list and print results.
    
    Args:
        shared_list: A shared data structure containing book information.
        output_lock: A lock to synchronize output operations.
        interval (int, optional): The time interval between analyses in seconds. Defaults to 2.
    """
    while True:
        time.sleep(interval)
        with acquire_lock(output_lock) as acquired:
            if not acquired:
                continue
            
            # Sort books and get results
            results = shared_list.sort_books()
            if not results:
                continue
            
            # Format and print the results
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            formatted_results = format_results(results)
            
            print(f"\nAnalysed Results at {timestamp}:")
            print(formatted_results)
            print()
