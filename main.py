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
        "3. Combined Market Structure (Fusion)",
        "4. Price Movement Analysis (Volatility)"
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

        def generate_linear_ranges(start, step, count):
            """Generates a comma-separated string of ranges: '0-10, 11-20, ...'"""
            if count <= 0: return ""
            ranges_list = []
            curr = float(start)
            for _ in range(int(count)):
                nxt = curr + float(step)
                # Format to avoid floating point mess (e.g. 0.30000000004)
                ranges_list.append(f"{round(curr, 4)}-{round(nxt, 4)}")
                curr = nxt
            return ", ".join(ranges_list)

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

        # 5. Universal Range Generator (SIDEBAR)
        st.sidebar.divider()
        st.sidebar.header("🛠️ Universal Range Setup")
        range_op = st.sidebar.radio("Input Method", ["Manual", "Auto-Generate"], key="range_op")
        
        if range_op == "Auto-Generate":
            c1, c2 = st.sidebar.columns(2)
            # Context-sensitive defaults
            is_pm = analysis_type.startswith("4")
            g_start = c1.number_input("Start", value=0.0, format="%.3f" if is_pm else "%.2f", key="side_s")
            g_step  = c2.number_input("Step", value=0.05 if is_pm else 10.0, format="%.3f" if is_pm else "%.2f", key="side_st")
            g_count = st.sidebar.number_input("Count", value=10, step=1, key="side_c")
            
            if st.sidebar.button("Generate & Apply Ranges"):
                gen_str = generate_linear_ranges(g_start, g_step, g_count)
                if is_pm: st.session_state['pm_ranges_input'] = gen_str
                else: st.session_state['sess_hm_input'] = gen_str # Sync points to main heatmap key
        
        else:
            # Manual Mode: Provide text inputs in Sidebar
            is_pm = analysis_type.startswith("4")
            if is_pm:
                st.sidebar.text_input("Impulse % Ranges", value="0-0.05, 0.05-0.1, 0.1-0.2, 0.2-0.5, 0.5-1.0", key="pm_ranges_input")
            else:
                st.sidebar.text_input("Impulse (Point) Ranges", value="10-20, 21-30, 31-40, 41-50, 51-60, 61-70, 71-80, 81-90, 91-100, 100-150, 151-200", key="sess_hm_input")
            
            # Additional Reversal Filtering (Optional)
            st.sidebar.text_input("Reversal % Filtering Bands (Global)", value="0-100", key="global_rev_input")

        # Selection Logic

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
                    
                    # Pull Impulse ranges from Sidebar
                    imp_ranges = parse_multi_range(st.session_state.get('sess_hm_input', ""))
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
                
                # Session Box Plot (New)
                if 'Session_Start' in df.columns:
                     from plots.trend_plots import plot_distance_by_session
                     st.plotly_chart(plot_distance_by_session(df))
                
                # Scatter Plot with Options
                scatter_color = st.selectbox("Scatter Plot Color", ["Direction", "Session_Start", "DayOfWeek"], key="scatter_col")
                st.plotly_chart(plot_duration_vs_distance(df, color_by=scatter_color))
                
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
                    
                    # Pull from Sidebar
                    imp_ranges = parse_multi_range(st.session_state.get('sess_hm_input', ""))
                    rev_ranges = parse_multi_range(st.session_state.get('global_rev_input', ""))
                
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
                
                # --- Advanced Filters ---
                st.markdown("### 🎯 Session Coherence")
                show_samesess = st.checkbox("Show Only Same-Session Events (Base = Peak = Trigger)", value=False)
                
                # Calculate Same-Session Metric before filtering
                if 'Session_Base' in df_filtered.columns and 'Session_Trigger' in df_filtered.columns:
                    # Strict Definition: Base, Peak, and Trigger must match
                    # Or at least Start (Base) and End (Trigger) match?
                    # User said: "crossover impulse and reversal was there in the same session"
                    # Let's enforce Base == Peak == Trigger for "Perfect" coherence
                    same_sess_mask = (df_filtered['Session_Base'] == df_filtered['Session_Peak']) & (df_filtered['Session_Peak'] == df_filtered['Session_Trigger'])
                    same_sess_count = same_sess_mask.sum()
                    same_sess_ratio = (same_sess_count / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
                else:
                    same_sess_ratio = 0
                    same_sess_mask = pd.Series([True]*len(df_filtered), index=df_filtered.index)

                if show_samesess:
                    df_filtered = df_filtered[same_sess_mask].copy()
                    if df_filtered.empty:
                        st.warning("No events found where Base, Peak, and Trigger occurred in the same session.")
                        st.stop()

                results, df = run_impulse_analysis(df_filtered)
                
                # --- Metrics ---
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Median Reversal %", f"{results['pullback_stats']['Median']:.2f}%")
                col2.metric("90th Percentile Pullback", f"{results['pullback_quantiles'][0.9]:.2f}%")
                col3.metric("Impulse/Pullback Corr", f"{results['impulse_pullback_corr']:.2f}")
                col4.metric("Same-Session Coherence", f"{same_sess_ratio:.1f}%", help="% of events starting and ending in the same session")
                
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

                # --- SHARED CONTROLS ---
                c1, c2 = st.columns(2)
                heatmap_sess = c1.radio("Session", ["ALL", "SYDNEY", "TOKYO", "LONDON", "NEW YORK"], horizontal=True, key="heatmap_sess")
                view_mode = c2.radio("Chart Style", ["2D Grid", "3D Topography"], horizontal=True, key="view_mode")

                st.divider()
                st.markdown("### 🌡️ Volatility & Reversal Heatmap")
                
                # --- GLOBAL MASTER HEATMAP (Shown if ALL selected) ---
                if heatmap_sess == "ALL":
                    st.markdown("#### 🌍 Global Master Heatmap (All Sessions Combined)")
                    # Use sess_hm_input from sidebar
                    global_ranges = parse_multi_range(st.session_state.get('sess_hm_input', ""))
                    
                    if global_ranges:
                        g_pcts, g_counts, g_atrs, g_total_pcts, g_y, g_x = calculate_heatmap_matrix(df_hm, global_ranges)
                        
                        if view_mode == "2D Grid":
                            st.plotly_chart(plot_heatmap_matrix(g_pcts, g_counts, g_atrs, g_total_pcts, g_x, g_y, title_suffix=" — Global Master"), use_container_width=True)
                        else:
                            from plots.heatmap_plots import plot_heatmap_3d
                            st.plotly_chart(plot_heatmap_3d(g_pcts, g_x, g_y, title_suffix=" — Global Master"), use_container_width=True)
                    st.divider()

                # --- SESSION-SPECIFIC HEATMAPS ---
                st.markdown("#### ⚡ Session-Specific Comparative Analysis")
                
                heatmap_ranges = parse_multi_range(st.session_state.get('sess_hm_input', ""))
                
                if heatmap_ranges:
                   # Determine which sessions to plot
                   if heatmap_sess == "ALL":
                       sessions_to_plot = ["SYDNEY", "TOKYO", "LONDON", "NEW YORK"]
                   else:
                       sessions_to_plot = [heatmap_sess]
                   
                   for sess in sessions_to_plot:
                       # Filter by Session
                       if 'Session_Peak' in df_hm.columns:
                           df_sess = df_hm[df_hm['Session_Peak'] == sess]
                       else:
                           df_sess = df_hm if sess == "ALL" else pd.DataFrame()
                       
                       if df_sess.empty:
                           if heatmap_sess != "ALL": st.warning(f"No data for session: {sess}")
                           continue
                       
                       # Calculate Matrix (using the MASTER df_hm for total density context? 
                       # Or the session df? Let's use df_hm for the total context)
                       m_pcts, m_counts, m_atrs, m_tpcts, y_labels, x_labels = calculate_heatmap_matrix(df_sess, heatmap_ranges)
                       
                       title_suffix = f" — {sess} Session"
                       
                       if view_mode == "2D Grid":
                           st.plotly_chart(plot_heatmap_matrix(m_pcts, m_counts, m_atrs, m_tpcts, x_labels, y_labels, title_suffix=title_suffix), use_container_width=True)
                       else:
                           from plots.heatmap_plots import plot_heatmap_3d
                           st.plotly_chart(plot_heatmap_3d(m_pcts, x_labels, y_labels, title_suffix=title_suffix), use_container_width=True)
                       
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
                    
                    # Pull from Sidebar
                    imp_ranges = parse_multi_range(st.session_state.get('sess_hm_input', ""))
                    rev_ranges = parse_multi_range(st.session_state.get('global_rev_input', ""))
                
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

        elif analysis_type.startswith("4."):
            if not uploaded_impulse:
                st.warning("⚠️ Please upload `Impulse_Reversal.csv` to run Price Movement Analysis.")
            else:
                st.subheader("📈 Price Movement Analysis (Volatility)")
                df_raw = load_and_validate_impulse(uploaded_impulse)
                
                # Check for new columns
                if 'Impulse%' not in df_raw.columns:
                    st.error("Missing `%` columns. Please regenerate data with the latest EA.")
                else:
                    # --- Filtering & Logic ---
                    # (Re-use Option 2 filtering logic or simplify)
                    with st.expander("🛠️ Filters", expanded=True):
                         c1, c2 = st.columns(2)
                         selected_days = c1.multiselect("Days", options=days_order, default=days_order, key="pm_days")
                         min_imp = c2.slider("Min Impulse (%)", 0.0, 5.0, 0.0, 0.01)
                    
                    df_pm = df_raw[df_raw['DayOfWeek'].isin(selected_days)].copy()
                    df_pm = df_pm[df_pm['Impulse%'] >= min_imp]

                    # Metrics
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Avg Impulse %", f"{df_pm['Impulse%'].mean():.3f}%")
                    c2.metric("Max Impulse %", f"{df_pm['Impulse%'].max():.3f}%")
                    c3.metric("Total Waves", len(df_pm))
                    same_sess_mask = (df_pm['Session_Base'] == df_pm['Session_Peak']) & (df_pm['Session_Peak'] == df_pm['Session_Trigger'])
                    c4.metric("Coherence", f"{(same_sess_mask.sum()/max(1,len(df_pm))*100):.1f}%")

                    st.divider()
                    # Range Setup for Option 4
                    st.markdown("### 🌡️ Price % Heatmap")
                    
                    pm_ranges = parse_multi_range(st.session_state.get('pm_ranges_input', ""))

                    if pm_ranges:
                        # Shared controls
                        c1, c2 = st.columns(2)
                        pm_sess = c1.radio("Session", ["ALL", "SYDNEY", "TOKYO", "LONDON", "NEW YORK"], horizontal=True, key="pm_sess")
                        view_type = c2.radio("Analysis Mode", ["Aggregate (Master)", "Time-Based (Month/Quarter)"], horizontal=True, key="pm_view_type")

                        # --- MODE A: AGGREGATE (Standard) ---
                        if view_type == "Aggregate (Master)":
                            # Chart Style Selector (Shared for all aggregate charts)
                            pm_view = st.radio("Chart Style", ["2D Grid", "3D Topography"], horizontal=True, key="pm_view_agg")
                            
                            # 1. Global Master (If ALL)
                            if pm_sess == "ALL":
                                st.markdown("#### 🌍 Global Master % Heatmap")
                                g_p, g_c, g_a, g_tp, y_l, x_l = calculate_heatmap_matrix(df_pm, pm_ranges, y_col='Impulse%')
                                if pm_view == "2D Grid":
                                    st.plotly_chart(plot_heatmap_matrix(g_p, g_c, g_a, g_tp, x_l, y_l, title_suffix=" — Global Master"), use_container_width=True)
                                else:
                                    from plots.heatmap_plots import plot_heatmap_3d
                                    st.plotly_chart(plot_heatmap_3d(g_p, x_l, y_l, title_suffix=" — Global Master"), use_container_width=True)
                                st.divider()

                            # 2. Session Specific
                            if pm_sess == "ALL": sessions = ["SYDNEY", "TOKYO", "LONDON", "NEW YORK"]
                            else: sessions = [pm_sess]

                            for s in sessions:
                                sub = df_pm[df_pm['Session_Peak'] == s]
                                if sub.empty: continue
                                
                                m_p, m_c, m_a, m_tp, y_l, x_l = calculate_heatmap_matrix(sub, pm_ranges, y_col='Impulse%')
                                st.markdown(f"#### {s} Session")
                                if pm_view == "2D Grid":
                                    st.plotly_chart(plot_heatmap_matrix(m_p, m_c, m_a, m_tp, x_l, y_l, title_suffix=f" — {s}"), use_container_width=True)
                                else:
                                    from plots.heatmap_plots import plot_heatmap_3d
                                    st.plotly_chart(plot_heatmap_3d(m_p, x_l, y_l, title_suffix=f" — {s}"), use_container_width=True)
                        
                        # --- MODE B: TIME-BASED ---
                        else:
                            # Apply Session Filter if not ALL
                            df_time = df_pm.copy()
                            if pm_sess != "ALL":
                                df_time = df_time[df_time['Session_Peak'] == pm_sess]
                                st.markdown(f"**Filtering by Session:** {pm_sess}")
                            
                            from engines.temporal_analysis import render_temporal_analysis_ui
                            render_temporal_analysis_ui(df_time, pm_ranges)

    except Exception as e:
        st.error(f"❌ Analysis Error: {str(e)}")

# --- Footer ---
st.sidebar.divider()
st.sidebar.caption("Interactive Reversal Analysis Suite v1.1")
