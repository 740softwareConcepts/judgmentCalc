

import mysql.connector

# Establishing a connection to MySQL
connection = mysql.connector.connect(
    host="master.ctnfprzjtuyt.us-east-1.rds.amazonaws.com",
    user="admin ",
    password="(*Dnnbmstn1jrg&*)",
    database="dbmaster"
)

# Creating a cursor object using the cursor() method
cursor = connection.cursor()

# Creating a table with updateDate column
create_table_query = '''
CREATE TABLE IF NOT EXISTS DEMO (
    callid VARCHAR(50),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    updateDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
'''

# Executing the query
cursor.execute(create_table_query)
print("Table created successfully!")

# Closing the cursor and connection
cursor.close()
connection.close()