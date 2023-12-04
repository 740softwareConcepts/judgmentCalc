import mysql.connector
from faker import Faker
from datetime import datetime, timedelta
import random

# Connect to your MySQL server
conn = mysql.connector.connect(
    host="database-1.ctnfprzjtuyt.us-east-1.rds.amazonaws.com",
    user="admin",
    password="Dnnbmstn1jrg",
    database="DataWarehouse"
)

cursor = conn.cursor()


# Create CASES table
cursor.execute('''CREATE TABLE IF NOT EXISTS CASES (
                caseID INT AUTO_INCREMENT PRIMARY KEY,
                caseNumber VARCHAR(10),
                createDate DATETIME,
                updateDate DATETIME
            )''')

# Create CLIENTS table
cursor.execute('''CREATE TABLE IF NOT EXISTS CLIENTS (
                clientID INT AUTO_INCREMENT PRIMARY KEY,
                firstName VARCHAR(255),
                lastName VARCHAR(255),
                type VARCHAR(50),
                caseID INT,
                createDate DATETIME,
                updateDate DATETIME,
                FOREIGN KEY (caseID) REFERENCES CASES(caseID)
            )''')            

# Generate 50 unique case numbers
case_numbers = set()
while len(case_numbers) < 50:
    case_numbers.add(f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') * 2}{random.randint(10000, 99999)}")

# Insert 50 random case numbers into CASES table
for case_number in case_numbers:
    cursor.execute("INSERT INTO CASES (caseNumber) VALUES (%s)", (case_number,))

# Commit changes to the database
conn.commit()

# Initialize Faker
fake = Faker()

# Prepare lists for plaintiffs and defendants
plaintiffs = []
defendants = []

# Generate and insert fake data into CLIENTS table
for _ in range(50):
    # Generate plaintiffs
    first_name = fake.first_name()
    last_name = fake.last_name()
    create_date = fake.date_time_between(start_date='-4y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
    update_date = create_date
    plaintiffs.append((first_name, last_name, create_date, update_date))

    # Generate corresponding defendants for each plaintiff
    first_name = fake.first_name()
    last_name = fake.last_name()
    create_date = fake.date_time_between(start_date='-4y', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
    update_date = create_date
    defendants.append((first_name, last_name, create_date, update_date))

# Shuffle the order of plaintiffs and defendants to match them
random.shuffle(plaintiffs)
random.shuffle(defendants)

# Insert plaintiffs and defendants into CLIENTS table, ensuring each case has one plaintiff and one defendant
for i in range(50):
    case_id = i + 1
    plaintiff = plaintiffs[i]
    defendant = defendants[i]

    cursor.execute("INSERT INTO CLIENTS (firstName, lastName, type, caseID, createDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s)",
                   (plaintiff[0], plaintiff[1], 'plaintiff', case_id, plaintiff[2], plaintiff[3]))

    cursor.execute("INSERT INTO CLIENTS (firstName, lastName, type, caseID, createDate, updateDate) VALUES (%s, %s, %s, %s, %s, %s)",
                   (defendant[0], defendant[1], 'defendant', case_id, defendant[2], defendant[3]))
    
    
    # Update the CASES table with the updateDate of the defendant for the corresponding case
    cursor.execute("UPDATE CASES SET updateDate = %s WHERE caseID = %s",
                   (defendant[3], case_id))

    # Update the CASES table with the createDate of the defendant for the corresponding case
    cursor.execute("UPDATE CASES SET createDate = %s WHERE caseID = %s",
                   (defendant[2], case_id))
# Commit changes to the database
conn.commit()

# Close the connection
conn.close()





