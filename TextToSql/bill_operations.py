import json
import google.generativeai as genai

from mysql.connector import Error as MySQLError
from database_connection import get_database_connection

def extract_bill_details(query):
    """Extract bill type from user input."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    extraction_prompt = money_extraction_prompt(query)
    response = model.generate_content(extraction_prompt)
    response_text = response.text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:].strip() 
    if response_text.endswith("```"):
        response_text = response_text[:-3].strip()

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
    
def money_extraction_prompt(query):
    bill_extraction_prompt = f"""
    Extract the bill type from the following query: {query}
    
    Respond with a JSON object:
    {{
      "bill_type": "type of bill (phone, electricity, water, etc.)",
      "error": "null if no errors, otherwise describe the error"
    }}

    Examples:

    Input: "Pay my phone bill/bills"
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
    return bill_extraction_prompt