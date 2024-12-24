import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

def create_transaction_timeline(df):
    """Create an interactive timeline of transactions."""
    fig = px.scatter(
        df,
        x='date',
        y='amount',
        color='type',
        size='amount',
        hover_data=['sender', 'recipient'],
        title='Transaction Timeline'
    )
    return fig

def create_transaction_heatmap(df):
    """Create a heatmap of transaction frequency by hour and day."""
    df['hour'] = pd.to_datetime(df['date']).dt.hour
    df['day'] = pd.to_datetime(df['date']).dt.day_name()
    
    pivot_table = df.pivot_table(
        values='amount',
        index='day',
        columns='hour',
        aggfunc='count',
        fill_value=0
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=pivot_table.columns,
        y=pivot_table.index,
        colorscale='Viridis'
    ))
    
    fig.update_layout(
        title='Transaction Frequency Heatmap',
        xaxis_title='Hour of Day',
        yaxis_title='Day of Week'
    )
    return fig

def create_amount_distribution(df):
    """Create a histogram of transaction amounts."""
    fig = px.histogram(
        df,
        x='amount',
        nbins=50,
        title='Distribution of Transaction Amounts'
    )
    return fig

def create_sender_recipient_network(df):
    """Create a network visualization of transactions between senders and recipients."""
    # Aggregate transaction amounts between parties
    edges = df.groupby(['sender', 'recipient'])['amount'].sum().reset_index()
    
    # Create network graph
    fig = go.Figure(data=[
        go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=list(set(edges['sender'].unique()) | set(edges['recipient'].unique())),
            ),
            link=dict(
                source=[list(set(edges['sender'].unique()) | set(edges['recipient'].unique())).index(s) for s in edges['sender']],
                target=[list(set(edges['sender'].unique()) | set(edges['recipient'].unique())).index(t) for t in edges['recipient']],
                value=edges['amount']
            )
        )
    ])
    
    fig.update_layout(title_text="Transaction Flow Network")
    return fig

def create_anomaly_scatter(df):
    """Create a scatter plot highlighting potential anomalies."""
    # Calculate z-scores for amounts
    df['amount_zscore'] = (df['amount'] - df['amount'].mean()) / df['amount'].std()
    
    fig = px.scatter(
        df,
        x='date',
        y='amount',
        color='amount_zscore',
        size='amount',
        hover_data=['sender', 'recipient'],
        title='Transaction Anomalies',
        color_continuous_scale='RdYlBu'
    )
    return fig
