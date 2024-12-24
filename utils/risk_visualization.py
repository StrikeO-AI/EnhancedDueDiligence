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
        },
        hovertemplate=(
            "<b>Risk Score</b>: %{value:.1f}<br>" +
            "<b>Status</b>: %{customdata}<br>" +
            "<b>Threshold</b>: 90<br>" +
            "<extra></extra>"  # This removes the secondary box
        ),
        customdata=[
            "High Risk" if risk_score >= 70
            else "Medium Risk" if risk_score >= 30
            else "Low Risk"
        ]
    ))

    fig.update_layout(
        height=250,
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    return fig

def create_compliance_timeline(compliance_data):
    """Create an animated timeline of compliance metrics."""
    fig = go.Figure()

    # Add traces for different compliance metrics
    metrics_info = {
        'kyc_score': {
            'name': 'KYC Compliance',
            'description': 'Know Your Customer compliance score'
        },
        'monitoring_score': {
            'name': 'Transaction Monitoring',
            'description': 'Real-time transaction monitoring effectiveness'
        },
        'reporting_score': {
            'name': 'Regulatory Reporting',
            'description': 'Timely and accurate regulatory reporting compliance'
        }
    }

    for metric, info in metrics_info.items():
        if metric in compliance_data.columns and metric != 'date':
            fig.add_trace(go.Scatter(
                x=compliance_data['date'],
                y=compliance_data[metric],
                name=info['name'],
                mode='lines+markers',
                hovertemplate=(
                    f"<b>{info['name']}</b><br>" +
                    "Date: %{x|%Y-%m-%d}<br>" +
                    "Score: %{y:.1f}<br>" +
                    f"<i>{info['description']}</i><br>" +
                    "<extra></extra>"
                )
            ))

    fig.update_layout(
        title="Compliance Metrics Timeline",
        xaxis_title="Date",
        yaxis_title="Compliance Score",
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    return fig

def create_risk_heatmap(risk_factors):
    """Create a heatmap of risk factors."""
    risk_descriptions = {
        'volume_risk': 'Risk based on transaction volume patterns',
        'frequency_risk': 'Risk based on transaction frequency',
        'concentration_risk': 'Risk based on concentration of transactions',
        'structuring_risk': 'Risk of potential structuring activity'
    }

    fig = go.Figure(data=go.Heatmap(
        z=[[risk_factors[factor]] for factor in risk_factors],
        y=list(risk_factors.keys()),
        x=['Risk Level'],
        colorscale=[
            [0, 'green'],
            [0.5, 'yellow'],
            [1, 'red']
        ],
        showscale=True,
        hovertemplate=(
            "<b>Risk Factor</b>: %{y}<br>" +
            "<b>Score</b>: %{z:.1f}<br>" +
            "<b>Description</b>: %{customdata}<br>" +
            "<extra></extra>"
        ),
        customdata=[[risk_descriptions.get(factor, 'Risk factor')] for factor in risk_factors]
    ))

    fig.update_layout(
        title="Risk Factors Heatmap",
        height=400,
        yaxis={'tickangle': 0},
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
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