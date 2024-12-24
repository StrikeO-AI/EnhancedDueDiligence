DEFAULT_TEMPLATE = """1. Analysis and Review

1.(i) Analysed By:
(a) Name:     {analyst_name}________________________
(b) Position: {position}________________________
(c) Date:        {date}________________________
(d) Case Number:        {case_number}________________________

2. Customer Profile
Inherent Customer risk rating :
2.1.   User_id:            {user_id}__________________________
2.2. Full Name: {customer_name}_____________
2.3 Profile Summary
{profile_summary}
___________________________________

3. Customer is PEP (Y/N) 
{is_pep}___________________________________
4. Sanctioned Customer (Y/N) 
{is_sanctioned}
5. Related Party: 
{related_party}
6. Transaction Analysis
Transaction Analysis:
{transaction_analysis}

Additional Information:
{additional_info}

7. Behavioral Analysis
{behavioral_analysis}
___________________________________
8. Recommendation
{recommendation}
"""

SMR_TEMPLATE = """SUSPICIOUS MATTER REPORT

1. Reporting Entity Information
Entity Name: {reporting_entity}
Report Date: {report_date}
Reference Number: {reference_number}
Priority: {priority}

2. Suspect Details
{suspect_details}

3. Suspicious Activity Description
{suspicious_activity}

4. Transaction Details
{transaction_details}

5. Supporting Documentation
{supporting_docs}

6. Risk Assessment
Risk Level: {risk_level}
Rationale: {risk_rationale}

7. Action Taken
{action_taken}

8. Recommendations
{recommendations}

Report Generated: {generated_date}
Report Status: {status}
"""