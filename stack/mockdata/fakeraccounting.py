import mysql.connector
from faker import Faker
import random
import datetime

# Connect to MySQL (adjust the parameters accordingly)
conn = mysql.connector.connect(
    host="database-1.ctnfprzjtuyt.us-east-1.rds.amazonaws.com",
    user="admin",
    password="Dnnbmstn1jrg",
    database="DataWarehouse"
)
cursor = conn.cursor()

# Create ACCOUNTING table
cursor.execute('''CREATE TABLE IF NOT EXISTS ACCOUNTING (
                accountingID INT AUTO_INCREMENT PRIMARY KEY,
                caseID INT,
                type VARCHAR(50),
                incurredDate DATE,
                amount DECIMAL(10, 2),
                description TEXT,
                FOREIGN KEY (caseID) REFERENCES CASES(caseID)
            )''')


fake = Faker()

# Function to generate liabilities for each case
def generate_liabilities(case_id):
    num_liabilities = random.randint(1, 2)  # On average, 1.5 liabilities per case
    for _ in range(num_liabilities):
        incurred_date = fake.date_time_between(start_date='-10y', end_date='now').strftime('%Y-%m-%d')
        amount = round(random.uniform(400, 300000), 2)
        description = fake.sentence()

        cursor.execute("INSERT INTO ACCOUNTING (caseID, type, incurredDate, amount, description) VALUES (%s, %s, %s, %s, %s)",
                       (case_id, 'liability', incurred_date, amount, description))

# Retrieve existing case IDs from the CASES table
cursor.execute("SELECT caseID FROM CASES")
case_ids = [row[0] for row in cursor.fetchall()]

# Generate liabilities for each case
for case_id in case_ids:
    generate_liabilities(case_id)

# Commit changes to the database
conn.commit()

# Close the connection
conn.close()


