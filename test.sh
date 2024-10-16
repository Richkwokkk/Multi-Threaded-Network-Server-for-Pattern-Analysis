#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <server_host> <server_port> <pattern> <num_clients> <delay>"
    echo "Example: $0 localhost 12345 \"happy\" 10 0"
    exit 1
fi

# Assign command-line arguments to variables
SERVER_HOST=$1
SERVER_PORT=$2
PATTERN=$3
NUM_CLIENTS=$4
DELAY=$5

# Check if the specified port is in use and kill any processes using it
echo "Checking if port $SERVER_PORT is in use..."
lsof -ti:$SERVER_PORT | xargs kill -9 2>/dev/null

# Start the server
echo "Starting server on $SERVER_HOST:$SERVER_PORT with pattern \"$PATTERN\"..."
./assignment3.py -l $SERVER_PORT -p "$PATTERN" &
SERVER_PID=$!

# Define a function to stop the server
stop() {
    kill -9 $SERVER_PID
}

# Set up a trap to catch SIGINT and SIGTERM signals
trap stop SIGINT SIGTERM

# Wait for the server to start
sleep 2

# Define an array of text files to be used by clients
TEXT_FILES=(
    "books/book1.txt"
    "books/book2.txt"
    "books/book3.txt"
    "books/book4.txt"
    "books/book5.txt"
    "books/book6.txt"
    "books/book7.txt"
    "books/book8.txt"
    "books/book9.txt"
    "books/book10.txt"
)

# Adjust the number of clients if there aren't enough text files
if [ "$NUM_CLIENTS" -gt "${#TEXT_FILES[@]}" ]; then
    echo "Warning: Not enough text files for the number of clients requested"
    echo "Adjusting number of clients to ${#TEXT_FILES[@]}"
    NUM_CLIENTS=${#TEXT_FILES[@]}
fi

echo "Simulating $NUM_CLIENTS clients..."

# Define a function to send data from a file to the server
send_data() {
    FILE=$1
    nc $SERVER_HOST $SERVER_PORT -i $DELAY < "$FILE" &
}

# Loop through the clients and send data
for (( i=0; i<$NUM_CLIENTS; i++ ))
do
    FILE=${TEXT_FILES[$i]}
    if [ ! -f "$FILE" ]; then
        echo "Error: File $FILE does not exist"
        continue
    fi
    echo "Client $((i+1)): Sending $FILE"
    send_data "$FILE"
done

# Wait for all background processes to finish
wait

echo "Stopping server..."

echo "Test completed"
