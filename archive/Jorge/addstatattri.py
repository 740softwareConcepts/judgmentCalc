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

try:
  

    total_entries = 100  # Assuming you have 100 entries in your accounting table
    contractual_percentage = 0.7  # 80% contractual, 20% statutory

    # Calculate the number of entries for each type
    contractual_count = int(total_entries * contractual_percentage)
    statutory_count = total_entries - contractual_count

    # Update rows randomly with 'contractual' and 'statutory' interestType
    for i in range(contractual_count):
        update_query = "UPDATE ACCOUNTING SET interestType = 'contractual' WHERE accountingID = %s"
        cursor.execute(update_query, (i + 1,))  # Assuming accountingID starts from 1
    for i in range(statutory_count):
        update_query = "UPDATE ACCOUNTING SET interestType = 'statutory' WHERE accountingID = %s"
        cursor.execute(update_query, (contractual_count + i + 1,))  # Update remaining rows

    conn.commit()
    print("Interest type updated in the 'accounting' table.")
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    conn.close()