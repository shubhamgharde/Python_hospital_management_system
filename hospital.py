import hashlib
import datetime
import mysql.connector

# Database connection configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "hospital_db",
}

# Establishing a connection to the MySQL server
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# SQL query to create the 'users' table
create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(255) PRIMARY KEY,
    hashed_password VARCHAR(255)
)
"""

# SQL query to create the 'doctors' table
create_doctors_table = """
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_name VARCHAR(255),
    specialty VARCHAR(255)
)
"""

# SQL query to create the 'patients' table
create_patients_table = """
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(255),
    age INT
)
"""

# SQL query to create the 'appointments' table
create_appointments_table = """
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT,
    patient_id INT,
    appointment_date DATETIME
)
"""

# Execute the SQL queries to create the tables
cursor.execute(create_users_table)
cursor.execute(create_doctors_table)
cursor.execute(create_patients_table)
cursor.execute(create_appointments_table)

# Commit the changes, close the cursor, and the connection
connection.commit()




# Load existing data from the database
def load_data_from_db(table_name):
    data = {}
    try:
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)  # Fixed: Added dot (.) here
        for row in cursor.fetchall():
            key, *values = row
            data[key] = ','.join(map(str, values))
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    return data

# Save data to the database
def save_data_to_db(table_name, data):
    try:
        # Delete existing data related to the specific table
        cursor.execute(f"DELETE FROM {table_name}")
        
        # Insert new data into the table
        for key, value in data.items():
            values = value.split(',')
            placeholders = ', '.join(['%s'] * len(values))
            query = f"INSERT INTO {table_name} VALUES (%s, {placeholders})"
            cursor.execute(query, (key, *values))
            
        connection.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        connection.rollback()

# Add a new user to the database
def add_user(username, hashed_password):
    users_database[username] = hashed_password
    save_data_to_db("users", users_database)

# Load existing data from the database at the beginning
users_database = load_data_from_db("users")
doctors_database = load_data_from_db("doctors")
patients_database = load_data_from_db("patients")
appointments_database = load_data_from_db("appointments")

def create_account():
    print("Create a new account:")
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    hashed_password = hash_password(password)

    # Store the user information in the database
    add_user(username, hashed_password)

    print("Account created successfully!\n")

def hash_password(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

def login():
    print("Login:")
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    hashed_password = hash_password(password)

    # Check if the user exists and the password is correct
    if username in users_database and hashed_password == users_database[username]:
        user_role = 'admin' if username == 'admin_username' else 'user'  # Replace 'admin_username' with your admin username
        print(f"Login successful as {user_role}!\n")
        admin_menu()
        return True, user_role
        
    else:
        print("Invalid username or password. Please try again.\n")
        return False, None

def add_doctor():
    print("Add a new doctor:")
    doctor_name = input("Enter doctor's name: ")
    specialty = input("Enter doctor's specialty: ")

    doctor_id = len(doctors_database) + 1
    doctors_database[doctor_id] = f"{doctor_name},{specialty}"
    save_data_to_db("doctors", doctors_database)

    print(f"Doctor {doctor_name} added successfully with ID {doctor_id}\n")

def add_patient():
    print("Add a new patient:")
    patient_name = input("Enter patient's name: ")
    age = input("Enter patient's age: ")

    patient_id = len(patients_database) + 1
    patients_database[patient_id] = f"{patient_name},{age}"
    save_data_to_db("patients", patients_database)

    print(f"Patient {patient_name} added successfully with ID {patient_id}\n")

def schedule_appointment():
    print("Schedule a new appointment:")
    doctor_id = input("Enter doctor's ID: ")
    patient_id = input("Enter patient's ID: ")

    doctor_id = int(doctor_id)
    patient_id = int(patient_id)

    if doctor_id in doctors_database and patient_id in patients_database:
        appointment_id = len(appointments_database) + 1
        date_time = input("Enter date and time (YYYY-MM-DD HH:MM): ")
        try:
            appointment_date = datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M")
            appointments_database[appointment_id] = f"{doctor_id},{patient_id},{appointment_date}"
            save_data_to_db("appointments", appointments_database)

            print(f"Appointment scheduled successfully with ID {appointment_id}\n")
        except ValueError:
            print("Invalid date and time format. Please use YYYY-MM-DD HH:MM.\n")
    else:
        print("Invalid doctor's ID or patient's ID. Please check and try again.\n")

def admin_menu():
    while True:
        print("Admin Menu:")
        print("1. Add Doctor")
        print("2. Add Patient")
        print("3. Schedule Appointment")
        print("4. Logout")

        admin_choice = input("Enter your choice (1/2/3/4): ")

        if admin_choice == "1":
            add_doctor()
        elif admin_choice == "2":
            add_patient()
        elif admin_choice == "3":
            schedule_appointment()
        elif admin_choice == "4":
            print("Logging out.\n")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.\n")

def user_menu():
    while True:
        print("User Menu:")
        print("1. View Appointments")
        print("2. Logout")

        user_choice = input("Enter your choice (1/2): ")

        if user_choice == "1":
            view_appointments()
        elif user_choice == "2":
            print("Logging out.\n")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.\n")

def view_appointments():
    print("View Appointments for a Patient:")
    patient_name = input("Enter the patient's name: ")

    found_appointments = False
    for appointment_id, details in appointments_database.items():
        parts = details.split(',')
        
        if len(parts) < 3:
            print(f"Error: Invalid data for appointment {appointment_id}. Skipping.")
            continue

        doctor_id, patient_id, appointment_date_str = map(str, parts)

        try:
            appointment_date = datetime.datetime.strptime(appointment_date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            print(f"Error: Invalid date and time format for appointment {appointment_id}. Skipping.")
            continue

        doctor_name, specialty = map(str, doctors_database.get(int(doctor_id), "").split(','))
        patient_info = patients_database.get(int(patient_id), "")
        if patient_info:
            patient_name_db, age = map(str, patient_info.split(','))
            if patient_name == patient_name_db:
                found_appointments = True
                print(f"Appointment ID: {appointment_id}")
                print(f"Doctor: {doctor_name}, Specialty: {specialty}")
                print(f"Patient: {patient_name_db}, Age: {age}")
                print(f"Date and Time: {appointment_date}")
                print("------")

    if not found_appointments:
        print(f"No appointments found for patient {patient_name}.")


def doctor_menu():
    print("Doctor Menu:")
    # Add doctor-specific functionalities here
    print("Logout\n")

def hospital_management_system():
    while True:
        print("1. Sign Up")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ")

        if choice == "1":
            create_account()
        elif choice == "2":
            login_status, user_role = login()
            if login_status:
                if user_role == 'admin':
                    admin_menu()
                elif user_role == 'user':
                    user_menu()
                elif user_role == 'doctor':
                    doctor_menu()
        elif choice == "3":
            print("Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.\n")

if __name__ == "__main__":
    # hospital_management_system()
    user_menu()

# Finally, close the connection when the program finishes
cursor.close()
connection.close()
