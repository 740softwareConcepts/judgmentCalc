import mysql.connector

# Establishing a connection to MySQL
conn = mysql.connector.connect(
    host="database-1.ctnfprzjtuyt.us-east-1.rds.amazonaws.com",
    user="admin",
    password="Dnnbmstn1jrg",
    database="DataWarehouse"
)

# Create a cursor to execute SQL queries
cursor = conn.cursor()

# Create INTEREST table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS INTEREST (
        id INT AUTO_INCREMENT PRIMARY KEY,
        date DATE NOT NULL,
        rate FLOAT NOT NULL,
        UNIQUE (date)
    )
""")
