import mysql.connector
from datetime import datetime, timedelta

from datetime import datetime

data = [
    ('1/1/2023', 0.075),
    ('1/1/2022', 0.0325),
    ('1/1/2021', 0.0325),
    ('1/1/2020', 0.0475),
    ('1/1/2019', 0.055),
    ('1/1/2018', 0.045),
    ('1/1/2017', 0.0375),
    ('1/1/2016', 0.035),
    ('1/1/2015', 0.0325),
    ('1/1/2014', 0.0325),
    ('1/1/2013', 0.0325),
    ('1/1/2012', 0.0325),
    ('1/1/2011', 0.0325),
    ('1/1/2010', 0.0325),
    ('1/1/2009', 0.0325),
    ('1/1/2008', 0.0725),
    ('1/1/2007', 0.0825),
    ('1/1/2006', 0.0725),
    ('1/1/2005', 0.0525),
    ('1/1/2004', 0.04),
    ('1/1/2003', 0.0425),
    ('1/1/2002', 0.0475),
    ('1/1/2001', 0.095),
    ('1/1/2000', 0.0825),
    ('1/1/1999', 0.0775),
    ('1/1/1998', 0.085),
    ('1/1/1997', 0.0825),
    ('1/1/1996', 0.085),
    ('1/1/1995', 0.085),
    ('1/1/1994', 0.06),
    ('1/1/1993', 0.06),
    ('1/1/1992', 0.065),
    ('1/1/1991', 0.1),
    ('1/1/1990', 0.105),
    ('1/1/1989', 0.105),
    ('1/1/1988', 0.0875),
    ('7/1/2022', 0.0475),
    ('7/1/2021', 0.0325),
    ('7/1/2020', 0.0325),
    ('7/1/2019', 0.055),
    ('7/1/2018', 0.05),
    ('7/1/2017', 0.0425),
    ('7/1/2016', 0.035),
    ('7/1/2015', 0.0325),
    ('7/1/2014', 0.0325),
    ('7/1/2013', 0.0325),
    ('7/1/2012', 0.0325),
    ('7/1/2011', 0.0325),
    ('7/1/2010', 0.0325),
    ('7/1/2009', 0.0325),
    ('7/1/2008', 0.05),
    ('7/1/2007', 0.0825),
    ('7/1/2006', 0.0825),
    ('7/1/2005', 0.0625),
    ('7/1/2004', 0.0425),
    ('7/1/2003', 0.04),
    ('7/1/2002', 0.0475),
    ('7/1/2001', 0.0675),
    ('7/1/2000', 0.095),
    ('7/1/1999', 0.0775),
    ('7/1/1998', 0.085),
    ('7/1/1997', 0.085),
    ('7/1/1996', 0.0825),
    ('7/1/1995', 0.09),
    ('7/1/1994', 0.0725),
    ('7/1/1993', 0.06),
    ('7/1/1992', 0.065),
    ('7/1/1991', 0.085),
    ('7/1/1990', 0.1),
    ('7/1/1989', 0.11),
    ('7/1/1988', 0.09),
    ('7/1/1987', 0.0825)
]

# Ensure dates are in the correct format
formatted_data = [(datetime.strptime(date_str, '%m/%d/%Y'), interest) for date_str, interest in data]


# Function to convert date string to datetime object
def convert_to_date(date_str):
    return datetime.strptime(date_str, '%m/%d/%Y')





# Establish a connection to your MySQL server
connection = mysql.connector.connect(
    host="database-1.ctnfprzjtuyt.us-east-1.rds.amazonaws.com",
    user="admin",
    password="Dnnbmstn1jrg",
    database="DataWarehouse"
)




# Create a cursor object to interact with the database
cursor = connection.cursor()



# Insert the provided data into the table, handling missing dates
insert_query = "INSERT INTO INTEREST (date, interest) VALUES (%s, %s)"

for i in range(len(data)):
    date, interest = data[i]
    date = convert_to_date(date)
    cursor.execute(insert_query, (date, interest))

    # Check for missing dates and fill them with the most recent interest rate
    if i > 0:
        prev_date = convert_to_date(data[i - 1][0])
        while prev_date + timedelta(days=1) < date:
            prev_date += timedelta(days=1)
            cursor.execute(insert_query, (prev_date, data[i - 1][1]))

# Commit the changes and close the connection
connection.commit()
connection.close()

print("Data inserted successfully.")
