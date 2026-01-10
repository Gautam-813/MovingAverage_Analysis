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

def plot_duration_vs_distance(df, color_by='Direction'):
    """Interactive scatter plot of Duration vs Distance."""
    
    # Define color map based on selection
    color_map = {'BULLISH': 'green', 'BEARISH': 'red'} if color_by == 'Direction' else None
    
    fig = px.scatter(
        df, x='Duration_Min', y='Distance', color=color_by,
        hover_data=['StartTime', 'EndTime', 'Session_Start'],
        color_discrete_map=color_map,
        title=f"Trend Duration vs Distance (Colored by {color_by})",
        labels={'Duration_Min': 'Duration (Minutes)', 'Distance': 'Distance (Points)'}
    )
    return fig

def plot_distance_by_session(df):
    """Box plot of Trend Distances grouped by Start Session."""
    # Ensure correct order
    session_order = ["SYDNEY", "TOKYO", "LONDON", "NEW YORK"]
    
    fig = px.box(
        df, x='Session_Start', y='Distance', color='Session_Start',
        category_orders={"Session_Start": session_order},
        title="Trend Distance Distribution by Session",
        points="all" # Show all points to see outliers
    )
    return fig
