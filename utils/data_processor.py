import pandas as pd
import json
from datetime import datetime

def process_excel_data(file):
    """Process uploaded Excel file and extract relevant data."""
    try:
        df = pd.read_excel(file)
        data = {
            'analyst_name': df.get('analyst_name', [''])[0],
            'position': df.get('position', [''])[0],
            'user_id': df.get('user_id', [''])[0],
            'customer_name': df.get('customer_name', [''])[0],
            'is_pep': df.get('is_pep', ['No'])[0],
            'is_sanctioned': df.get('is_sanctioned', ['No'])[0],
            'transaction_analysis': df.get('transaction_analysis', [''])[0],
            'behavioral_analysis': df.get('behavioral_analysis', [''])[0],
            'case_number': generate_case_number()
        }
        return data
    except Exception as e:
        raise Exception(f"Error processing Excel file: {str(e)}")

def process_json_data(file):
    """Process uploaded JSON file and extract relevant data."""
    try:
        data = json.load(file)
        data['case_number'] = generate_case_number()
        return data
    except Exception as e:
        raise Exception(f"Error processing JSON file: {str(e)}")

def generate_case_number():
    """Generate incremental case number based on current date."""
    today = datetime.now()
    return f"{today.strftime('%d%m')}001"
