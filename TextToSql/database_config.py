from dotenv import load_dotenv

import mysql.connector
import os

# Load environment variable from .env file
load_dotenv()

# Alias for mysql.connector.Error
MySQLError = mysql.connector.Error

# SQL queries
CREATE_TABLE = """
    create table if not exists employeeTable(
        employeeID int primary key,
        employeeName varchar(100) not null,
        designation varchar(50) not null,
        salary float not null
    );
"""

ADD_ENTRIES = """
    INSERT INTO employeeTable (employeeID, employeeName, designation, salary)
    VALUES 
    (101001, 'John Doe', 'Software Engineer', '75000'),
    (101002, 'Jane Smith', 'Data Scientist', '85000'),
    (101003, 'Michael Brown', 'Senior Developer', '95000'),
    (101004, 'Emily Davis', 'Project Manager', '105000'),
    (101005, 'William Wilson', 'System Architect', '115000'),
    (101006, 'Olivia Moore', 'QA Tester', '55000'),
    (101007, 'James Taylor', 'Business Analyst', '72000'),
    (101008, 'Sophia White', 'DevOps Engineer', '80000'),
    (101009, 'Benjamin Harris', 'Product Manager', '110000'),
    (101010, 'Isabella Clark', 'UX Designer', '65000');
"""

FETCH_DATA = """
    select * from employeeTable;
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
        
        print("\nTable 'employeeTable' created successfully !!")
        
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
        
        print("\nEntries added successfully !!")
        
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
        print("\nData in employeeTable:")
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
        