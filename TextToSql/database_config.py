from dotenv import load_dotenv

import mysql.connector
import os

# Load environment variable from .env file
load_dotenv()

# Alias for mysql.connector.Error
MySQLError = mysql.connector.Error

CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS banking (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        date DATE NOT NULL,
        transaction_amount DECIMAL(10,2) NOT NULL,
        type_of_transaction VARCHAR(100) NOT NULL,
        credit_or_debit VARCHAR(10) CHECK (credit_or_debit IN ('Credit', 'Debit')) NOT NULL,
        balance DECIMAL(10,2) NOT NULL
    );
"""

ADD_ENTRIES = """
    INSERT INTO banking (name, date, transaction_amount, type_of_transaction, credit_or_debit, balance)
    VALUES 
    ('John Doe', '2025-02-01', 50000.0, 'Initial Deposit', 'Credit', 50000.0),
    ('Jane Smith', '2025-02-02', 10000.0, 'Salary', 'Credit', 60000.0),
    ('Michael Johnson', '2025-02-03', 1500.0, 'Grocery', 'Debit', 58500.0),
    ('Emily Davis', '2025-02-04', 5000.0, 'Freelance Income', 'Credit', 63500.0),
    ('Robert Brown', '2025-02-05', 800.0, 'Food', 'Debit', 62700.0),
    ('Olivia Wilson', '2025-02-06', 70000.0, 'Business Profit', 'Credit', 132700.0),
    ('William Garcia', '2025-02-07', 1200.0, 'Shopping', 'Debit', 131500.0),
    ('Sophia Martinez', '2025-02-08', 50000.0, 'Stock Market Profit', 'Credit', 181500.0),
    ('James Anderson', '2025-02-09', 2000.0, 'Travel', 'Debit', 179500.0),
    ('Isabella Thomas', '2025-02-10', 75000.0, 'Real Estate Sale', 'Credit', 254500.0);

"""


FETCH_DATA = """
    select * from banking;
"""

CREATE_BILL_TABLE = """
    CREATE TABLE IF NOT EXISTS bills (
        id INT AUTO_INCREMENT PRIMARY KEY,
        type VARCHAR(50),
        amount DECIMAL(10,2),
        due_date DATE,
        payment_date DATE,
        status ENUM('unpaid', 'paid')
    );
"""

ADD_ENTRIES_TO_BILLS = """
    INSERT INTO bills (type, amount, due_date, payment_date, status) 
    VALUES
    ('electricity', 1200.50, '2025-02-10', '2025-02-12', 'paid'),
    ('internet', 999.99, '2025-02-15', NULL, 'unpaid'),
    ('water', 500.00, '2025-02-05', '2025-02-06', 'paid'),
    ('phone', 650.75, '2025-02-20', NULL, 'unpaid'),
    ('gas', 850.25, '2025-02-18', NULL, 'unpaid'),
    ('credit_card', 5000.00, '2025-02-25', '2025-02-26', 'paid'),
    ('insurance', 2000.00, '2025-03-01', NULL, 'unpaid'),
    ('rent', 15000.00, '2025-02-28', NULL, 'unpaid'),
    ('subscription', 399.99, '2025-02-14', '2025-02-14', 'paid'),
    ('education_loan', 7500.00, '2025-03-05', NULL, 'unpaid');

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



def create_bill_table(database_connection):
    try:
        cursor = database_connection.cursor()
        cursor.execute(CREATE_BILL_TABLE)
        database_connection.commit()
    except MySQLError as err:
        print(f"\nError during creating table: {err}")
    finally:
        cursor.close()

def add_entries_to_bills(database_connection):
    try:
        cursor = database_connection.cursor()
        cursor.execute(ADD_ENTRIES_TO_BILLS)
        database_connection.commit()
    except MySQLError as err:
        print(f"Error while adding entries to bills table: {err}")
    finally:
        cursor.close()
        
    
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
        create_bill_table(database_connection)
        add_entries_to_bills(database_connection)
        
        # Close the connection
        database_connection.close()
        print("\nDatabase connection closed")
        