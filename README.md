# Book Analysis Server

This project implements a multi-threaded server that receives book content from multiple clients, analyzes the frequency of a specified pattern in the books, and provides real-time analysis results.

## Features

- Multi-threaded server capable of handling multiple client connections simultaneously
- Real-time pattern analysis across all received book content
- Periodic output of top books based on pattern frequency
- Non-blocking I/O for efficient client handling
- Thread-safe data structures for concurrent operations
- Automatic saving of received book content to files

## Project Structure

The project consists of the following main components:

- `src/server.py`: Main server script that handles incoming connections and initializes the system
- `src/client_handler.py`: Manages individual client connections and processes incoming data
- `src/pattern_analysis.py`: Performs periodic analysis of the received data
- `src/linked_list.py`: Implements a custom linked list data structure for efficient data management
- `src/utils.py`: Contains utility functions, such as writing received books to files
- `tests/test.sh`: A bash script for testing the server with multiple simulated clients

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Richkwokkk/Multi-Threaded-Network-Server-for-Pattern-Analysis
   ```

2. Ensure you have Python 3 installed on your system.

3. No additional dependencies are required as the project uses only Python standard libraries.

## Usage

To start the server, run the following command:

```
python -m src.server -l <port> -p <pattern>
```
Where:
- `<port>` is the port number the server should listen on (must be greater than 1024)
- `<pattern>` is the search pattern to analyze in the books

## How It Works

1. The server starts and listens for incoming connections on the specified port.
2. For each client connection, a new thread is spawned to handle the client.
3. Clients send book content line by line. Each line is added to a shared linked list data structure.
4. Two analysis threads periodically process the shared data, counting pattern occurrences and sorting books by frequency.
5. Analysis results are printed to the console at regular intervals.
6. When a client disconnects, the received book content is saved to a text file.

## Testing

A bash script `tests/test.sh` is provided to test the server with multiple simulated clients. To use the test script:

1. Ensure the script is executable:
   ```
   chmod +x tests/test.sh
   ```

2. Run the script with the following parameters:
   ```
   ./tests/test.sh <server_host> <server_port> <pattern> <num_clients> <delay>
   ```

   Example:
   ```
   ./tests/test.sh localhost 12345 "happy" 10 0
   ```

   This will:
   - Start the server on localhost:12345 with the pattern "happy"
   - Simulate 10 clients sending book content to the server
   - Use no delay between sending lines (0)

The test script will:
- Check if the specified port is in use and kill any existing process using it
- Start the server
- Send content from multiple text files (located in a `books/` directory) to simulate clients
- Stop the server after all clients have finished sending data

Note: Ensure you have the necessary text files in the `books/` directory before running the test script.