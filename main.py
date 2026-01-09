import streamlit as st
import pandas as pd
from config import APP_TITLE, APP_SUBTITLE
from data.validation import load_and_validate_stats, load_and_validate_impulse

# --- Page Config ---
st.set_page_config(page_title=APP_TITLE, layout="wide")

# --- Header ---
st.title(f"🎯 {APP_TITLE}")
st.markdown(f"**{APP_SUBTITLE}**")
st.divider()

# --- Sidebar: Interface Layer ---
st.sidebar.header("📂 Data Ingest")
uploaded_stats = st.sidebar.file_uploader("Upload Crossover_Stats.csv", type=['csv'])
uploaded_impulse = st.sidebar.file_uploader("Upload Impulse_Reversal.csv", type=['csv'])

st.sidebar.divider()
st.sidebar.header("🔍 Analysis Selection")
analysis_type = st.sidebar.selectbox(
    "What market question do you want answered?",
    [
        "Select an option...",
        "1. Crossover Trend Intelligence",
        "2. Impulse & Reversal Behavior",
        "3. Combined Market Structure (Fusion)"
    ]
)

# --- App Content ---
if analysis_type == "Select an option...":
    st.info("👋 Welcome! Please upload your MT5 CSV files in the sidebar and choose an analysis type.")
    st.image("https://images.unsplash.com/photo-1620321023374-d1a63fbc7178?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80", caption="Interactive Quant Dashboard")

