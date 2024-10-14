import time
from contextlib import contextmanager

@contextmanager
def acquire_lock(lock):
    # 尝试非阻塞方式获取锁
    acquired = lock.acquire(blocking=False)
    try:
        # 返回是否成功获取锁
        yield acquired
    finally:
        # 如果成功获取了锁，在退出时释放
        if acquired:
            lock.release()

def format_results(results):
    # 格式化结果为字符串列表
    return "\n".join(
        f"{idx}. '{title}' - {count} occurrences"
        for idx, (_, title, count) in enumerate(results, start=1)
    )

def analyze_data(shared_list, output_lock, interval=2):
    while True:
        # 每隔指定时间间隔执行一次分析
        time.sleep(interval)
        with acquire_lock(output_lock) as acquired:
            # 如果无法获取锁，跳过本次循环
            if not acquired:
                continue
            
            # 对共享列表进行排序
            results = shared_list.sort_books()
            # 如果结果为空，跳过本次循环
            if not results:
                continue
            
            # 获取当前时间戳
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            # 格式化结果
            formatted_results = format_results(results)
            
            # 打印分析结果
            print(f"\nAnalysed Results at {timestamp}:")
            print(formatted_results)
            print()
