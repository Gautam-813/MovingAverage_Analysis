import pandas as pd
import numpy as np
from analytics.statistics import calculate_distribution_stats, calculate_quantiles

def run_impulse_analysis(df):
    """
    Analyzes Impulse_Reversal.csv data for behavioral intelligence.
    """
    results = {}
    
    # 1. Pullback % Distribution
    results['pullback_stats'] = calculate_distribution_stats(df['Reversal%'])
    results['pullback_quantiles'] = calculate_quantiles(df['Reversal%'])
    
    # 2. Scaling Law (Correlating Impulse Size with Pullback Size)
    # We want to see if larger impulses lead to larger pullbacks
    correlation = df['Impulse'].corr(df['Pullback'])
    results['impulse_pullback_corr'] = correlation
    
    # Simple Linear Regression: Pullback = alpha * Impulse + epsilon
    if len(df) > 1:
        z = np.polyfit(df['Impulse'], df['Pullback'], 1)
        results['scaling_alpha'] = z[0]  # The slope
        results['scaling_intercept'] = z[1]
    
    # 3. Directional Shock Analysis
    bullish_rev = df[df['Direction'] == 'BULLISH']['Reversal%']
    bearish_rev = df[df['Direction'] == 'BEARISH']['Reversal%']
    
    results['bullish_rev_stats'] = calculate_distribution_stats(bullish_rev)
    results['bearish_rev_stats'] = calculate_distribution_stats(bearish_rev)
    
    return results, df
