

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


# Add 'judgmentDate' attribute to ACCOUNTING table
cursor.execute("ALTER TABLE ACCOUNTING ADD COLUMN judgmentDate DATE")

# Close the connection
conn.close()