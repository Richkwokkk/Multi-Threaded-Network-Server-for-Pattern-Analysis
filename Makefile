PYTHON ?= python3
SERVER_FILE = main.py
CLIENT_FILE = client.py
PORT ?= 12345
PATTERN ?= "happy"
BOOKS_DIR = books

.PHONY: all run clean test send_books

all: run

run:
	$(PYTHON) $(SERVER_FILE) -l $(PORT) -p $(PATTERN)

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -f book_*.txt

test:
	PYTHONPATH=. $(PYTHON) -m unittest discover tests

send_books:
	@for book in $(BOOKS_DIR)/*.txt; do \
		echo "Sending $$book to server..."; \
		nc localhost $(PORT) < $$book; \
		echo "Finished sending $$book"; \
		sleep 1; \
	done

assignment3: run
