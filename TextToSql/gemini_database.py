from re import sub
from dotenv import load_dotenv

import mysql.connector
import google.generativeai as genai
import streamlit as st
import os

# Load environment variable from .env file
load_dotenv()

# Configure GenAI key
genai.configure(api_key = os.getenv("GEMINI_API_KEY"))

# Alias for mysql.connector.Error
MySQLError = mysql.connector.Error

# Function to connect to the database
def get_databaase_connection():
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
        
    return database_connection

# Function to get gemini response (English Sentence -> SQL query)
def convert_sentence_to_query_using_gemini(sentence, prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt[0], sentence])
    return response.text

# Funtion to retrieve query from the database
def read_sql_query(query):
    database_connection = get_databaase_connection()
    
    # Cursor to perform actions in the database
    cursor = database_connection.cursor()
    cursor.execute(query)
    
    # Rows affected by cursor
    rows = cursor.fetchall()
    
    # Commit to save the changes and then close the connection
    database_connection.commit()
    database_connection.close()
    print("Connection to the MySQL server closed")
    
    # Verify the data by iterating over the rows affected
    for row in rows:
        print(row)
    
    return rows


#  Define your prompt
prompt=[
    """
    You are an expert in converting English sentences to MySQL query!
    The SQL database has the name employeeDb with a table employeeTable which has the following columns - employeeId, employeeName, 
    designation, salary,
    \n\nFor example,\nExample 1 - How many entries of records are present?, 
    the SQL command will be something like this SELECT COUNT(*) FROM employeeTable ;
    \nExample 2 - Tell me all the employees whose designation is Associate Engineer?, 
    the SQL command will be something like this SELECT * FROM employeeTable 
    where designation="Data Science"; 
    Also make use of aggregate functions used in MySql to improve efficiency,
    also the sql code should not have ``` in beginning or end and sql word in output
    
    """
]

# Streamlit part
st.set_page_config(page_title = "Text To SQL")
st.header("Gemini Query Retreiver")

query = st.text_input("Input: ", key = "input")
submit = st.button("Convert")

# If submit is clicked
if submit:
    # Get the SQL query from gemini
    response_from_gemini = convert_sentence_to_query_using_gemini(query, prompt)
    print(response_from_gemini)
    # Pass that qquery to the database
    response_from_database = read_sql_query(response_from_gemini)
    # If we get a response then displaay
    if response_from_database:
        st.subheader("The Response is")
        for row in response_from_database:
            st.write(row)
    else:
        st.write("No data found")
    
    