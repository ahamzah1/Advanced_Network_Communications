import socket
import hashlib

# Server configuration
SERVER_HOST = "127.0.0.1"  # Change this to the actual server IP
SERVER_PORT = 65432

# Function to hash a password (simulate client-side hashing)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print("Connected to server.")

        while True:
            message = input("Enter command or hashed password (or 'exit' to quit): ").strip()
            
            if message.lower() == "exit":
                break

            client_socket.send(message.encode())
            response = client_socket.recv(1024).decode()
            print("Server Response:", response)

if __name__ == "__main__":
    main()
