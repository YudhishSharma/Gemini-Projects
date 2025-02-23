# Function to connect to the database
import os
import mysql.connector

# Alias for mysql.connector.Error
MySQLError = mysql.connector.Error

def get_database_connection():
    database_connection = None
    try:
        database_connection = mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
            database = os.getenv("DB_DATABASE")
        )
        print("Connected to the MySQL server successfully");
    except MySQLError as err:
        print(f"Error during connecting to server: {err}")
    if database_connection is None:
        raise ValueError("Database connection failed. Please check your credentials.")
        
    return database_connection