else:
    try:
        from engines.trend_engine import run_trend_analysis
        from engines.impulse_engine import run_impulse_analysis
        from engines.fusion_engine import run_fusion_analysis
        from plots.trend_plots import plot_distance_distribution, plot_duration_vs_distance
        from plots.pullback_plots import plot_reversal_distribution, plot_impulse_vs_pullback
        from engines.heatmap_engine import calculate_heatmap_matrix
        from plots.heatmap_plots import plot_heatmap_matrix

        def parse_multi_range(range_str):
            """Parses strings like '5-10, 20-30' into a list of tuples [(5, 10), (20, 30)]"""
            if not range_str or range_str.strip() == "":
                return []
            ranges = []
            try:
                parts = [p.strip() for p in range_str.split(',')]
                for p in parts:
                    if '-' in p:
                        start, end = map(float, p.split('-'))
                        ranges.append((start, end))
                    else:
                        val = float(p)
                        ranges.append((val, val))
            except:
                st.sidebar.error(f"Invalid range format: {range_str}")
            return ranges

        def apply_multi_range_filter(df, column, ranges):
            """Filters dataframe where column value matches ANY of the provided ranges"""
            if not ranges:
                return df
            mask = pd.Series(False, index=df.index)
            for start, end in ranges:
                mask |= (df[column] >= start) & (df[column] <= end)
            return df[mask]

        # --- Sidebar UI ---
        st.sidebar.title("📊 Market Engine Filters")
        st.sidebar.info("Upload your CSV files here to begin analysis.")
        
        # 4. Day of Week Filter Global
        # Removed global sidebar filters to move them to tabs as requested
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        selected_days = st.sidebar.multiselect("Days to Include", days, default=days)

        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        # Selection Logic
        if analysis_type.startswith("1."):
            if not uploaded_stats:
                st.warning("⚠️ Please upload `Crossover_Stats.csv` in the sidebar to run Trend Intelligence.")
            else:
                st.subheader("🔵 Crossover Trend Intelligence")
                df_raw = load_and_validate_stats(uploaded_stats)
                
                # --- Contextual Filters ---
                with st.expander("🛠️ Advanced Filters & Controls", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    selected_days_local = c1.multiselect("Filter by Day of Week", options=days_order, default=days_order)
                    date_range = c2.date_input("Select Analysis Period (Trend)", [])
                    min_dist = c3.number_input("Min Distance Filter", value=0.0, step=10.0)
                    
                    c4, c5 = st.columns(2)
                    imp_input = c4.text_input("⚡ Impulse/Distance Bands (e.g. 10-20, 50-100)", key="trend_imp")
                    imp_ranges = parse_multi_range(imp_input)
                    # Reversal bands not relevant for trend tab usually, but consistent UI is good. 
                    # Keeping it simple for trend: Impulse(Distance) bands only.
                
                # --- Filtering Logic ---
                df_filtered = df_raw[df_raw['DayOfWeek'].isin(selected_days_local)].copy()
                
                # Date Range Filter
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    df_filtered['StartTime'] = pd.to_datetime(df_filtered['StartTime']) # Ensure datetime type
                    df_filtered = df_filtered[
                        (df_filtered['StartTime'].dt.date >= start_date) & 
                        (df_filtered['StartTime'].dt.date <= end_date)
                    ]
                
                # Impulse Range (Distance) Filter (using imp_ranges from sidebar)
                df_filtered = apply_multi_range_filter(df_filtered, 'Distance', imp_ranges)
                
                # Apply min_dist filter
                df_filtered = df_filtered[df_filtered['Distance'] >= min_dist].copy()

                if df_filtered.empty:
                    st.warning("No data matches the selected filters.")
                    st.stop()
                
                st.info(f"Filtering: Keeping {len(df_filtered)} of {len(df_raw)} records")
                
                # --- Metadata Info ---
                meta = df_raw.iloc[0]
                scan_end = df_raw.iloc[-1]['ScanEnd']
                st.success(f"📊 **Context:** {meta['Symbol']} | {meta['TF']} | {meta['MAType']} Period: {meta['MAPeriod']}")
                st.caption(f"📅 **Session Span:** {pd.to_datetime(meta['ScanStart']).strftime('%Y.%m.%d %H:%M')} — {pd.to_datetime(scan_end).strftime('%Y.%m.%d %H:%M')}")
                
                results, df = run_trend_analysis(df_filtered)
                
                # --- Metrics ---
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Avg Distance", f"{results['global_stats']['Mean']:.2f}")
                col2.metric("Median Distance", f"{results['global_stats']['Median']:.2f}")
                col3.metric("Avg Duration (Min)", f"{results['avg_duration']:.1f}")
                col4.metric("Bullish/Bearish Ratio", f"{len(df[df['Direction']=='BULLISH'])/max(1, len(df[df['Direction']=='BEARISH'])):.2f}")
                
                # --- Plotly Charts ---
                st.plotly_chart(plot_distance_distribution(df))
                st.plotly_chart(plot_duration_vs_distance(df))
                
                with st.expander("View Raw Intelligence Table"):
                    st.dataframe(df)

        elif analysis_type.startswith("2."):
            if not uploaded_impulse:
                st.warning("⚠️ Please upload `Impulse_Reversal.csv` in the sidebar to run Behavioral Analysis.")
            else:
                st.subheader("🔴 Impulse & Reversal Behavior")
                df_raw = load_and_validate_impulse(uploaded_impulse)
                
                # --- Contextual Filters ---
                with st.expander("🛠️ Advanced Filters & Controls", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    selected_days = c1.multiselect("Filter by Day of Week", options=days_order, default=days_order, key="imp_days")
                    date_range = c2.date_input("Select Analysis Period (Impulse)", [], key="imp_date")
                    min_impulse_local = c3.slider("Min Impulse Slider", 0.0, 200.0, 5.0, 1.0)
                    
                    c4, c5 = st.columns(2)
                    imp_input = c4.text_input("⚡ Impulse Bands (e.g. 10-20, 50-100)", key="imp_imp")
                    imp_ranges = parse_multi_range(imp_input)
                    
                    rev_input = c5.text_input("🔄 Reversal % Bands (e.g. 30-50, 80-100)", key="imp_rev")
                    rev_ranges = parse_multi_range(rev_input)
                
                # --- Filtering Logic ---
                df_filtered = df_raw[df_raw['DayOfWeek'].isin(selected_days)].copy()
                
                # Date Range Filter
                if len(date_range) == 2:
                    start_date, end_date = date_range
                    df_filtered['Time'] = pd.to_datetime(df_filtered['Time'])
                    df_filtered = df_filtered[
                        (df_filtered['Time'].dt.date >= start_date) & 
                        (df_filtered['Time'].dt.date <= end_date)
                    ]
                
                # Impulse Range (Impulse column) Filter
                df_filtered = apply_multi_range_filter(df_filtered, 'Impulse', imp_ranges)
                
                # Reversal % Range Filter
                df_filtered = apply_multi_range_filter(df_filtered, 'Reversal%', rev_ranges)
                
                # Apply min_impulse_local filter (if not already covered by imp_ranges)
                # This ensures the slider filter is still respected.
                if min_impulse_local > 0:
                    df_filtered = df_filtered[df_filtered['Impulse'] >= min_impulse_local].copy()

                if df_filtered.empty:
                    st.warning("No data matches the selected filters.")
                    st.stop()
                
                st.info(f"Filtering: Keeping {len(df_filtered)} of {len(df_raw)} logs")
                
                # --- Metadata Info ---
                meta = df_raw.iloc[0]
                scan_end = df_raw.iloc[-1]['ScanEnd']
                st.success(f"📊 **Context:** {meta['Symbol']} | {meta['TF']} | {meta['MAType']} Period: {meta['MAPeriod']}")
                st.caption(f"📅 **Session Span:** {pd.to_datetime(meta['ScanStart']).strftime('%Y.%m.%d %H:%M')} — {pd.to_datetime(scan_end).strftime('%Y.%m.%d %H:%M')}")
                
                results, df = run_impulse_analysis(df_filtered)
                
                # --- Metrics ---
                col1, col2, col3 = st.columns(3)
                col1.metric("Median Reversal %", f"{results['pullback_stats']['Median']:.2f}%")
                col2.metric("90th Percentile Pullback", f"{results['pullback_quantiles'][0.9]:.2f}%")
                col3.metric("Impulse/Pullback Corr", f"{results['impulse_pullback_corr']:.2f}")
                
                # --- Plotly Charts ---
                st.plotly_chart(plot_reversal_distribution(df))
                st.plotly_chart(plot_impulse_vs_pullback(df))
                
                with st.expander("View Raw Behavioral Table"):
                    st.dataframe(df)
                    
                st.info(f"💡 **Actionable Logic:** 90% of healthy trends retrace less than **{results['pullback_quantiles'][0.9]:.2f}%**. Exits before this are statistically premature.")

                st.divider()
                st.subheader("🔥 Zone Heatmap Analysis")
                
                # Heatmap Direction Filter
                hm_dir = st.radio("Filter Trend Direction", ["ALL", "BULLISH", "BEARISH"], horizontal=True, key="hm_dir")
                
                # Filter Data for Heatmap
                df_hm = df_filtered.copy()
                if hm_dir != "ALL":
                    df_hm = df_hm[df_hm['Direction'] == hm_dir]

                # Heatmap Logic
                heatmap_input = st.text_input("Define Impulse Ranges for Heatmap (e.g. 10-20, 21-30...)", value="10-20, 21-30, 31-40, 41-50, 51-60, 61-70, 71-80, 81-90, 91-100, 100-150, 151-200")
                heatmap_ranges = parse_multi_range(heatmap_input)
                
                if heatmap_ranges:
                   # Calculate Matrix
                   matrix_pcts, matrix_counts, y_labels, x_labels = calculate_heatmap_matrix(df_hm, heatmap_ranges)
                   
                   # Plot (Normalized)
                   fig_hm = plot_heatmap_matrix(matrix_pcts, matrix_counts, x_labels, y_labels)
                   st.plotly_chart(fig_hm, use_container_width=True)
                else:
                   st.caption("Enter ranges above to generate the heatmap matrix.")


        elif analysis_type.startswith("3."):
            if not uploaded_stats or not uploaded_impulse:
                st.warning("⚠️ Fusion Analysis requires BOTH CSV files to be uploaded.")
            else:
                st.subheader("🟣 Combined Market Structure (Fusion)")
                stats_raw = load_and_validate_stats(uploaded_stats)
                impulse_raw = load_and_validate_impulse(uploaded_impulse)
                
                # --- Contextual Filters ---
                with st.expander("🛠️ Advanced Filters & Controls", expanded=True):
                    c1, c2, c3 = st.columns(3)
                    selected_days = c1.multiselect("Filter by Day of Week", options=days_order, default=days_order, key="fusion_days")
                    date_range = c2.date_input("Select Analysis Period (Fusion)", [], key="fusion_date")
                    min_impulse_fusion = c3.slider("Min Impulse Slider", 0.0, 200.0, 5.0, 1.0)
                    
                    c4, c5 = st.columns(2)
                    imp_input = c4.text_input("⚡ Impulse Bands (e.g. 10-20, 50-100)", key="fusion_imp")
                    imp_ranges = parse_multi_range(imp_input)
                    
                    rev_input = c5.text_input("🔄 Reversal % Bands (e.g. 30-50, 80-100)", key="fusion_rev")
                    rev_ranges = parse_multi_range(rev_input)
                
                # --- Filtering Logic for both Dataframes ---
                # 1. Stats DF
                df_stats_filtered = stats_raw[stats_raw['DayOfWeek'].isin(selected_days)].copy()
                if len(date_range) == 2:
                    s, e = date_range
                    df_stats_filtered['StartTime'] = pd.to_datetime(df_stats_filtered['StartTime'])
                    df_stats_filtered = df_stats_filtered[
                        (df_stats_filtered['StartTime'].dt.date >= s) & 
                        (df_stats_filtered['StartTime'].dt.date <= e)
                    ]
                df_stats_filtered = apply_multi_range_filter(df_stats_filtered, 'Distance', imp_ranges)
                
                # 2. Impulse DF
                df_imp_filtered = impulse_raw[impulse_raw['DayOfWeek'].isin(selected_days)].copy()
                if len(date_range) == 2:
                    s, e = date_range
                    df_imp_filtered['Time'] = pd.to_datetime(df_imp_filtered['Time'])
                    df_imp_filtered = df_imp_filtered[
                        (df_imp_filtered['Time'].dt.date >= s) & 
                        (df_imp_filtered['Time'].dt.date <= e)
                    ]
                df_imp_filtered = apply_multi_range_filter(df_imp_filtered, 'Impulse', imp_ranges)
                df_imp_filtered = apply_multi_range_filter(df_imp_filtered, 'Reversal%', rev_ranges)

                # Apply min_impulse_fusion filter
                if min_impulse_fusion > 0:
                    df_imp_filtered = df_imp_filtered[df_imp_filtered['Impulse'] >= min_impulse_fusion].copy()

                if df_stats_filtered.empty or df_imp_filtered.empty:
                    st.warning("Insufficient data across one or both files to perform Fusion.")
                    st.stop()
                
                st.info(f"Fusion Context: {len(df_stats_filtered)} Trends & {len(df_imp_filtered)} Impulses")
                
                results, fused_df = run_fusion_analysis(df_stats_filtered, df_imp_filtered)
                
                st.metric("90% Survival Threshold", f"{results['pullback_90th_percentile']:.2f}%")

                
                st.markdown(f"""
                ### 🛡️ Recommended Management Zones
                - **Green Zone (<10%)**: Strength. No action needed.
                - **Yellow Zone (10% - {results['pullback_90th_percentile']:.2f}%)**: Market breathing. Prepare to trail.
                - **Red Zone (>{results['pullback_90th_percentile']:.2f}%)**: Statistical failure. High risk of full reversal.
                """)

    except Exception as e:
        st.error(f"❌ Analysis Error: {str(e)}")

# --- Footer ---
st.sidebar.divider()
st.sidebar.caption("Interactive Reversal Analysis Suite v1.1")
