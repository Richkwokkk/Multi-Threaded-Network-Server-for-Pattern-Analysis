def write_received_book(book_id, shared_list):
    head = shared_list.get_head(book_id)
    if head is None:
        print(f"No head found for book {book_id}")
        return

    filename = f"book_{book_id:02d}.txt"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            node = head
            while node and node.book_id == book_id:
                f.write(node.data + '\n')
                node = node.book_next
        print(f"Book {book_id} written to {filename}")
    except Exception as e:
        print(f"Failed to write book {book_id} to file: {e}")