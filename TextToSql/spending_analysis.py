from database_connection import get_database_connection
import google.generativeai as genai

SPENDING_ANALYSIS = """
        SELECT date, type_of_transaction, transaction_amount, credit_or_debit 
        FROM banking 
        WHERE credit_or_debit = 'Debit' 
        ORDER BY date DESC 
        LIMIT 30;
"""


def get_spending_analysis():
    database_connection = get_database_connection()
    cursor = database_connection.cursor()
    cursor.execute(SPENDING_ANALYSIS)
    transactions = cursor.fetchall()
    database_connection.close()

    if not transactions:
        return "No spending data available."

    transactions_text = "\n".join(
        [f"{t[0]} - {t[1]}: ₹{t[2]}" for t in transactions]
    )
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Analyze these transactions and give a brief overview of spending trends and how to control expenses:\n\n{transactions_text}"
    response = model.generate_content(prompt)
    
    return response.text