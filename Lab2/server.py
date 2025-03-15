import csv
import socket
import hashlib

HOST = "127.0.0.1"  
PORT = 65432      

GET_MIDTERM_AVG_CMD = "GMA"
GET_LAB_1_AVG_CMD = "GL1A"
GET_LAB_2_AVG_CMD = "GL2A"
GET_LAB_3_AVG_CMD = "GL3A"
GET_LAB_4_AVG_CMD = "GL4A"

CSV_FILE = "course_grades.csv"

def load_database():
    database = {}
    averages = {}
    
    with open(CSV_FILE, mode="r", newline="") as file:
        reader = csv.reader(file)
        headers = next(reader)  # Read the header row

        # **Fix:** Use actual column names instead of cmd[1:]
        lab_mapping = {
            GET_LAB_1_AVG_CMD: "Lab 1",
            GET_LAB_2_AVG_CMD: "Lab 2",
            GET_LAB_3_AVG_CMD: "Lab 3",
            GET_LAB_4_AVG_CMD: "Lab 4"
        }
        
        lab_indices = {cmd: headers.index(name) for cmd, name in lab_mapping.items()}
        midterm_index = headers.index("Midterm")

        total_scores = {cmd: 0 for cmd in lab_indices}
        total_midterm = 0
        student_count = 0

        for row in reader:
            if row[0].isdigit():  # Ignore "Averages" row
                student_count += 1
                database[row[1]] = row  # Store student data (key: hashed password)

                total_midterm += int(row[midterm_index])
                for cmd, idx in lab_indices.items():
                    total_scores[cmd] += int(row[idx])

        if student_count > 0:
            averages[GET_MIDTERM_AVG_CMD] = total_midterm / student_count
            for cmd, total in total_scores.items():
                averages[cmd] = total / student_count

    return database, averages


def authenticate(database, received_hash):
    return database.get(received_hash)

def handle_client(client_socket, database, averages):
    try:
        while True:
            data = client_socket.recv(1024).decode().strip()
            if not data:
                break 

            if data in averages:
                response = f"Average {data}: {averages[data]:.2f}"
            else:
                user_data = authenticate(database, data)
                if user_data:
                    response = f"Authenticated: {user_data[3]} {user_data[2]}, Midterm: {user_data[4]}, Labs: {user_data[5:]}"
                else:
                    response = "ERROR: Invalid credentials or command."

            client_socket.send(response.encode())

    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def start_server():
    database, averages = load_database()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"Server listening on {HOST}:{PORT}...")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connected to {addr}")
            handle_client(client_socket, database, averages)

if __name__ == "__main__":
    start_server()
