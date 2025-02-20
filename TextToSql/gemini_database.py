from pyexpat import model
import time
from turtle import mode
from urllib import response
from dotenv import load_dotenv

import mysql.connector
import google.generativeai as genai
import streamlit as st
import speech_recognition as sr
import os
import json

# Load environment variable from .env file
load_dotenv()

# Configure GenAI key
genai.configure(api_key = os.getenv("GEMINI_API_KEY"))

# Alias for mysql.connector.Error
MySQLError = mysql.connector.Error

# Default Message
DEFAULT_ASSISTANT_MESSAGE = "Hi buddy!! 😊 How can I help you with your account?"

# Function to connect to the database
def get_database_connection():
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

# Function to retrieve query from the database
def read_sql_query(query):
    database_connection = get_database_connection()
    
    # Cursor to perform actions in the database
    cursor = database_connection.cursor()
    cursor.execute(query)
    
    # Rows affected by cursor
    rows = cursor.fetchall()
    
    # Commit to save the changes and then close the connection
    database_connection.commit()
    database_connection.close()
    print("Connection to the MySQL server closed")
    
    return rows

# Function to load chat history from file
def load_chat_history_from_file():
    if os.path.exists("chat_history.json"):
        try:
            with open("chat_history.json", "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Error: The chat history file is empty or corrupt. Starting with an empty history.")
            return []
    else:
        return []

# Function to save history to file
def save_chat_history_to_file(messages):
    with open("chat_history.json", "w") as file:
        json.dump(messages, file)
        
def get_speech_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Speak Now !!")
        try:
            audio = recognizer.listen(source, timeout = 7, phrase_time_limit = 10)
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            st.warning("Sorry, I could not understand what you said!")
        except sr.RequestError as e:
            st.error(f"Sorry, an error occurred while processing your request!:  {e}")

#  Define your prompt
prompt = [
    """
    You are an expert in converting English sentences to MySQL queries! 
    The SQL database has the name 'employeeDb' with two tables:
    
    1. **banking** (Transactions Table)  
       - Columns: (id, name, date, transaction_amount, type_of_transaction, balance)  
       - Stores transaction records like deposits, withdrawals, and payments.  

    2. **bills** (Bills Table)  
       - Columns: (id, type, amount, due_date, status, payment_date)  
       - Stores bill payment records, such as phone bills, electricity bills, etc.  
       - The `status` column can have values: 'unpaid', 'paid'.  
       - The `type` column indicates the type of bill (e.g., 'phone', 'electricity', 'water').  
    
    **Relationships:**  
    - The `bills` table is linked to `banking` because when a bill is paid, a new transaction is logged in the `banking` table.
    
    For each SQL query you generate:
    - Make sure all non-aggregated columns in the SELECT statement are either aggregated (using functions like COUNT, SUM, AVG, etc.) or included in the GROUP BY clause.
    - If the user requests a group operation (e.g., grouping by transaction type), ensure that all selected columns are either aggregated or functionally dependent on the GROUP BY clause.
    
    **Examples:**  
    - **Show me all unpaid bills:**  
      SELECT * FROM bills WHERE status = 'unpaid';
      
    - **Pay my phone bill:**  
      1. Check the phone bill amount:
         SELECT amount FROM bills WHERE type = 'phone' AND status = 'unpaid';
         
      2. If sufficient balance, pay the bill:
         UPDATE banking SET balance = balance - (SELECT amount FROM bills WHERE type = 'phone' AND status = 'unpaid');
         
      3. Update the bill status:
         UPDATE bills SET status = 'paid' WHERE type = 'phone' AND status = 'unpaid';
      
      4. Update the date of the payment:
         UPDATE bills SET payment_date = CURDATE() where type = 'phone';
         
      5. Insert a transaction record in `banking`:  
         INSERT INTO banking (name, date, transaction_amount, type_of_transaction, balance)
         VALUES ('Yudhish', CURDATE(), (SELECT amount FROM bills WHERE type = 'phone' AND status = 'paid'), 'Bill Payment - Phone', (SELECT balance FROM banking WHERE name = 'Yudhish'));
         
    
    - **List of transactions with type_of_transaction as 'grocery'** 
        SELECT transaction_amount FROM banking WHERE type_of_transaction='grocery';

    - **Total transactions by type_of_transaction and count**
        SELECT SUM(transaction_amount) AS total_transaction_amount, type_of_transaction, COUNT(*) AS ccount
        FROM banking 
        GROUP BY type_of_transaction;
    
    - **What is my current balance?**
        SELECT balance FROM banking ORDER BY id DESC LIMIT 1;
    
    - **Show me all the transactions**
        SELECT * FROM banking;

    Ensure that the generated SQL query is functional, efficient, and free from any SQL errors related to aggregation.
    Ensure you use the chat history and provide accurate sql query and only one query should be given and very important point to note
    the result should contain  proper SQL syntax with no comments or any English sentence added to it and the last output sql code should not have 
    ``` in beginning or end and should not have sql word in output. To be more specific the output should be only SQL code without sql word in it.
    """
]

