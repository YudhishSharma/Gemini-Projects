from database_connection import get_database_connection

CHECK_CHEQUE_BOOK_STATUS = """
    SELECT issued FROM cheque_book WHERE id = 1;
"""

ISSUE_CHEQUE_BOOK = """
    UPDATE cheque_book SET issued = TRUE, issued_date = CURDATE() WHERE id = 1;
"""

def check_cheque_book_status():
    try:
        database_connection = get_database_connection()
        cursor = database_connection.cursor()
        cursor.execute(CHECK_CHEQUE_BOOK_STATUS)
        
        result = cursor.fetchone()
        print(result)
        cursor.close()
        
        if result:
            return bool(result[0])
        else:
            return False
    except Exception as e:
        print(f"Error checking cheque book status: {e}")
    
def order_cheque_book():
    try:
        database_connection = get_database_connection()
        cursor = database_connection.cursor()
        cursor.execute(ISSUE_CHEQUE_BOOK)
        database_connection.commit()
        cursor.close()
        
        return "Cheque book ordered successfully!"
    except Exception as e:
        print(f"Error ordering cheque book: {e}")
        return "Error ordering cheque book"
    