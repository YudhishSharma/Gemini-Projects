import google.generativeai as genai
import streamlit as st
import json

from database_connection import get_database_connection
from chat_history import save_chat_history_to_file
from bill_operations import extract_bill_details, pay_bills
from transactions import extract_transaction_details, send_money
from table_formatter import format_using_llm
from cheque_book import check_cheque_book_status, order_cheque_book
import prompts

capabilites_phrases = [
    "what can you do for me", "what can you do", "what are your capabilities",
    "what are your features", "what services do you offer", "how can you help me"
]

# Function to get gemini response (English Sentence -> SQL query)
def convert_sentence_to_query_using_gemini(sentence, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
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
    
    column_names = [desc[0] for desc in cursor.description]
    
    # Commit to save the changes and then close the connection
    database_connection.commit()
    database_connection.close()
    print("Connection to the MySQL server closed")
    
    return rows, column_names

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
    
    elif user_intent == "table_format":
        
        last_result = st.session_state.get("last_result", None)
        print("last result is -------------------> ",last_result)
        last_columns = st.session_state.get("last_columns", None)
        
        if last_result and last_columns:
            formatted_table = format_using_llm(last_result, last_columns)
            response_content = formatted_table
        else:
            response_content = "No previous data available to format."
            
            
    elif user_intent == "sql":
        response_from_gemini = convert_sentence_to_query_using_gemini(query, prompt)
        response_from_gemini = response_from_gemini.replace("```", "").strip()
        
        print("Response from gemini for the sql query:", response_from_gemini)
        
        response_from_database, column_names = read_sql_query(response_from_gemini)
        
        if response_from_database:
            st.session_state["last_columns"] = column_names
            st.session_state["last_result"] = response_from_database  # Store the last database result
        
        response_content = f"Here are the results: \n{response_from_database}" if response_from_database else "No data found or an error occurred."
        
    elif user_intent == "explanation":
        last_result = st.session_state.get("last_result", "No previous data available.")
        model = genai.GenerativeModel('gemini-1.5-flash')
        explanation_prompt = f"Explain the following database result based on the user's input: {last_result}. User query: {query}"
        response = model.generate_content(explanation_prompt)
        response_content = response.text
        
    elif user_intent == "sql_and_format":
        response_from_gemini = convert_sentence_to_query_using_gemini(query, prompt)
        response_from_gemini = response_from_gemini.replace("```", "").strip()
        
        print("Response from gemini for the sql query:", response_from_gemini)
        
        response_from_database, column_names = read_sql_query(response_from_gemini)
        
        if response_from_database:
            st.session_state["last_columns"] = column_names
            st.session_state["last_result"] = response_from_database
            
            formatted_table = format_using_llm(response_from_database, column_names)
            response_content = formatted_table
        else:
            response_content = "No data found or an error occurred."
        
    elif user_intent == "send_money":
        # Pass the query to model to extract sender, receiver, and amount
        model = genai.GenerativeModel('gemini-1.5-flash')
        extraction_prompt = extract_transaction_details(query)
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
    
    elif user_intent == "order_cheque_book":
        if check_cheque_book_status():
            response_content = "You already have a cheque book."
        else:
            response_content = order_cheque_book()
    
    else:
        if any(phrase in query.lower() for phrase in capabilites_phrases):
            response_content = prompts.capabilities_response
        else:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(query)
            response_content = response.text
        
        print("Response from gemini for the queries unrelated to SQL:", response_content)
    
    st.session_state["messages"].append({"role": "assistant", "content": response_content})
    
    with st.chat_message("assistant"):
        st.write(response_content) 
    
    save_chat_history_to_file(st.session_state["messages"])
    
def classify_user_intent(query):
    """Determine if the user wants a SQL query, explanation, or general conversation."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    classification_prompt = prompts.classification_prompt

    response = model.generate_content([classification_prompt, query])
    return response.text.strip().lower()