import csv

CSV_FILE = "course_grades.csv"

def load_database():
    database = {}
    with open(CSV_FILE, mode="r", newline="") as file:
        reader = csv.reader(file)
        headers = next(reader) 

        for row in reader:
            if row[0].isdigit():  
                database[row[1]] = row  

    return database, headers

def authenticate(database):
    while True:
        password = input("Enter your password (or type 'exit' to quit): ").strip()
        
        if password.lower() == "exit":
            return None
        
        if password in database:
            return database[password] 
        
        print("Invalid password. Try again.")

def handle_commands(user_data, headers):
    commands = {
        "GMA": "Midterm",
        "GL1A": "Lab 1",
        "GL2A": "Lab 2",
        "GL3A": "Lab 3",
        "GL4A": "Lab 4",
    }

    while True:
        command = input(f"Enter a command {list(commands.keys())} (or 'logout' to switch user): ").strip().upper()

        if command == "LOGOUT":
            print("\nLogging out...\n")
            return 

        elif command in commands:
            col_name = commands[command]
            col_index = headers.index(col_name)
            print(f"{col_name} Score: {user_data[col_index]}")
        else:
            print("Invalid command. Try again.")


def main():
    database, headers = load_database()

    while True:
        user_data = authenticate(database)

        if user_data is None:  
            print("Exiting program.")
            break

        print(f"\nWelcome, {user_data[3]} {user_data[2]}!") 
        handle_commands(user_data, headers)

if __name__ == "__main__":
    main()
