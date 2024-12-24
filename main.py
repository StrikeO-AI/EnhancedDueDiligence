import streamlit as st
import pandas as pd
import json
from datetime import datetime
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
import tempfile
import os
from utils.data_processor import (
    process_excel_data, 
    process_json_data, 
    process_image_data,
    process_pdf_data,
    process_docx_data # Added to handle docx files
)
from utils.report_generator import generate_report
from utils.templates import DEFAULT_TEMPLATE, SMR_TEMPLATE
from utils.transaction_monitor import analyze_transactions
from utils.ocr_processor import extract_text_from_image

st.set_page_config(page_title="AML/CTF Case Management System", layout="wide")

def main():
    st.title("AML/CTF Case Management System")

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Select Module",
        ["ECDD Generator", "Transaction Monitoring", "Suspicious Matter Reports", "Case Management"]
    )

    if page == "ECDD Generator":
        display_ecdd_generator()
    elif page == "Transaction Monitoring":
        display_transaction_monitoring()
    elif page == "Suspicious Matter Reports":
        display_smr_generator()
    else:
        display_case_management()

def display_ecdd_generator():
    st.header("Enhanced Customer Due Diligence (ECDD) Report Generator")

    # File upload section with multiple file types
    st.subheader("Upload Customer Data")
    file = st.file_uploader(
        "Choose a file",
        type=['xlsx', 'json', 'pdf', 'png', 'jpg', 'jpeg', 'docx']
    )

    if file is not None:
        try:
            # Process file based on type
            if file.name.endswith('.xlsx'):
                data = process_excel_data(file)
            elif file.name.endswith('.json'):
                data = process_json_data(file)
            elif file.name.endswith('.pdf'):
                data = process_pdf_data(file)
            elif file.name.endswith(('.png', '.jpg', '.jpeg')):
                data = process_image_data(file)
            else:  # docx
                data = process_docx_data(file)

            # Display form for additional inputs
            st.header("Report Details")
            col1, col2 = st.columns(2)

            with col1:
                analyst_name = st.text_input("Analyst Name", value=data.get('analyst_name', ''))
                position = st.text_input("Position", value=data.get('position', ''))

            with col2:
                date = st.date_input("Date", value=datetime.now())
                case_number = f"EC{date.strftime('%y%m')}{data.get('case_number', '001').zfill(3)}"
                st.text_input("Case Number", value=case_number, disabled=True)

            # Customer details section
            st.header("Customer Details")
            user_id = st.text_input("User ID", value=data.get('user_id', ''))
            customer_name = st.text_input("Customer Name", value=data.get('customer_name', ''))

            # Risk Assessment
            st.subheader("Risk Assessment")
            col3, col4 = st.columns(2)
            with col3:
                is_pep = st.selectbox("Is PEP?", ["No", "Yes"], 
                                    index=0 if data.get('is_pep', 'No') == 'No' else 1)
            with col4:
                is_sanctioned = st.selectbox("Is Sanctioned?", ["No", "Yes"],
                                           index=0 if data.get('is_sanctioned', 'No') == 'No' else 1)

            # Transaction Analysis
            st.header("Transaction Analysis")
            transaction_analysis = st.text_area("Transaction Analysis", 
                                              value=data.get('transaction_analysis', ''),
                                              height=200)

            # Additional Information
            st.header("Additional Information")
            additional_info = st.text_area("Additional Information",
                                         value=data.get('additional_info', ''),
                                         height=150)

            # Behavioral Analysis
            st.header("Behavioral Analysis")
            behavioral_analysis = st.text_area("Behavioral Analysis",
                                             value=data.get('behavioral_analysis', ''),
                                             height=150)

            # Generate Report
            if st.button("Generate Report"):
                report_data = {
                    'analyst_name': analyst_name,
                    'position': position,
                    'date': date.strftime('%d/%m/%Y'),
                    'case_number': case_number,
                    'user_id': user_id,
                    'customer_name': customer_name,
                    'is_pep': is_pep,
                    'is_sanctioned': is_sanctioned,
                    'transaction_analysis': transaction_analysis,
                    'additional_info': additional_info,
                    'behavioral_analysis': behavioral_analysis,
                }

                report = generate_report(report_data, DEFAULT_TEMPLATE)

                # Display preview
                st.header("Report Preview")
                st.text_area("Preview", value=report, height=400)

                # Download button
                st.download_button(
                    label="Download Report",
                    data=report,
                    file_name=f"ECDD_Report_{case_number}.txt",
                    mime="text/plain"
                )

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

