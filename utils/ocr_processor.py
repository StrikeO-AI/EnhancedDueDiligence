import cv2
import pytesseract
import numpy as np
from PIL import Image
import io

def extract_text_from_image(image_data):
    """
    Extract text from image data using OCR.
    
    Args:
        image_data: Image data (can be bytes or file-like object)
        
    Returns:
        str: Extracted text from the image
    """
    try:
        # Convert image data to numpy array
        if isinstance(image_data, bytes):
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        else:
            # For file-like objects
            image_data = Image.open(image_data)
            image = cv2.cvtColor(np.array(image_data), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to preprocess the image
        threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Perform OCR
        text = pytesseract.image_to_string(threshold)
        
        return text.strip()
        
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

def extract_text_from_pdf_image(pdf_image):
    """
    Extract text from PDF-converted image.
    
    Args:
        pdf_image: Image from PDF conversion
        
    Returns:
        str: Extracted text from the image
    """
    try:
        # Convert to grayscale
        gray = cv2.cvtColor(np.array(pdf_image), cv2.COLOR_RGB2GRAY)
        
        # Apply thresholding
        threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Perform OCR
        text = pytesseract.image_to_string(threshold)
        
        return text.strip()
        
    except Exception as e:
        raise Exception(f"Error processing PDF image: {str(e)}")
