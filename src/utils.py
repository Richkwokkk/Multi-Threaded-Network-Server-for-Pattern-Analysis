def write_received_book(book_id, shared_list):
    # 获取指定书籍ID的头节点
    head = shared_list.get_head(book_id)
    if head is None:
        print(f"No head found for book {book_id}")
        return

    # 生成文件名
    filename = f"book_{book_id:02d}.txt"
    try:
        # 打开文件并写入内容
        with open(filename, 'w', encoding='utf-8') as f:
            node = head
            while node:
                # 逐行写入书籍内容
                f.write(node.line + '\n')
                # 移动到下一个节点
                node = node.book_next
        print(f"Book {book_id} written to {filename}")
    except Exception as e:
        # 捕获并打印写入过程中的任何错误
        print(f"Failed to write book {book_id} to file: {e}")
