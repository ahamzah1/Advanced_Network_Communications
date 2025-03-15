import socket
import os
import threading

# Configuration
SDP = 30000  # Service Discovery Port
FSP = 30001  # File Sharing Port
SERVICE_NAME = "Ahmad's File Sharing Service"
SHARED_DIR = "shared_files"  # Directory for shared files

# Command dictionary
CMD = {
    "get": 1,
    "put": 2,
    "list": 3,
}

if not os.path.exists(SHARED_DIR):
    os.makedirs(SHARED_DIR)

# Function to handle UDP service discovery
def handle_udp_discovery():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.bind(('', SDP))

    print(f"Server listening for UDP broadcasts on port {SDP}...")

    while True:
        data, addr = udp_socket.recvfrom(1024)
        if data.decode().strip() == "SERVICE DISCOVERY":
            print(f"Received SERVICE DISCOVERY request from {addr}")
            udp_socket.sendto(SERVICE_NAME.encode(), addr)

# Function to handle TCP client connections
def handle_tcp_client(client_socket):
    while True:
        # Receive the command byte
        command_byte = client_socket.recv(1)
        if not command_byte:
            break

        command = int.from_bytes(command_byte, byteorder='big')

        if command == CMD["list"]:
            # List files in the shared directory
            files = os.listdir(SHARED_DIR)
            file_list = "\n".join(files).encode()
            client_socket.send(len(file_list).to_bytes(8, byteorder='big'))
            client_socket.send(file_list)

        elif command == CMD["get"]:
            # Receive the filename
            filename = client_socket.recv(1024).decode().strip()
            filepath = os.path.join(SHARED_DIR, filename)

            if os.path.exists(filepath):
                # Send file size and data
                filesize = os.path.getsize(filepath)
                client_socket.send(filesize.to_bytes(8, byteorder='big'))

                with open(filepath, 'rb') as f:
                    client_socket.sendfile(f)
            else:
                # Send 0 file size if file doesn't exist
                client_socket.send((0).to_bytes(8, byteorder='big'))

        elif command == CMD["put"]:
            # Receive the filename
            filename = client_socket.recv(1024).decode().strip()
            filepath = os.path.join(SHARED_DIR, filename)

            # Receive file size
            filesize = int.from_bytes(client_socket.recv(8), byteorder='big')

            if filesize > 0:
                # Receive file data
                with open(filepath, 'wb') as f:
                    remaining = filesize
                    while remaining > 0:
                        data = client_socket.recv(min(remaining, 4096))
                        f.write(data)
                        remaining -= len(data)
                print(f"File {filename} uploaded successfully.")
            else:
                print(f"Invalid file size for {filename}.")

    client_socket.close()

# Function to handle TCP connections
def handle_tcp_connections():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_socket.bind(('', FSP))
    tcp_socket.listen(5)

    print(f"Server listening for TCP connections on port {FSP}...")

    while True:
        client_socket, addr = tcp_socket.accept()
        print(f"Accepted TCP connection from {addr}")
        threading.Thread(target=handle_tcp_client, args=(client_socket,)).start()

# Start UDP and TCP threads
udp_thread = threading.Thread(target=handle_udp_discovery)
tcp_thread = threading.Thread(target=handle_tcp_connections)

udp_thread.start()
tcp_thread.start()

udp_thread.join()
tcp_thread.join()