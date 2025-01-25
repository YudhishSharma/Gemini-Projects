from dotenv import load_dotenv

import mysql.connector
import google.generativeai as genai
import streamlit as st
import os
import json

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


# Function to load chat history from file
def load_chat_history_from_file():
    if os.path.exists("chat_history.json"):
        try:
            with open("chat_history.json", "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            # If the file is empty or corrupt, start with an empty history
            print("Error: The chat history file is empty or corrupt. Starting with an empty history.")
            return []
    else:
        # If the file doesn't exist, start with an empty history
        return []


# Funtion to save history to file
def save_chat_history_to_file(messages):
    with open("chat_history.json", "w") as file:
        json.dump(messages, file)


#  Define your prompt
prompt = [
    """
    You are an expert in converting English sentences to MySQL queries! 
    The SQL database has the name 'employeeDb' with a table 'banking' which has the following columns - (id, name, date, transaction_amount, type_of_transaction, balance).
    
    For each SQL query you generate:
    - Make sure all non-aggregated columns in the SELECT statement are either aggregated (using functions like COUNT, SUM, AVG, etc.) or included in the GROUP BY clause.
    - If the user requests a group operation (e.g., grouping by transaction type), ensure that all selected columns are either aggregated or functionally dependent on the GROUP BY clause.
    
    Example 1 - List of transactions with type_of_transaction as 'grocery'? 
    The SQL command will be: 
    SELECT transaction_amount FROM banking WHERE type_of_transaction='grocery';

    Example 2 - Total transactions by type_of_transaction and count?
    The SQL command will be:
    SELECT SUM(transaction_amount) AS total_transaction_amount, type_of_transaction, COUNT(*) AS ccount
    FROM banking 
    GROUP BY type_of_transaction;

    Ensure that the generated SQL query is functional, efficient, and free from any SQL errors related to aggregation.
    Ensure you use the chat history and provide accurate sql query and only one query should be given, result should
    contain  proper SQL syntax, it should not have any English  sentence and stick to the syntax
    also the sql code should not have ``` in beginning or end and sql word in output.
    """
]


# Streamlit part
st.set_page_config(page_title = "Text To SQL")
st.header("Gemini Query Retreiver")

# Default Message
DEFAULT_ASSISTANT_MESSAGE = "Hi buddy!! 😊 How can I help you with your account?"

# Store conversation history
if "messages" not in st.session_state:
    st.session_state["messages"] = load_chat_history_from_file() or [{"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}]

# New Chat button to start new conversation
if st.button("New Chat"):
    st.session_state["messages"] = [{"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}]
    save_chat_history_to_file([])
    st.success("Chat reset successfully. Start a new conversation.")
    
# Display previous chat messages
for messagge in st.session_state["messages"]:
    with st.chat_message(messagge["role"]):
        st.write(messagge["content"])
        
# Get user input
if user_input := st.chat_input("Enter you query"):
    # Add user message to chat history
    st.session_state["messages"].append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
        
    # Get the SQL query from gemini
    response_from_gemini = convert_sentence_to_query_using_gemini(user_input, prompt)
    print(response_from_gemini)
    # Pass that qquery to the database
    response_from_database = read_sql_query(response_from_gemini)
    # If we get a response then displaay
    if response_from_database:
        response_content = f"Here are the  results: \n{response_from_database}"
    else:
        response_content = "No data found or an error occured"
    
    # Add gemini message to chat history
    st.session_state["messages"].append({"role": "assistant", "content":response_content})
    
    # Display gemini response
    with st.chat_message("assistant"):
        st.write(response_content) 
    
    save_chat_history_to_file(st.session_state["messages"])
    