import streamlit as st
import pandas as pd
import json
from datetime import datetime
from utils.data_processor import process_excel_data, process_json_data
from utils.report_generator import generate_report
from utils.templates import DEFAULT_TEMPLATE

st.set_page_config(page_title="ECDD Report Generator", layout="wide")

def main():
    st.title("Enhanced Customer Due Diligence (ECDD) Report Generator")
    
    # File upload section
    st.header("Upload Customer Data")
    file = st.file_uploader("Choose a file", type=['xlsx', 'json'])
    
    if file is not None:
        try:
            # Process file based on type
            if file.name.endswith('.xlsx'):
                data = process_excel_data(file)
            else:
                data = process_json_data(file)
                
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
            
            # PEP and Sanctions
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

if __name__ == "__main__":
    main()