def display_transaction_monitoring():
    st.header("Transaction Monitoring")

    # Upload transaction data
    file = st.file_uploader("Upload Transaction Data", type=['csv', 'xlsx'])

    if file is not None:
        try:
            df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)

            # Display transaction summary
            st.subheader("Transaction Summary")
            st.dataframe(df.head())

            # Analyze transactions
            alerts = analyze_transactions(df)

            # Display alerts
            if alerts:
                st.subheader("Transaction Alerts")
                for alert in alerts:
                    st.warning(alert)

                # Option to generate SMR
                if st.button("Generate Suspicious Matter Report"):
                    # Redirect to SMR generator with pre-filled data
                    st.session_state['generate_smr'] = True
                    st.session_state['smr_data'] = alerts
                    st.experimental_rerun()
            else:
                st.success("No suspicious transactions detected")

        except Exception as e:
            st.error(f"Error analyzing transactions: {str(e)}")

def display_smr_generator():
    st.header("Suspicious Matter Report Generator")

    # Check if we're coming from transaction monitoring
    if 'generate_smr' in st.session_state and st.session_state['generate_smr']:
        alerts = st.session_state['smr_data']
        st.text_area("Transaction Alerts", value="\n".join(alerts))
        st.session_state['generate_smr'] = False

    # SMR form
    col1, col2 = st.columns(2)
    with col1:
        reporting_entity = st.text_input("Reporting Entity")
        report_date = st.date_input("Report Date")
    with col2:
        reference_number = st.text_input("Reference Number")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])

    suspect_details = st.text_area("Suspect Details")
    suspicious_activity = st.text_area("Suspicious Activity Description")
    supporting_documents = st.file_uploader("Supporting Documents", 
                                          type=['pdf', 'png', 'jpg', 'jpeg'],
                                          accept_multiple_files=True)

    if st.button("Generate SMR"):
        smr_data = {
            'reporting_entity': reporting_entity,
            'report_date': report_date.strftime('%d/%m/%Y'),
            'reference_number': reference_number,
            'priority': priority,
            'suspect_details': suspect_details,
            'suspicious_activity': suspicious_activity
        }

        report = generate_report(smr_data, SMR_TEMPLATE)

        st.text_area("SMR Preview", value=report, height=400)
        st.download_button(
            label="Download SMR",
            data=report,
            file_name=f"SMR_{reference_number}.txt",
            mime="text/plain"
        )

def display_case_management():
    st.header("Case Management")

    # Case filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status = st.selectbox("Status", ["All", "Open", "In Progress", "Closed"])
    with col2:
        priority = st.selectbox("Priority", ["All", "High", "Medium", "Low"])
    with col3:
        case_type = st.selectbox("Type", ["All", "ECDD", "SMR", "Investigation"])

    # Mock case data - In real implementation, this would come from a database
    cases = [
        {"id": "CASE001", "type": "ECDD", "status": "Open", "priority": "High", 
         "customer": "John Doe", "date": "2024-03-24"},
        {"id": "CASE002", "type": "SMR", "status": "In Progress", "priority": "Medium",
         "customer": "Jane Smith", "date": "2024-03-23"}
    ]

    # Display cases in a table
    st.dataframe(pd.DataFrame(cases))

if __name__ == "__main__":
    main()