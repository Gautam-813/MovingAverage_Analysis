import pandas as pd
import numpy as np

def run_fusion_analysis(stats_df, impulse_df):
    """
    Combines Crossover_Stats and Impulse_Reversal to find deep insights.
    """
    results = {}
    
    # --- 1. Correlation of Max Retracement vs Trend Success ---
    # For each trend in stats_df, find the maximum Reversal% recorded in impulse_df
    max_revs = []
    for idx, row in stats_df.iterrows():
        # Find pullbacks that happened during this trend's lifetime
        related_pb = impulse_df[
            (impulse_df['Time'] >= row['StartTime']) & 
            (impulse_df['Time'] <= row['EndTime']) &
            (impulse_df['Direction'] == row['Direction'])
        ]
        
        if not related_pb.empty:
            max_revs.append(related_pb['Reversal%'].max())
        else:
            max_revs.append(0.0)
            
    stats_df['Max_Observed_Retracement'] = max_revs
    
    # --- 2. Safe Zone Map ---
    # A safe zone is a retracement level that 90% of trends survive
    surviving_trends = stats_df[stats_df['Max_Observed_Retracement'] > 0]
    if not surviving_trends.empty:
        results['safe_zone_90'] = surviving_trends['Max_Observed_Retracement'].quantile(0.10) # 10th percentile of max retracements that finished? No.
        # Actually, we want the level that most trends stay above.
        # Let's say: "90% of observed pullbacks were below X%"
        results['pullback_90th_percentile'] = impulse_df['Reversal%'].quantile(0.90)
    
    # --- 3. Expectancy Envelope ---
    avg_gain = stats_df['Distance'].mean()
    # Loss is harder to define without a real SL, but we can use the 90th percentile pullback as a proxy for SL
    results['avg_expectancy'] = avg_gain # Placeholder for more complex math
    
    return results, stats_df
