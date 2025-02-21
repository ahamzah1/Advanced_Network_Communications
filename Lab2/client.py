import socket
import hashlib
import getpass

# Server configuration
SERVER_HOST = "127.0.0.1"  # Change this to the actual server IP if needed
SERVER_PORT = 65432

# Function to hash the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print("Connected to server.")

        while True:
            command = input("Enter command (GG, GMA, GL1A, GL2A, GL3A, GL4A) or 'exit' to quit: ").strip().upper()
            
            if command == "EXIT":
                break

            if command == "GG":
                # Prompt for authentication details
                student_id = input("Enter your student ID: ").strip()
                password = getpass.getpass("Enter your password: ").strip()

                # Print received values
                print(f"ID number {student_id} and password {password} received.")

                # Hash the password before sending
                hashed_password = hash_password(password)

                # Send the hashed password to the server
                client_socket.send(hashed_password.encode())

                # Get authentication response
                response = client_socket.recv(1024).decode()
                print("Server Response:", response)

            elif command in {"GMA", "GL1A", "GL2A", "GL3A", "GL4A"}:
                # Send command without authentication
                client_socket.send(command.encode())
                response = client_socket.recv(1024).decode()
                print("Server Response:", response)
            
            else:
                print("Invalid command. Please enter a valid command.")

if __name__ == "__main__":
    main()
