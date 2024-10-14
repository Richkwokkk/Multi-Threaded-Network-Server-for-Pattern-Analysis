from .linked_list import Node
from .utils import write_received_book

# 处理客户端连接的主函数
def handle_client(client_socket, book_id, shared_list):
    print(f"Handling client {book_id}")
    client_socket.setblocking(False)  # 设置非阻塞模式
    buffer = ""

    try:
        while True:
            # 处理接收到的数据
            buffer = process_incoming_data(client_socket, buffer)
            if not buffer:
                print(f"No more data from client {book_id}")
                break
            # 处理缓冲区中的数据
            buffer = process_buffer(buffer, book_id, shared_list)
    except Exception as e:
        print(f"Error handling client {book_id}: {e}")
    finally:
        # 清理连接
        cleanup(client_socket, book_id, shared_list)
    
    print(f"Finished handling client {book_id}")

# 处理接收到的数据
def process_incoming_data(client_socket, buffer):
    try:
        data = client_socket.recv(1024)  # 接收数据
        if not data:
            return ""
        return buffer + data.decode('utf-8', errors='ignore')  # 解码并添加到缓冲区
    except BlockingIOError:
        return buffer  # 如果没有可用数据，返回原缓冲区

# 处理缓冲区中的数据
def process_buffer(buffer, book_id, shared_list):
    while '\n' in buffer:
        line, buffer = buffer.split('\n', 1)  # 分割一行数据
        line = line.strip()
        node = Node(line, book_id)  # 创建新节点
        shared_list.append(node)  # 添加到共享列表
        print(f"Added node from connection {book_id}: {line}")
    return buffer  # 返回剩余的缓冲区数据

# 清理连接
def cleanup(client_socket, book_id, shared_list):
    client_socket.close()  # 关闭socket连接
    print(f"Connection {book_id} closed.")
    write_received_book(book_id, shared_list)  # 将接收到的数据写入文件
