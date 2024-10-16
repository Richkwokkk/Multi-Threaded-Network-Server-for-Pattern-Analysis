def write_received_book(book_id, shared_list):
    """
    Write the contents of a received book to a file.

    Args:
        book_id (int): The ID of the book to write.
        shared_list (SharedList): The shared list containing the book data.

    Returns:
        None
    """
    # Get the head node of the book
    head = shared_list.get_head(book_id)
    if head is None:
        print(f"No head found for book {book_id}")
        return

    # Generate the filename for the book
    filename = f"book_{book_id:02d}.txt"
    try:
        # Open the file and write the book contents
        with open(filename, 'w', encoding='utf-8') as f:
            node = head
            while node:
                if node.book_next:
                    node.line += '\n'
                f.write(node.line)
                node = node.book_next
        print(f"Book {book_id} written to {filename}")
    except Exception as e:
        # Handle any errors that occur during file writing
        print(f"Failed to write book {book_id} to file: {e}")
