import pandas as pd
import json
from datetime import datetime
import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
import io
from PIL import Image
import docx

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

def process_image_data(file):
    """Process uploaded image file using OCR and extract relevant data."""
    try:
        # Read image file
        image = Image.open(file)

        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Preprocess image
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # Perform OCR
        text = pytesseract.image_to_string(thresh)

        # Extract relevant information using pattern matching
        data = extract_data_from_text(text)
        data['case_number'] = generate_case_number()

        return data
    except Exception as e:
        raise Exception(f"Error processing image file: {str(e)}")

def process_pdf_data(file):
    """Process uploaded PDF file and extract relevant data."""
    try:
        # Convert PDF to images
        images = convert_from_path(file)

        # Extract text from all pages
        text = ""
        for image in images:
            # Convert PIL image to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # Preprocess image
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            # Perform OCR
            text += pytesseract.image_to_string(thresh) + "\n"

        # Extract relevant information
        data = extract_data_from_text(text)
        data['case_number'] = generate_case_number()

        return data
    except Exception as e:
        raise Exception(f"Error processing PDF file: {str(e)}")

def process_docx_data(file):
    """Process uploaded DOCX file and extract relevant data."""
    try:
        doc = docx.Document(file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

        # Extract relevant information
        data = extract_data_from_text(text)
        data['case_number'] = generate_case_number()

        return data
    except Exception as e:
        raise Exception(f"Error processing DOCX file: {str(e)}")

def extract_data_from_text(text):
    """Extract relevant information from OCR text using pattern matching."""
    data = {
        'analyst_name': '',
        'position': '',
        'user_id': '',
        'customer_name': '',
        'is_pep': 'No',
        'is_sanctioned': 'No',
        'transaction_analysis': '',
        'behavioral_analysis': ''
    }

    # Add pattern matching logic here based on document structure
    # This is a simplified example - you would need more sophisticated
    # text processing based on your document formats

    lines = text.split('\n')
    for line in lines:
        if 'analyst name' in line.lower():
            data['analyst_name'] = line.split(':')[-1].strip()
        elif 'position' in line.lower():
            data['position'] = line.split(':')[-1].strip()
        elif 'user id' in line.lower():
            data['user_id'] = line.split(':')[-1].strip()
        elif 'customer name' in line.lower():
            data['customer_name'] = line.split(':')[-1].strip()

    return data

def generate_case_number():
    """Generate incremental case number based on current date."""
    today = datetime.now()
    return f"{today.strftime('%d%m')}001"