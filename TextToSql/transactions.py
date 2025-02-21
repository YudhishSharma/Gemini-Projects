from database_connection import get_database_connection
from mysql.connector import Error as MySQLError

def extract_transaction_details(query):
    money_extraction_prompt = f"""
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
    return money_extraction_prompt

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