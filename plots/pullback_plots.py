import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def plot_reversal_distribution(df):
    """Plots a Bi-Directional (Mirror) histogram of reversal percentages."""
    if df.empty:
        return go.Figure()

    # 1. Define 5% Bins
    max_val = max(df['Reversal%'].max(), 5.0)
    max_bin = (np.ceil(max_val / 5) * 5) + 5
    bins = np.arange(0, max_bin + 5, 5)
    labels = [f"{int(bins[i])}-{int(bins[i+1])}%" for i in range(len(bins)-1)]

    # 2. Calculate Counts manually for Mirror effect
    bull_df = df[df['Direction'] == 'BULLISH']
    bear_df = df[df['Direction'] == 'BEARISH']

    bull_counts = pd.cut(bull_df['Reversal%'], bins=bins, labels=labels, right=False).value_counts().reindex(labels).fillna(0)
    bear_counts = pd.cut(bear_df['Reversal%'], bins=bins, labels=labels, right=False).value_counts().reindex(labels).fillna(0)

    # 3. Create Bi-Directional Bar Chart
    fig = go.Figure()

    # Bullish (Upwards)
    fig.add_trace(go.Bar(
        x=labels,
        y=bull_counts,
        name='BULLISH',
        marker_color='green',
        opacity=0.7,
        hovertemplate='Range: %{x}<br>Count: %{y}'
    ))

    # Bearish (Downwards)
    fig.add_trace(go.Bar(
        x=labels,
        y=-bear_counts, # Inverse Y for Mirror effect
        name='BEARISH',
        marker_color='red',
        opacity=0.7,
        customdata=bear_counts, # Store actual count for hover
        hovertemplate='Range: %{x}<br>Count: %{customdata}'
    ))

    # 4. Styling
    fig.update_layout(
        title="Bi-Directional Reversal (%) Distribution (5% Increments)",
        xaxis_title="Reversal % Range",
        yaxis_title="Frequency (Count)",
        barmode='relative',
        bargap=0.1,
        hovermode="x unified",
        template="plotly_dark"
    )

    # Add Zero Line
    fig.add_hline(y=0, line_color="white", line_width=1)

    return fig

def plot_impulse_vs_pullback(df):
    """Interactive scatter plot with regression line for Impulse vs Pullback."""
    fig = px.scatter(
        df, x='Impulse', y='Pullback', color='Direction',
        trendline="ols",
        title="Scaling Law: Impulse vs Pullback (Points)",
        color_discrete_map={'BULLISH': 'green', 'BEARISH': 'red'},
        template="plotly_dark"
    )
    return fig
