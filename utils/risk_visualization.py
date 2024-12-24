import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_risk_gauge(risk_score, title="Overall Risk Score"):
    """Create an animated gauge chart for risk visualization."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(height=250)
    return fig

def create_compliance_timeline(compliance_data):
    """Create an animated timeline of compliance metrics."""
    fig = go.Figure()
    
    # Add traces for different compliance metrics
    for metric in compliance_data.columns:
        if metric != 'date':
            fig.add_trace(go.Scatter(
                x=compliance_data['date'],
                y=compliance_data[metric],
                name=metric,
                mode='lines+markers'
            ))
    
    fig.update_layout(
        title="Compliance Metrics Timeline",
        xaxis_title="Date",
        yaxis_title="Compliance Score",
        hovermode='x unified'
    )
    return fig

def create_risk_heatmap(risk_factors):
    """Create a heatmap of risk factors."""
    fig = go.Figure(data=go.Heatmap(
        z=[[risk_factors[factor]] for factor in risk_factors],
        y=list(risk_factors.keys()),
        x=['Risk Level'],
        colorscale=[
            [0, 'green'],
            [0.5, 'yellow'],
            [1, 'red']
        ],
        showscale=True
    ))
    
    fig.update_layout(
        title="Risk Factors Heatmap",
        height=400,
        yaxis={'tickangle': 0}
    )
    return fig

def calculate_risk_indicators(transaction_data: pd.DataFrame):
    """Calculate various risk indicators from transaction data."""
    risk_indicators = {}
    
    # Volume-based risk
    daily_volume = transaction_data.groupby(
        transaction_data['date'].dt.date)['amount'].sum()
    volume_volatility = daily_volume.std() / daily_volume.mean() * 100
    risk_indicators['volume_risk'] = min(100, volume_volatility)
    
    # Frequency-based risk
    hourly_freq = transaction_data.groupby(
        transaction_data['date'].dt.hour)['amount'].count()
    freq_volatility = hourly_freq.std() / hourly_freq.mean() * 100
    risk_indicators['frequency_risk'] = min(100, freq_volatility)
    
    # Concentration risk
    recipient_concentration = (
        transaction_data.groupby('recipient')['amount'].sum().max() /
        transaction_data['amount'].sum() * 100
    )
    risk_indicators['concentration_risk'] = recipient_concentration
    
    # Structuring risk
    struct_threshold = 10000
    potential_structuring = len(
        transaction_data[
            (transaction_data['amount'] >= struct_threshold * 0.9) &
            (transaction_data['amount'] <= struct_threshold)
        ]
    )
    risk_indicators['structuring_risk'] = min(
        100,
        (potential_structuring / len(transaction_data)) * 100
    )
    
    return risk_indicators

def generate_compliance_metrics(transaction_data: pd.DataFrame):
    """Generate compliance metrics for the timeline."""
    dates = pd.date_range(
        start=transaction_data['date'].min(),
        end=transaction_data['date'].max(),
        freq='D'
    )
    
    compliance_data = pd.DataFrame(index=dates)
    compliance_data['date'] = dates
    
    # KYC compliance score
    compliance_data['kyc_score'] = np.random.normal(85, 5, len(dates))
    compliance_data['kyc_score'] = compliance_data['kyc_score'].clip(0, 100)
    
    # Transaction monitoring score
    compliance_data['monitoring_score'] = np.random.normal(90, 3, len(dates))
    compliance_data['monitoring_score'] = compliance_data['monitoring_score'].clip(0, 100)
    
    # Reporting compliance
    compliance_data['reporting_score'] = np.random.normal(95, 2, len(dates))
    compliance_data['reporting_score'] = compliance_data['reporting_score'].clip(0, 100)
    
    return compliance_data
