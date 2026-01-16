import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from engines.heatmap_engine import calculate_heatmap_matrix
from plots.heatmap_plots import plot_heatmap_matrix, plot_heatmap_3d

def get_temporal_options(period_type):
    """
    Returns the list of options based on period type.
    """
    if period_type == "Month-wise":
        return ["All Months", "January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"]
    elif period_type == "Quarter-wise":
        return ["All Quarters", "Q1 (Jan-Mar)", "Q2 (Apr-Jun)", "Q3 (Jul-Sep)", "Q4 (Oct-Dec)"]
    return []

def filter_dataframe_by_period(df, period_type, selected_period):
    """
    Filters the dataframe based on the selected period.
    """
    # Fix: Impulse Data uses 'Time', Stats uses 'StartTime'
    time_col = 'Time' if 'Time' in df.columns else 'StartTime'
    if time_col not in df.columns:
        return pd.DataFrame()

    # Ensure datetime
    dt_series = pd.to_datetime(df[time_col])
    
    if period_type == "Month-wise":
        month_map = {
            "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
            "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
        }
        target_month = month_map.get(selected_period)
        if target_month:
            return df[dt_series.dt.month == target_month]

    elif period_type == "Quarter-wise":
        quarter_map = {
            "Q1 (Jan-Mar)": 1, "Q2 (Apr-Jun)": 2, "Q3 (Jul-Sep)": 3, "Q4 (Oct-Dec)": 4
        }
        target_quarter = quarter_map.get(selected_period)
        if target_quarter:
            return df[dt_series.dt.quarter == target_quarter]

    return pd.DataFrame()

def _render_period_chart(df_sub, pm_ranges, period_name, chart_style, period_type_label):
    """
    Helper to render a single heatmap chart for a specific period.
    """
    pcts, counts, atrs, total_pcts, y_labels, x_labels = calculate_heatmap_matrix(df_sub, pm_ranges, y_col='Impulse%')

    st.markdown(f"##### {period_name} ({period_type_label})")
    title_suffix = f" — {period_name}"
    
    if chart_style == "2D Grid":
        fig = plot_heatmap_matrix(pcts, counts, atrs, total_pcts, x_labels, y_labels, title_suffix=title_suffix)
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = plot_heatmap_3d(pcts, x_labels, y_labels, title_suffix=title_suffix)
        st.plotly_chart(fig, use_container_width=True)

def render_temporal_analysis_ui(df_pm, pm_ranges):
    """
    Renders the UI and Heatmaps for Temporal Analysis.
    Isolates this logic from main.py.
    """
    st.markdown("#### ⏳ Temporal Analysis (Month/Quarter)")
    
    # 1. Period Type Selector
    c1, c2, c3 = st.columns(3)
    period_type = c1.selectbox("Select Time View", ["Month-wise", "Quarter-wise"], key="temp_period_type")
    
    # 2. Specific Period Selector
    options = get_temporal_options(period_type)
    selected_period = c2.selectbox(f"Select {period_type.split('-')[0]}", options, key="temp_period_val")
    
    # 3. Chart Style
    chart_style = c3.radio("Chart Style", ["2D Grid", "3D Topography"], horizontal=True, key="temp_view_mode")
    
    st.divider()

    # Logic: Handle "All" vs Single Selection
    periods_to_render = []
    
    if selected_period.startswith("All"):
        # Render all options except the first "All" one
        periods_to_render = options[1:]
    else:
        periods_to_render = [selected_period]
        
    # Render Loop
    for p_name in periods_to_render:
        df_filtered = filter_dataframe_by_period(df_pm, period_type, p_name)
        
        if df_filtered.empty:
            if not selected_period.startswith("All"):
                st.warning(f"No data found for **{p_name}**.")
            continue
            
        _render_period_chart(df_filtered, pm_ranges, p_name, chart_style, period_type.split('-')[0])
        if selected_period.startswith("All"):
            st.divider()
