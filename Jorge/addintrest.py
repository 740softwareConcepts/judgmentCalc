import mysql.connector
import random

# Connect to your MySQL database
conn = mysql.connector.connect(
    host="database-1.ctnfprzjtuyt.us-east-1.rds.amazonaws.com",
    user="admin",
    password="Dnnbmstn1jrg",
    database="DataWarehouse"
)

cursor = conn.cursor()



# Alter the 'interest' attribute in ACCOUNTING table to store decimal values
cursor.execute("ALTER TABLE ACCOUNTING MODIFY COLUMN interest DECIMAL(10,2)")

# Close the connection
conn.close()