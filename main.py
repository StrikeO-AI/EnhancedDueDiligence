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
import io  # Add this import for BytesIO
from utils.data_processor import (
    process_excel_data, 
    process_json_data, 
    process_image_data,
    process_pdf_data,
    process_docx_data
)
from utils.report_generator import generate_report
from utils.templates import DEFAULT_TEMPLATE, SMR_TEMPLATE
from utils.transaction_monitor import analyze_transactions
from utils.ocr_processor import extract_text_from_image
from utils.visualization import (
    create_transaction_timeline,
    create_transaction_heatmap,
    create_amount_distribution,
    create_sender_recipient_network,
    create_anomaly_scatter
)
from utils.ai_analyzer import analyze_transaction_pattern
from utils.risk_visualization import (
    create_risk_gauge,
    create_compliance_timeline,
    create_risk_heatmap,
    calculate_risk_indicators,
    generate_compliance_metrics
)
from utils.training_module import TrainingModule

TRAINING_CATEGORIES = [
    "Transaction Monitoring",
    "Customer Due Diligence",
    "Suspicious Matter Reporting",
    "Risk Assessment",
    "Regulatory Reporting"
]


st.set_page_config(page_title="AML/CTF Case Management System", layout="wide")

def main():
    st.title("AML/CTF Case Management System")

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Select Module",
        ["ECDD Generator", "Transaction Monitoring", "Suspicious Matter Reports", "Case Management", "Training Module"]
    )

    if page == "ECDD Generator":
        display_ecdd_generator()
    elif page == "Transaction Monitoring":
        display_transaction_monitoring()
    elif page == "Suspicious Matter Reports":
        display_smr_generator()
    elif page == "Training Module":
        display_training_module()
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

            # Ensure date column is datetime
            df['date'] = pd.to_datetime(df['date'])

            # Advanced Filtering Section
            st.sidebar.header("Filters")

            # Date Range Filter
            date_range = st.sidebar.date_input(
                "Select Date Range",
                value=(df['date'].min(), df['date'].max()),
                min_value=df['date'].min().date(),
                max_value=df['date'].max().date()
            )

            # Amount Range Filter
            amount_range = st.sidebar.slider(
                "Amount Range",
                float(df['amount'].min()),
                float(df['amount'].max()),
                (float(df['amount'].min()), float(df['amount'].max()))
            )

            # Transaction Type Filter
            transaction_types = df['type'].unique().tolist()
            selected_types = st.sidebar.multiselect(
                "Transaction Types",
                transaction_types,
                default=transaction_types
            )

            # Search Box
            search_term = st.sidebar.text_input("Search (Sender/Recipient/Reference)")

            # Apply Filters
            mask = (
                (df['date'].dt.date >= date_range[0]) &
                (df['date'].dt.date <= date_range[1]) &
                (df['amount'].between(amount_range[0], amount_range[1])) &
                (df['type'].isin(selected_types))
            )

            # Apply Search
            if search_term:
                search_mask = (
                    df['sender'].str.contains(search_term, case=False, na=False) |
                    df['recipient'].str.contains(search_term, case=False, na=False) |
                    df['reference'].str.contains(search_term, case=False, na=False)
                )
                mask = mask & search_mask

            filtered_df = df[mask]

            # Display transaction summary
            st.subheader("Transaction Summary")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Transactions", len(filtered_df))
            with col2:
                st.metric("Total Amount", f"${filtered_df['amount'].sum():,.2f}")
            with col3:
                st.metric("Average Amount", f"${filtered_df['amount'].mean():,.2f}")

            # Export filtered data
            st.header("Export Options")
            col1, col2 = st.columns(2)

            with col1:
                export_format = st.selectbox(
                    "Export Format",
                    ["CSV", "JSON", "Excel"]
                )

            with col2:
                export_data = st.multiselect(
                    "Data to Include",
                    [
                        "Transaction Details",
                        "Risk Analysis",
                        "Compliance Metrics",
                        "AI Analysis",
                        "Alert Triggers"
                    ],
                    default=["Transaction Details"]
                )

            if st.button("Generate Report"):
                try:
                    # Prepare export data based on selection
                    export_dict = {}

                    if "Transaction Details" in export_data:
                        export_dict["transactions"] = filtered_df.to_dict(orient='records')

                    if "Risk Analysis" in export_data:
                        export_dict["risk_indicators"] = risk_indicators

                    if "Compliance Metrics" in export_data:
                        export_dict["compliance_metrics"] = compliance_data.to_dict(orient='records')

                    if "AI Analysis" in export_data and 'ai_analysis' in locals():
                        export_dict["ai_analysis"] = ai_analysis

                    if "Alert Triggers" in export_data and alerts:
                        export_dict["alerts"] = alerts

                    # Generate export file based on format
                    if export_format == "CSV":
                        # For CSV, we'll focus on transaction data
                        csv = filtered_df.to_csv(index=False)
                        st.download_button(
                            label="Download CSV Report",
                            data=csv,
                            file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )

                    elif export_format == "JSON":
                        # JSON can include all selected data
                        json_str = json.dumps(export_dict, indent=2, default=str)
                        st.download_button(
                            label="Download JSON Report",
                            data=json_str,
                            file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )

                    else:  # Excel
                        # Create Excel file with multiple sheets
                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                            if "Transaction Details" in export_data:
                                filtered_df.to_excel(writer, sheet_name='Transactions', index=False)

                            if "Risk Analysis" in export_data:
                                pd.DataFrame([risk_indicators]).to_excel(writer, sheet_name='Risk Analysis', index=False)

                            if "Compliance Metrics" in export_data:
                                compliance_data.to_excel(writer, sheet_name='Compliance Metrics', index=False)

                            if "AI Analysis" in export_data and 'ai_analysis' in locals():
                                pd.DataFrame([ai_analysis]).to_excel(writer, sheet_name='AI Analysis', index=False)

                            if "Alert Triggers" in export_data and alerts:
                                pd.DataFrame({'alerts': alerts}).to_excel(writer, sheet_name='Alerts', index=False)

                        excel_data = excel_buffer.getvalue()
                        st.download_button(
                            label="Download Excel Report",
                            data=excel_data,
                            file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                    st.success("Report generated successfully!")

                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")

            # Interactive visualizations with filtered data
            st.subheader("Transaction Analysis Dashboard")

            # Timeline visualization
            st.plotly_chart(create_transaction_timeline(filtered_df), use_container_width=True)

            # Transaction patterns
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(create_amount_distribution(filtered_df), use_container_width=True)
            with col2:
                st.plotly_chart(create_transaction_heatmap(filtered_df), use_container_width=True)

            # Network analysis
            st.subheader("Transaction Network Analysis")
            st.plotly_chart(create_sender_recipient_network(filtered_df), use_container_width=True)

            # Anomaly detection
            st.subheader("Anomaly Detection")
            st.plotly_chart(create_anomaly_scatter(filtered_df), use_container_width=True)

            # AI Analysis Section
            st.subheader("AI-Powered Analysis")
            if st.button("Generate AI Analysis"):
                with st.spinner("Analyzing transaction patterns using AUSTRAC and FATF typologies..."):
                    ai_analysis = analyze_transaction_pattern(filtered_df)

                    # Display analysis results
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        risk_color = {
                            "high": "🔴",
                            "medium": "🟡",
                            "low": "🟢",
                            "unknown": "⚪"
                        }
                        st.markdown(f"### Risk Level: {risk_color.get(ai_analysis['risk_level'].lower(), '⚪')} {ai_analysis['risk_level'].upper()}")

                    with col2:
                        if ai_analysis['matched_typologies']:
                            st.markdown("### Matched AUSTRAC Typologies")
                            for typology in ai_analysis['matched_typologies']:
                                st.markdown(f"- {typology}")

                    if ai_analysis['suspicious_patterns']:
                        st.markdown("### Identified Patterns")
                        for pattern in ai_analysis['suspicious_patterns']:
                            st.markdown(f"- {pattern}")

                    st.markdown("### Alert Triggers")
                    if ai_analysis['alert_triggers']:
                        for trigger in ai_analysis['alert_triggers']:
                            st.warning(trigger)
                    else:
                        st.success("No immediate alert triggers identified")

                    st.markdown("### Detailed Analysis")
                    st.write(ai_analysis['explanation'])

                    st.markdown("### Recommendations")
                    for rec in ai_analysis['recommendations']:
                        st.markdown(f"- {rec}")

                    # Option to include AI analysis in SMR
                    if st.button("Include in SMR"):
                        if 'smr_data' not in st.session_state:
                            st.session_state['smr_data'] = {}
                        st.session_state['smr_data']['ai_analysis'] = ai_analysis
                        st.success("AI analysis added to SMR data")

            # Detailed transaction view
            st.subheader("Transaction Details")
            st.dataframe(
                filtered_df.style.highlight_max(axis=0, subset=['amount']),
                use_container_width=True
            )

            # Analyze transactions for suspicious patterns
            alerts = analyze_transactions(filtered_df)

            # Display alerts
            if alerts:
                st.subheader("Transaction Alerts")
                for alert in alerts:
                    st.warning(alert)

                # Option to generate SMR
                if st.button("Generate Suspicious Matter Report"):
                    st.session_state['generate_smr'] = True
                    st.session_state['smr_data'] = alerts
                    st.experimental_rerun()
            else:
                st.success("No suspicious transactions detected")

            # Real-time Compliance Dashboard
            st.header("Real-time Compliance Dashboard")

            # Calculate risk indicators
            risk_indicators = calculate_risk_indicators(filtered_df)

            # Display risk gauges in columns
            st.subheader("Risk Indicators")
            cols = st.columns(4)

            # Volume Risk Gauge
            with cols[0]:
                volume_gauge = create_risk_gauge(
                    risk_indicators['volume_risk'],
                    "Volume Risk"
                )
                st.plotly_chart(volume_gauge, use_container_width=True)

            # Frequency Risk Gauge
            with cols[1]:
                freq_gauge = create_risk_gauge(
                    risk_indicators['frequency_risk'],
                    "Frequency Risk"
                )
                st.plotly_chart(freq_gauge, use_container_width=True)

            # Concentration Risk Gauge
            with cols[2]:
                conc_gauge = create_risk_gauge(
                    risk_indicators['concentration_risk'],
                    "Concentration Risk"
                )
                st.plotly_chart(conc_gauge, use_container_width=True)

            # Structuring Risk Gauge
            with cols[3]:
                struct_gauge = create_risk_gauge(
                    risk_indicators['structuring_risk'],
                    "Structuring Risk"
                )
                st.plotly_chart(struct_gauge, use_container_width=True)

            # Risk Heatmap
            st.subheader("Risk Factor Analysis")
            risk_heatmap = create_risk_heatmap(risk_indicators)
            st.plotly_chart(risk_heatmap, use_container_width=True)

            # Compliance Timeline
            st.subheader("Compliance Metrics Timeline")
            compliance_data = generate_compliance_metrics(filtered_df)
            compliance_timeline = create_compliance_timeline(compliance_data)
            st.plotly_chart(compliance_timeline, use_container_width=True)


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
        if 'ai_analysis' in st.session_state['smr_data']:
            smr_data['ai_analysis'] = st.session_state['smr_data']['ai_analysis']

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


def display_training_module():
    st.header("Interactive Compliance Training")

    # Initialize training module in session state
    if 'training_module' not in st.session_state:
        st.session_state['training_module'] = TrainingModule()

    # Display progress if training has started
    if st.session_state['training_module'].scenarios_completed > 0:
        progress = st.session_state['training_module'].get_progress()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Scenarios Completed", progress['completed'])
        with col2:
            st.metric("Correct Answers", progress['score'])
        with col3:
            st.metric("Success Rate", f"{progress['percentage']:.1f}%")

    # Category selection
    category = st.selectbox("Select Training Category", 
                          ["Random"] + TRAINING_CATEGORIES)

    # Generate new scenario
    if st.button("Generate New Scenario"):
        with st.spinner("Generating scenario..."):
            scenario = st.session_state['training_module'].generate_scenario(
                category if category != "Random" else None
            )
            if 'error' in scenario:
                st.error(scenario['error'])
            else:
                st.session_state['current_scenario'] = scenario

    # Display current scenario
    if 'current_scenario' in st.session_state:
        scenario = st.session_state['current_scenario']

        # Scenario details
        st.subheader("Scenario")
        st.write(scenario['scenario'])

        # Red flags
        st.subheader("Red Flags to Consider")
        for flag in scenario['red_flags']:
            st.markdown(f"- {flag}")

        # Question and options
        st.subheader("What action should be taken?")
        user_answer = st.radio(
            scenario['question'],
            options=scenario['options'],
            key="scenario_response"
        )

        # Submit and evaluate
        if st.button("Submit Answer"):
            answer_index = scenario['options'].index(user_answer)
            result = st.session_state['training_module'].evaluate_response(answer_index)

            if result['correct']:
                st.success("✅ Correct!")
            else:
                st.error("❌ Incorrect")

            st.write("Explanation:", result['explanation'])

            # Show performance analysis after multiple scenarios
            if st.session_state['training_module'].scenarios_completed >= 3:
                st.subheader("Performance Analysis")
                analysis = st.session_state['training_module'].analyze_performance()

                if 'error' not in analysis:
                    st.write(f"Performance Level: {analysis['performance_level']}")
                    st.write("Analysis:", analysis['analysis'])

                    st.subheader("Recommendations")
                    for rec in analysis['recommendations']:
                        st.markdown(f"- {rec}")

                    st.subheader("Focus Areas")
                    for area in analysis['focus_areas']:
                        st.markdown(f"- {area}")



if __name__ == "__main__":
    main()