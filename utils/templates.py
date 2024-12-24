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
N/A
6. Transaction Analysis
Transaction Analysis:
{transaction_analysis}

7. Behavioral Analysis
{behavioral_analysis}
___________________________________
8. Recommendation
Based on our analysis, recommending to continue monitoring as a high-risk customer (HRC) and conduct periodic reviews.
"""
