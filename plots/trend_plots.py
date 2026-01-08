import plotly.express as px
import plotly.graph_objects as go

def plot_distance_distribution(df):
    """Plots the distribution of trend distances using Plotly."""
    fig = px.histogram(
        df, x='Distance', color='Direction', 
        nbins=50, marginal="box", 
        color_discrete_map={'BULLISH': 'green', 'BEARISH': 'red'},
        title="Trend Distance Distribution (Points)",
        opacity=0.7
    )
    fig.update_layout(bargap=0.1)
    return fig

def plot_duration_vs_distance(df):
    """Interactive scatter plot of Duration vs Distance."""
    fig = px.scatter(
        df, x='Duration_Min', y='Distance', color='Direction',
        hover_data=['StartTime', 'EndTime'],
        color_discrete_map={'BULLISH': 'green', 'BEARISH': 'red'},
        title="Trend Duration vs Distance",
        labels={'Duration_Min': 'Duration (Minutes)', 'Distance': 'Distance (Points)'}
    )
    return fig
