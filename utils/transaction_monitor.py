import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_transactions(df):
    """
    Analyze transactions for suspicious patterns.
    Returns a list of alerts for suspicious activities.
    """
    alerts = []
    
    # Ensure required columns exist
    required_columns = ['date', 'amount', 'type', 'sender', 'recipient']
    if not all(col in df.columns for col in required_columns):
        raise ValueError("Transaction data missing required columns")
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Check for large transactions
    large_txn_threshold = 10000  # Example threshold
    large_txns = df[df['amount'] > large_txn_threshold]
    if not large_txns.empty:
        alerts.append(f"Found {len(large_txns)} large transactions above {large_txn_threshold}")
    
    # Check for structured transactions
    structured_txns = check_structured_transactions(df)
    if structured_txns:
        alerts.extend(structured_txns)
    
    # Check for rapid succession transactions
    rapid_txns = check_rapid_transactions(df)
    if rapid_txns:
        alerts.extend(rapid_txns)
    
    # Check for unusual patterns
    unusual_patterns = check_unusual_patterns(df)
    if unusual_patterns:
        alerts.extend(unusual_patterns)
    
    return alerts

def check_structured_transactions(df):
    """Check for potential structuring behavior."""
    alerts = []
    
    # Group transactions by sender within 24-hour periods
    df['date_group'] = df['date'].dt.floor('D')
    daily_groups = df.groupby(['sender', 'date_group'])
    
    for (sender, date), group in daily_groups:
        total_amount = group['amount'].sum()
        num_txns = len(group)
        
        # Alert if multiple transactions just below threshold
        if total_amount > 9000 and num_txns > 2:
            alerts.append(
                f"Potential structuring: {sender} made {num_txns} transactions "
                f"totaling {total_amount:.2f} on {date.strftime('%Y-%m-%d')}"
            )
    
    return alerts

def check_rapid_transactions(df):
    """Check for unusually rapid succession of transactions."""
    alerts = []
    
    # Sort transactions by date
    df_sorted = df.sort_values('date')
    
    # Group by sender
    for sender in df_sorted['sender'].unique():
        sender_txns = df_sorted[df_sorted['sender'] == sender]
        
        # Check time differences between consecutive transactions
        if len(sender_txns) > 1:
            time_diffs = sender_txns['date'].diff()
            rapid_txns = time_diffs[time_diffs < timedelta(minutes=5)]
            
            if not rapid_txns.empty:
                alerts.append(
                    f"Rapid transactions detected: {sender} made {len(rapid_txns)} "
                    f"transactions within 5 minutes"
                )
    
    return alerts

def check_unusual_patterns(df):
    """Check for unusual transaction patterns."""
    alerts = []
    
    # Calculate average transaction amount per sender
    sender_avg = df.groupby('sender')['amount'].agg(['mean', 'std'])
    
    # Check for transactions significantly above average
    for sender in sender_avg.index:
        sender_txns = df[df['sender'] == sender]
        mean_amount = sender_avg.loc[sender, 'mean']
        std_amount = sender_avg.loc[sender, 'std']
        
        if std_amount > 0:
            unusual_txns = sender_txns[
                sender_txns['amount'] > (mean_amount + 2 * std_amount)
            ]
            
            if not unusual_txns.empty:
                alerts.append(
                    f"Unusual transaction amount: {sender} made {len(unusual_txns)} "
                    f"transactions significantly above their average"
                )
    
    return alerts
