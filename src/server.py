import socket
import threading
import argparse
from .linked_list import SharedLinkedList
from .pattern_analysis import analyze_data
from .client_handler import handle_client

def parse_arguments():
    # 创建参数解析器
    parser = argparse.ArgumentParser(description="Start the server.")
    parser.add_argument('-l', type=int, required=True, help='The listen port for the server.')
    parser.add_argument('-p', type=str, required=True, help='The search pattern.')
    args = parser.parse_args()

    # 验证端口号是否有效
    if args.l <= 1024:
        parser.error("The listen port must be greater than 1024.")
    return args

def start_analysis_threads(shared_list, output_lock):
    # 启动两个数据分析线程
    for _ in range(2):
        thread = threading.Thread(target=analyze_data, args=(shared_list, output_lock))
        thread.daemon = True
        thread.start()

def main():
    # 解析命令行参数
    args = parse_arguments()
    port = args.l
    pattern = args.p

    # 初始化共享数据结构和锁
    shared_list = SharedLinkedList(pattern)
    output_lock = threading.Lock()
    book_id_counter_lock = threading.Lock()
    book_id = 0

    # 启动分析线程
    start_analysis_threads(shared_list, output_lock)

    # 创建并配置服务器socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen()
    print(f"Server started on port {port}")

    try:
        while True:
            print("Waiting for a connection...")
            connection, address = server.accept()
            # 为每个新连接分配唯一ID
            with book_id_counter_lock:
                book_id += 1
                id = book_id
            print(f"Accepted connection {id} from {address}")
            # 为每个客户端创建新线程
            client_thread = threading.Thread(target=handle_client, args=(connection, id, shared_list))
            print(f"Starting client thread for connection {id}")
            client_thread.start()
            print(f"Client thread for connection {id} started")
    except KeyboardInterrupt:
        print("Server shutting down...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        server.close()
