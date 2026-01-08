import pandas as pd
from analytics.statistics import calculate_distribution_stats, calculate_quantiles

def run_trend_analysis(df):
    """
    Analyzes Crossover_Stats.csv data for trend intelligence.
    """
    results = {}
    
    # 1. Global Distance Distribution
    results['global_stats'] = calculate_distribution_stats(df['Distance'])
    results['global_quantiles'] = calculate_quantiles(df['Distance'])
    
    # 2. Directional Asymmetry
    bullish_df = df[df['Direction'] == 'BULLISH']
    bearish_df = df[df['Direction'] == 'BEARISH']
    
    results['bullish_stats'] = calculate_distribution_stats(bullish_df['Distance'])
    results['bearish_stats'] = calculate_distribution_stats(bearish_df['Distance'])
    
    # 3. Duration Analysis
    df['Duration_Min'] = (df['EndTime'] - df['StartTime']).dt.total_seconds() / 60
    results['avg_duration'] = df['Duration_Min'].mean()
    
    # 4. Efficiency Analysis (Distance per Minute)
    # Filter out zero duration to avoid division by zero
    valid_duration = df[df['Duration_Min'] > 0].copy()
    valid_duration['Efficiency'] = valid_duration['Distance'] / valid_duration['Duration_Min']
    results['efficiency_stats'] = calculate_distribution_stats(valid_duration['Efficiency'])
    
    return results, df
