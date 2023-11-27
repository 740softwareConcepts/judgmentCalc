import mysql.connector
from faker import Faker
from datetime import datetime, timedelta
import random

# Connect to your MySQL server
connection = mysql.connector.connect(
    host="database-1.ctnfprzjtuyt.us-east-1.rds.amazonaws.com",
    user="admin",
    password="Dnnbmstn1jrg",
    database="DataWarehouse"
)

# Create a Faker object
fake = Faker()

# Function to generate random date within a range
def generate_random_date(start_date, end_date):
    return start_date + timedelta(seconds=random.randint(0, int((end_date - start_date).total_seconds())))

# Create tables
create_clients_table_query = """
CREATE TABLE IF NOT EXISTS Clients (
    ClientID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50),
    LastName VARCHAR(50),
    DOB DATE,
    CreateDate DATE
)
"""

create_case_information_table_query = """
CREATE TABLE IF NOT EXISTS CaseInformation (
    CaseID INT AUTO_INCREMENT PRIMARY KEY,
    ClientID INT,
    CreateDate DATE,
    JudgmentDate DATE,
    FOREIGN KEY (ClientID) REFERENCES Clients(ClientID)
)
"""

# Execute table creation queries
cursor = connection.cursor()
cursor.execute(create_clients_table_query)
cursor.execute(create_case_information_table_query)

# Set auto-increment starting values
cursor.execute("ALTER TABLE CaseInformation AUTO_INCREMENT = 1000")


# Generate and insert data for Clients table
for i in range(1, 201):
    name = fake.first_name()
    last_name = fake.last_name()
    dob = fake.date_of_birth(minimum_age=18, maximum_age=80).strftime('%Y-%m-%d')
    create_date = fake.date_time_between(start_date='-5y', end_date='now').strftime('%Y-%m-%d')

    cursor.execute(
        "INSERT INTO Clients (Name, LastName, DOB, CreateDate) VALUES (%s, %s, %s, %s)",
        (name, last_name, dob, create_date)
    )

# Generate and insert data for CaseInformation table
for i in range(1, 201):
    client_id = i
    create_date = fake.date_time_between(start_date='-5y', end_date='now').strftime('%Y-%m-%d')
    judgment_date = generate_random_date(datetime.strptime(create_date, '%Y-%m-%d'), datetime.now()).strftime('%Y-%m-%d')

    cursor.execute(
        "INSERT INTO CaseInformation (ClientID, CreateDate, JudgmentDate) VALUES (%s, %s, %s)",
        (client_id, create_date, judgment_date)
    )

# Commit changes and close connection
connection.commit()
connection.close()
