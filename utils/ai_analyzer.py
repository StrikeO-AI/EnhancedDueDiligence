import os
from openai import OpenAI
import json
from datetime import datetime
import pandas as pd

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# AUSTRAC typology indicators
AUSTRAC_INDICATORS = [
    "transactions inconsistent with customer profile",
    "associations with multiple accounts under multiple names",
    "cash deposited domestically with funds withdrawn from ATMs offshore",
    "elaborate movement of funds through different accounts",
    "frequent early repayments of loans",
    "high volume of transactions within a short period",
    "structuring cash deposits/withdrawals",
    "use of third parties to undertake wire transfers",
    "unexplained income inconsistent with economic situation",
    "multiple individuals sending funds to one beneficiary",
    "use of intermediaries",
    "rapid movement of funds",
    "'u-turn' transactions",
    "use of multiple jurisdictions",
    "unusual patterns of transactions",
    "transactions just below reporting thresholds",
]

def analyze_transaction_pattern(transaction_data: pd.DataFrame):
    """
    Analyze transaction patterns using OpenAI to provide detailed explanations
    of potential anomalies and suspicious patterns.
    """
    try:
        # Format transaction data for analysis
        transaction_context = format_transaction_data(transaction_data)

        # Create prompt for GPT analysis
        prompt = f"""As an AML/CTF expert, analyze the following financial transaction data for potential money laundering 
        or suspicious patterns. Consider these specific AUSTRAC typology indicators:

        {json.dumps(AUSTRAC_INDICATORS, indent=2)}

        Look for patterns such as:
        - Structuring (transactions just below reporting thresholds)
        - Rapid movement of funds
        - Multiple accounts/parties involvement
        - Unusual transaction patterns
        - Geographic risk factors
        - Inconsistency with customer profile

        Transaction Data:
        {transaction_context}

        Provide a detailed analysis focusing on:
        1. Match with known AUSTRAC typologies
        2. Risk assessment
        3. Suspicious patterns identified
        4. Recommendations for investigation

        Respond in JSON format with:
        {{
            "risk_level": "high/medium/low",
            "matched_typologies": ["list of matched AUSTRAC typologies"],
            "suspicious_patterns": ["list of identified patterns"],
            "explanation": "detailed analysis explanation",
            "recommendations": ["list of recommended actions"],
            "alert_triggers": ["specific transaction patterns that triggered alerts"]
        }}
        """

        # Call OpenAI API for analysis
        response = client.chat.completions.create(
            model="gpt-4",  # Using GPT-4 for better pattern recognition
            messages=[
                {"role": "system", "content": "You are an AML/CTF analysis expert with deep knowledge of AUSTRAC and FATF typologies."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        # Parse and return the analysis
        return json.loads(response.choices[0].message.content)

    except Exception as e:
        return {
            "risk_level": "unknown",
            "matched_typologies": [],
            "suspicious_patterns": [],
            "explanation": f"Error during analysis: {str(e)}",
            "recommendations": ["Manual review required due to analysis error"],
            "alert_triggers": []
        }

def format_transaction_data(transaction_data: pd.DataFrame):
    """Format transaction data into a comprehensive string for analysis."""
    summary = []

    # Basic statistics
    summary.append(f"Total Transactions: {len(transaction_data)}")
    summary.append(f"Total Amount: ${transaction_data['amount'].sum():,.2f}")
    summary.append(f"Average Amount: ${transaction_data['amount'].mean():,.2f}")

    # Time-based analysis
    summary.append("\nTime Analysis:")
    time_diffs = transaction_data['date'].diff().dropna()
    if not time_diffs.empty:
        rapid_txns = time_diffs[time_diffs.dt.total_seconds() < 300].count()
        summary.append(f"Rapid Transactions (< 5 min apart): {rapid_txns}")

    # Transaction patterns
    summary.append("\nTransaction Patterns:")

    # Analyze by sender
    for sender in transaction_data['sender'].unique():
        sender_txns = transaction_data[transaction_data['sender'] == sender]
        summary.append(f"\nSender: {sender}")
        summary.append(f"Number of transactions: {len(sender_txns)}")
        summary.append(f"Total amount: ${sender_txns['amount'].sum():,.2f}")
        summary.append(f"Average amount: ${sender_txns['amount'].mean():,.2f}")

        # Check for potential structuring
        potential_struct = sender_txns[
            (sender_txns['amount'] >= 9000) & 
            (sender_txns['amount'] <= 10000)
        ].count()
        if potential_struct > 0:
            summary.append(f"Potential structuring transactions: {potential_struct}")

    # Analyze by recipient
    summary.append("\nRecipient Analysis:")
    recipient_counts = transaction_data['recipient'].value_counts()
    multiple_recipients = recipient_counts[recipient_counts > 1]
    if not multiple_recipients.empty:
        summary.append("Recipients receiving multiple transactions:")
        for recipient, count in multiple_recipients.items():
            recipient_total = transaction_data[
                transaction_data['recipient'] == recipient
            ]['amount'].sum()
            summary.append(
                f"- {recipient}: {count} transactions, "
                f"total ${recipient_total:,.2f}"
            )

    return "\n".join(summary)