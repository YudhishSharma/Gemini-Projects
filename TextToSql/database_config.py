from dotenv import load_dotenv

import mysql.connector
import os

# Load environment variable from .env file
load_dotenv()

# Alias for mysql.connector.Error
MySQLError = mysql.connector.Error

# SQL queries
CREATE_TABLE = """
    create table if not exists banking(
        id int primary key,
        name varchar(100) not null,
        date Date not null,
        transaction_amount float not null,
        type_of_transaction varchar(100) not null,
        balance float not null
    );
"""

ADD_ENTRIES = """
    INSERT INTO banking (id, name, date, transaction_amount, type_of_transaction, balance)
    VALUES 
    (1, 'John Doe', '2025-01-01', 500.0, 'Grocery', 1500.0),
    (2, 'Jane Smith', '2025-01-02', 200.0, 'Food', 1300.0),
    (3, 'Michael Johnson', '2025-01-03', 300.0, 'Travel', 1600.0),
    (4, 'Emily Davis', '2025-01-04', 150.0, 'Beauty', 1450.0),
    (5, 'Robert Brown', '2025-01-05', 700.0, 'Grocery', 2150.0),
    (6, 'Olivia Wilson', '2025-01-06', 400.0, 'Food', 1750.0),
    (7, 'William Garcia', '2025-01-07', 600.0, 'Travel', 2350.0),
    (8, 'Sophia Martinez', '2025-01-08', 250.0, 'Beauty', 2100.0),
    (9, 'James Anderson', '2025-01-09', 800.0, 'Grocery', 2900.0),
    (10, 'Isabella Thomas', '2025-01-10', 100.0, 'Food', 2800.0);
"""

FETCH_DATA = """
    select * from banking;
"""


# Function to connect to the database
def get_database_connection():
    database_connection = mysql.connector.connect(
        host = os.getenv("DB_HOST"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        database = os.getenv("DB_DATABASE")
    )

    if database_connection.is_connected():
        print("\nConnected to the MySQL server successfully");
    else:
        print("\nConnection failed")
        
    return database_connection

# Funtion to create table 
def create_table(database_connection):
    # Try and except to ensure smooth functioning and hadle any exception if occured
    try:
        # Cursor to perform actions
        cursor = database_connection.cursor()
        
        # Create an employee table
        cursor.execute(CREATE_TABLE)
        
        # print("\nTable 'employeeTable' created successfully !!")
        
        # Commit the changes
        database_connection.commit()
    except MySQLError as err:
        print(f"\nError during creating table: {err}")
    finally:
        cursor.close()

# Funtion to add entries to the table 
def add_entries_to_table(database_connection):
    # Try and except to ensure smooth functioning and hadle any exception if occured
    try:
        # Cursor to perform actions
        cursor = database_connection.cursor()
        
        # Add entries to the table
        cursor.execute(ADD_ENTRIES)
        
        # print("\nEntries added successfully !!")
        
        # Commit the changes
        database_connection.commit()
    except MySQLError as errr:
        print(f"\nError during adding entries: {err}")
    finally:
        cursor.close()
        
# Funtion to print the contents of the table 
def fetch_data(database_connection):
    # Try and except to ensure smooth functioning and hadle any exception if occured
    try:
        # Cursor to perform actions
        cursor = database_connection.cursor()
        
        # Get all the details of the table
        cursor.execute(FETCH_DATA)
        
        # Store the results and output the same
        results = cursor.fetchall()
        
        # Print the result
        # print("\nData in employeeTable:")
        for rows in results:
            print(rows)
        
        # Commit the changes
        database_connection.commit()
    except MySQLError as err:
        print(f"\nError during fetching data: {err}")
    finally:
        cursor.close()
        
# Call the functions
if __name__ == "__main__":
    database_connection = get_database_connection()
    if database_connection:
        create_table(database_connection)
        add_entries_to_table(database_connection)
        fetch_data(database_connection)
        
        # Close the connection
        database_connection.close()
        print("\nDatabase connection closed")
        