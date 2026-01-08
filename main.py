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
st.sidebar.header("⚙️ Analysis Settings")
min_impulse = st.sidebar.slider("Minimum Impulse Filter (Points)", min_value=0.0, max_value=200.0, value=5.0, step=1.0)

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

        if "1." in analysis_type:
            if not uploaded_stats:
                st.warning("⚠️ Please upload `Crossover_Stats.csv` in the sidebar to run Trend Intelligence.")
            else:
                st.subheader("🔵 Crossover Trend Intelligence")
                df_raw = load_and_validate_stats(uploaded_stats)
                results, df = run_trend_analysis(df_raw)
                
                # --- Metrics ---
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Avg Distance", f"{results['global_stats']['Mean']:.2f}")
                col2.metric("Median Distance", f"{results['global_stats']['Median']:.2f}")
                col3.metric("Avg Duration (Min)", f"{results['avg_duration']:.1f}")
                col4.metric("Bullish/Bearish Ratio", f"{len(df[df['Direction']=='BULLISH'])/len(df[df['Direction']=='BEARISH']):.2f}")
                
                # --- Plotly Charts ---
                st.plotly_chart(plot_distance_distribution(df))
                st.plotly_chart(plot_duration_vs_distance(df))
                
                with st.expander("View Raw Intelligence Table"):
                    st.dataframe(df)

        elif "2." in analysis_type:
            if not uploaded_impulse:
                st.warning("⚠️ Please upload `Impulse_Reversal.csv` in the sidebar to run Behavioral Analysis.")
            else:
                st.subheader("🔴 Impulse & Reversal Behavior")
                df_raw = load_and_validate_impulse(uploaded_impulse)
                
                # Apply Impulse Filter
                df_filtered = df_raw[df_raw['Impulse'] >= min_impulse].copy()
                st.info(f"Filtering: Keeping {len(df_filtered)} of {len(df_raw)} logs with Impulse >= {min_impulse}")
                
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


        elif "3." in analysis_type:
            if not uploaded_stats or not uploaded_impulse:
                st.warning("⚠️ Fusion Analysis requires BOTH CSV files to be uploaded.")
            else:
                st.subheader("🟣 Combined Market Structure (Fusion)")
                stats_df = load_and_validate_stats(uploaded_stats)
                impulse_raw = load_and_validate_impulse(uploaded_impulse)
                
                # Apply Impulse Filter
                impulse_df = impulse_raw[impulse_raw['Impulse'] >= min_impulse].copy()
                
                results, fused_df = run_fusion_analysis(stats_df, impulse_df)
                
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
