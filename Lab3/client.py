import socket
import os
import sys
import time

# Configuration
SDP = 30000  # Service Discovery Port
FSP = 30001  # File Sharing Port
LOCAL_DIR = "client_files"  # Local directory for client files
TIMEOUT = 5  # Timeout for service discovery in seconds

# Command dictionary
CMD = {
    "get": 1,
    "put": 2,
    "list": 3,
}

if not os.path.exists(LOCAL_DIR):
    os.makedirs(LOCAL_DIR)

# Function to scan for services
def scan_for_services():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.settimeout(TIMEOUT)

    # Send SERVICE DISCOVERY broadcast
    print("Scanning for file sharing services...")
    udp_socket.sendto(b"SERVICE DISCOVERY", ('255.255.255.255', SDP))

    try:
        while True:
            data, addr = udp_socket.recvfrom(1024)
            service_name = data.decode()
            print(f"{service_name} found at IP address/port {addr[0]}:{addr[1]}")
    except socket.timeout:
        print("No service found.")

# Function to connect to a server
def connect_to_server(ip, port):
    try:
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.connect((ip, port))
        print(f"Connected to server at {ip}:{port}")
        return tcp_socket
    except Exception as e:
        print(f"Failed to connect to server: {e}")
        return None

# Function to list local files
def list_local_files():
    files = os.listdir(LOCAL_DIR)
    if files:
        print("Local files:")
        for file in files:
            print(file)
    else:
        print("No files in local directory.")

# Function to list remote files
def list_remote_files(tcp_socket):
    if tcp_socket:
        tcp_socket.send(CMD["list"].to_bytes(1, byteorder='big'))
        filesize = int.from_bytes(tcp_socket.recv(8), byteorder='big')
        file_list = tcp_socket.recv(filesize).decode()
        print("Remote files:")
        print(file_list)
    else:
        print("Not connected to a server.")

# Function to upload a file
def upload_file(tcp_socket, filename):
    if tcp_socket:
        filepath = os.path.join(LOCAL_DIR, filename)
        if os.path.exists(filepath):
            tcp_socket.send(CMD["put"].to_bytes(1, byteorder='big'))
            tcp_socket.send(filename.encode())

            filesize = os.path.getsize(filepath)
            tcp_socket.send(filesize.to_bytes(8, byteorder='big'))

            with open(filepath, 'rb') as f:
                tcp_socket.sendfile(f)
            print(f"File {filename} uploaded successfully.")
        else:
            print(f"File {filename} not found in local directory.")
    else:
        print("Not connected to a server.")

# Function to download a file
def download_file(tcp_socket, filename):
    if tcp_socket:
        tcp_socket.send(CMD["get"].to_bytes(1, byteorder='big'))
        tcp_socket.send(filename.encode())

        filesize = int.from_bytes(tcp_socket.recv(8), byteorder='big')
        if filesize > 0:
            filepath = os.path.join(LOCAL_DIR, filename)
            with open(filepath, 'wb') as f:
                remaining = filesize
                while remaining > 0:
                    data = tcp_socket.recv(min(remaining, 4096))
                    f.write(data)
                    remaining -= len(data)
            print(f"File {filename} downloaded successfully.")
        else:
            print(f"File {filename} not found on server.")
    else:
        print("Not connected to a server.")

# Main client loop
def client_loop():
    tcp_socket = None
    while True:
        command = input("> ").strip().split()
        if not command:
            continue

        if command[0] == "scan":
            scan_for_services()

        elif command[0] == "connect" and len(command) == 3:
            ip = command[1]
            port = int(command[2])
            tcp_socket = connect_to_server(ip, port)

        elif command[0] == "llist":
            list_local_files()

        elif command[0] == "rlist":
            list_remote_files(tcp_socket)

        elif command[0] == "put" and len(command) == 2:
            upload_file(tcp_socket, command[1])

        elif command[0] == "get" and len(command) == 2:
            download_file(tcp_socket, command[1])

        elif command[0] == "bye":
            if tcp_socket:
                tcp_socket.close()
                tcp_socket = None
                print("Disconnected from server.")
            else:
                print("Not connected to a server.")

        else:
            print("Invalid command.")

# Start the client
if __name__ == "__main__":
    print("Client started. Type 'help' for a list of commands.")
    client_loop()