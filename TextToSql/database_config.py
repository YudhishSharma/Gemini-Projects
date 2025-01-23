from dotenv import load_dotenv

import mysql.connector
import os

# Load environment variable from .env file
load_dotenv()

# Alias for mysql.connector.Error
MySQLError = mysql.connector.Error

# SQL queries required
CREATE_TABLE = """
    create table if not exists employeeTable(
        employeeID int primary key,
        employeeName varchar(100) not null,
        designation varchar(50) not null,
        salary decimal(10, 2) not null
    );
"""

ADD_ENTRIES = """
    INSERT INTO employeeTable (employeeID, employeeName, designation, salary)
    VALUES 
    (8150808, 'Yudhish Sharma', 'Associate Engineer', '123456'),
    (8140440, 'Gavin Schindler', 'Engineer', '3454345'),
    (8135249, 'Krishna Prasad Budamkayala', 'Senior Lead Software Engineer', '55654345'),
    (8156295, 'Manikanta Venkata Sainath Gottipalli', 'Associate Architect', '76766755'),
    (8166121, 'Rajeswari Anamalaboina', 'Senior Software Engineer', '6686433');
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
    except erMySQLError as errr:
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
        