# Streamlit part
st.set_page_config(page_title = "Text To SQL")
st.header("Gemini Query Retriever")

# Store conversation history
if "messages" not in st.session_state:
    st.session_state["messages"] = load_chat_history_from_file() or [{"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}]

# New Chat button to start new conversation
if st.button("New Chat"):
    st.session_state["messages"] = [{"role": "assistant", "content": DEFAULT_ASSISTANT_MESSAGE}]
    save_chat_history_to_file([])
    st.success("Chat reset successfully. Start a new conversation.")
    
# Display previous chat messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
def classify_user_intent(query):
    """Determine if the user wants a SQL query, explanation, or general conversation."""
    model = genai.GenerativeModel('gemini-pro')
    classification_prompt = """
    Classify the following user input into one of five categories:
    1. 'sql' if the user wants database information (e.g., retrieving transactions, balance, banking details, bills).
    2. 'explanation' if the user is asking what the retrieved data means.
    3. 'conversation' if the user is engaging in a general discussion.
    4. 'send_money' if the user wants to send money to another user.
    5. 'pay_bills' if the user wants to pay bills.

    Respond with only one word: 'sql', 'explanation', 'conversation', 'send_money' or 'pay_bills'.

    Examples:

    - "What is my account balance?" → sql
    - "Show me all the bills" → sql
    - "Retrieve my transaction history" → sql
    - "Thank you" → conversation
    - "Can you explain what this transaction means?" → explanation
    - "Hey, how are you?" → conversation
    - "Pay my electricity bill" → pay_bills
    - "Send $100 to John" → send_money
    - "Transfer 500 to Alice" → send_money
    - "Hi" → conversation
    """

    response = model.generate_content([classification_prompt, query])
    return response.text.strip().lower()

def text_to_sql_using_gemini(query, prompt):
    
    user_intent = classify_user_intent(query)
    print("User intent is -------------------> ",user_intent)
    if user_intent == "pay_bills":
        # Extract bill type
        bill_type, error = extract_bill_details(query)
        print("the bill type and the error --------------- ",bill_type, error)
        
        if error:
            response_content = f"Could not process bill payment: {error}"
        else:
            response_content = pay_bills(bill_type)
    elif user_intent == "sql":
        response_from_gemini = convert_sentence_to_query_using_gemini(query, prompt)
        response_from_gemini = response_from_gemini.replace("```", "").strip()
        
        print("Response from gemini for the sql query:", response_from_gemini)
        
        response_from_database = read_sql_query(response_from_gemini)
        st.session_state["last_result"] = response_from_database  # Store the last database result
        
        response_content = f"Here are the results: \n{response_from_database}" if response_from_database else "No data found or an error occurred."
        
    elif user_intent == "explanation":
        last_result = st.session_state.get("last_result", "No previous data available.")
        model = genai.GenerativeModel('gemini-pro')
        explanation_prompt = f"Explain the following database result based on the user's input: {last_result}. User query: {query}"
        response = model.generate_content(explanation_prompt)
        response_content = response.text
    elif user_intent == "send_money":
        # Pass the query to model to extract sender, receiver, and amount
        model = genai.GenerativeModel('gemini-pro')
        extraction_prompt = f"""
        Extract the receiver and amount from the following query: {query}

        Respond with a JSON object in the following format:

        {{
          "receiver": "the receiver's name or ID",
          "amount": "the amount to send (as a number, without currency symbols or commas)",
          "error": "a string describing any errors encountered, or null if no errors"
        }}

        Examples:

        Input: "Send $100 to John Smith"
        Output:
        {{
          "receiver": "John Smith",
          "amount": 100,
          "error": null
        }}

        Input: "Transfer one hundred dollars to john.davis"
        Output:
        {{
          "receiver": "john.davis",
          "amount": 100,
          "error": null
        }}

        Input: "Send money to John"  (Amount missing)
        Output:
        {{
          "receiver": null,
          "amount": null,
          "error": "Amount not specified"
        }}

        Input: "Send 100 to John, please."
        Output:
        {{
          "receiver": "John",
          "amount": 100,
          "error": null
        }}
        ```
        NOTE - The response should be a JSON object with the receiver's name or ID, the amount to send, and an error message if applicable, it
        should not contain any comments or additional text, should not contain the word 'JSON', and should not be enclosed in triple backticks i.e it 
        should not start and end with ```.
        """
        extraction_response = model.generate_content(extraction_prompt)
        extraction_response_text = extraction_response.text.replace("```", "").strip()
        print(extraction_response_text)
        try:
            extraction_response_json = json.loads(extraction_response_text)
            receiver = extraction_response_json.get("receiver")
            amount = extraction_response_json.get("amount")
            error = extraction_response_json.get("error")
            
            print(receiver, amount, error)
            
            if error:
                response_content = f"Transaction failed! {error}"
            elif receiver or amount is not None:
                response_content = send_money("Yudhish", receiver, amount)
            else:
                response_content = "Transaction failed! An error occurred while sending money."
        except json.JSONDecodeError:
            response_content = "Transaction failed! An error occurred while sending money."
        except ValueError:
            response_content = "Invalid Amount. Amount should be a number."
    
    else:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(query)
        response_content = response.text
        
        print("Response from gemini for the queries unrelated to SQL:", response_content)
    
    st.session_state["messages"].append({"role": "assistant", "content": response_content})
    
    with st.chat_message("assistant"):
        st.write(response_content) 
    
    save_chat_history_to_file(st.session_state["messages"])


def extract_bill_details(query):
    """Extract bill type from user input."""
    model = genai.GenerativeModel('gemini-pro')
    extraction_prompt = f"""
    Extract the bill type from the following query: {query}
    
    Respond with a JSON object:
    {{
      "bill_type": "type of bill (phone, electricity, water, etc.)",
      "error": "null if no errors, otherwise describe the error"
    }}

    Examples:

    Input: "Pay my phone bill"
    Output:
    {{
      "bill_type": "phone",
      "error": null
    }}

    Input: "Settle my electricity bill"
    Output:
    {{
      "bill_type": "electricity",
      "error": null
    }}

    Input: "I want to make a payment" (No specific bill mentioned)
    Output:
    {{
      "bill_type": null,
      "error": "Bill type not specified"
    }}
    """
    response = model.generate_content(extraction_prompt)
    response_text = response.text.replace("```", "").strip()

    try:
        response_json = json.loads(response_text)
        return response_json.get("bill_type"), response_json.get("error")
    except json.JSONDecodeError:
        return None, "Error extracting bill details."


# Funtion to pay bills
def pay_bills(bill_type):
    database_connection = get_database_connection()
    cursor = database_connection.cursor(buffered = True)
    
    try:
        cursor.execute(f"SELECT amount, due_date, payment_date, status from bills WHERE type = '{bill_type}'")
        bill_result = cursor.fetchone()
        
        if not bill_result:
            return f"Yayyyy!!! No bills found for {bill_type} 😁"
        print("Bill result ---------------> " ,bill_result)
        bill_amount, due_date, payment_date, status = bill_result
        
        if status == "paid":
            return f"The {bill_type} bill has already been paid on {payment_date}"
        
        cursor.execute("SELECT balance FROM banking ORDER BY id DESC LIMIT 1")
        balance_result = cursor.fetchone()
        
        if not balance_result:
            return f"Transaction failed! User account not found"
        
        balance = balance_result[0]
        if(balance < bill_amount):
            return f"Insufficient balance! Your current balance is {balance}, but the {bill_type} bill is {bill_amount}"
        print("balance -----------> ",balance)
        cursor.execute(f"UPDATE bills SET status = 'paid', payment_date = CURDATE() WHERE type = '{bill_type}' ")
        
        cursor.execute(f"""
                       INSERT INTO banking (name, date, transaction_amount, type_of_transaction, credit_or_debit, balance)
                        VALUES
                        ('{bill_type}', CURDATE(), {bill_amount}, '{bill_type}', 'Debit', {balance - bill_amount})
                       """)
        database_connection.commit()
        cursor.close()
        database_connection.close()
        return f"Successfully paid {bill_amount} for {bill_type}. Your new balance is {balance - bill_amount}"

    except MySQLError as err:
        print(f"Error during paying bills: {err}")
        database_connection.rollback()
        return f"Transaction failed! An error occurred while paying bills: {err}"  
    except Exception as e: 
        print(f"A general error occurred: {e}")
        database_connection.rollback()
        return f"Transaction failed! An error occurred: {e}"
    
# Function to send money
def send_money(sender, receiver, amount):
    database_connection = get_database_connection()
    cursor = database_connection.cursor(buffered = True)

    try:
        # Check if the sender has enough balance
        cursor.execute(f"SELECT balance FROM banking") 
        sender_balance_result = cursor.fetchone()
        if sender_balance_result is None:
            return f"Transaction failed! Sender '{sender}' not found." 
        sender_balance = sender_balance_result[-1]
        print(sender_balance)
        if sender_balance < amount:
            return f"Transaction failed! {sender} does not have enough balance to send {amount}."


        # Update the balance of the sender
        cursor = database_connection.cursor() 
        cursor.execute(f"UPDATE banking SET balance = balance - {amount}") 
        database_connection.commit() 

        # Insert the record of the transaction
        cursor = database_connection.cursor() 
        cursor.execute(f"INSERT INTO banking (name, date, transaction_amount, type_of_transaction, credit_or_debit, balance) VALUES ('{receiver}', CURDATE(), {amount}, 'Personal', 'Debit', {sender_balance - amount})")
        database_connection.commit() 
        cursor.close()

        database_connection.close() 
        print("Connection to the MySQL server closed")

    except MySQLError as err:
        print(f"Error during sending money: {err}")
        database_connection.rollback()
        return f"Transaction failed! An error occurred while sending money: {err}"  
    except Exception as e: 
        print(f"A general error occurred: {e}")
        database_connection.rollback()
        return f"Transaction failed! An error occurred: {e}"

    return f"Transaction successful! {amount} has been sent from {sender} to {receiver}."
        
if user_input := st.chat_input("Enter your query"):
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    text_to_sql_using_gemini(user_input, prompt)

if st.button("🎙 Speak"):
    speech_input = get_speech_input()
    if(speech_input):
        st.session_state["messages"].append({"role": "user", "content": speech_input})
        with st.chat_message("user"):
            st.write(speech_input)
        text_to_sql_using_gemini(speech_input, prompt)   
