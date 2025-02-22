import json
import google.generativeai as genai
from datetime import date
from decimal import Decimal

def format_using_llm(data, column_names):
    """Use Gemini to format SQL results as a structured table."""
    model = genai.GenerativeModel('gemini-pro')
    
    formatted_data = serialize_mysql_data(data)
    
    table_format_prompt = f"""
    Convert the following SQL result into a formatted table.

    Column Names: {column_names}
    Data:
    {json.dumps(formatted_data, indent=2)}

    Present the data in a structured table format.
    """

    response = model.generate_content(table_format_prompt)
    return response.text

def serialize_mysql_data(data):
    def serialize_value(value):
        if isinstance(value, date):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, Decimal):
            return float(value)
        return value
    return [[serialize_value(value) for value in row] for row in data]