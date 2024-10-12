import argparse
from src.server import Server

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start the server.")
    parser.add_argument('-l', type=int, default=12345, help='The listen port for the server.')
    parser.add_argument('-p', type=str, required=True, help='The search pattern.')
    args = parser.parse_args()

    server = Server('0.0.0.0', args.l, args.p)

    try:
        server.run_server()
    except KeyboardInterrupt:
        print("\nShutting down the server...")
        server.stop_server()
