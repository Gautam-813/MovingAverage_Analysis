import pandas as pd
import numpy as np

def calculate_heatmap_matrix(df, ranges):
    """
    Calculates a frequency matrix for Reversal % across specified Impulse ranges.
    
    Args:
        df: DataFrame containing 'Impulse' and 'Reversal%' columns.
        ranges: List of tuples [(start, end), (start, end)] representing Impulse ranges.
        
    Returns:
        matrix_pcts: 2D list of probabilities (0-100%).
        matrix_counts: 2D list of raw counts.
        y_labels: List of string labels for the ranges.
        x_labels: List of string labels for the reversal bins.
    """
    if df.empty or not ranges:
        return [], [], [], []

    # 1. Define Reversal Bins (0-100% in 5% steps)
    # We go slightly above 100 to catch anything over 100
    bins = np.arange(0, 105, 5) 
    x_labels = [f"{int(bins[i])}-{int(bins[i+1])}%" for i in range(len(bins)-1)]
    
    matrix_counts = []
    matrix_pcts = []
    matrix_atrs = []
    y_labels = []

    for start, end in ranges:
        # Filter Data for this Range
        # Inclusive of start, exclusive of end (standard pythonic) or inclusive both?
        # Let's do inclusive-inclusive for user intuition
        mask = (df['Impulse'] >= start) & (df['Impulse'] <= end)
        subset = df[mask]
        
        # Create Label with Total Count
        label = f"Impulse {start}-{end} (N={len(subset)})"
        y_labels.append(label)
        
        if subset.empty:
            # Empty row of zeros
            matrix_counts.append([0] * len(x_labels))
            matrix_pcts.append([0] * len(x_labels))
            matrix_atrs.append([0] * len(x_labels))
        else:
            # Bin the Reversal %
            # cut returns a Series of Intervals
            counts_series = pd.cut(subset['Reversal%'], bins=bins, include_lowest=True, right=False).value_counts().sort_index()
            
            # Reindex to ensure all bins are present
            counts_series = counts_series.reindex(pd.cut(pd.Series([0]), bins=bins, right=False).values.categories).fillna(0)
            
            # Raw Counts
            row_counts = counts_series.tolist()
            matrix_counts.append(row_counts)
            
            # Probabilities (Percentage of this row's total)
            row_total = sum(row_counts)
            if row_total > 0:
                row_pcts = [(c / row_total) * 100.0 for c in row_counts]
            else:
                row_pcts = [0.0] * len(row_counts)
                
            matrix_pcts.append(row_pcts)

            # --- ATR Calculation Logic ---
            # We need to bin the 'subset' again to get the ATRs for each specific bin
            # pd.cut returns the bin label. We group by that.
            subset['Bin'] = pd.cut(subset['Reversal%'], bins=bins, include_lowest=True, right=False)
            
            # Group by Bin and calculate Mean BaseATR (Volatility when move started)
            # You can change 'BaseATR_Live' to 'PeakATR_Live' if preferred. Base is usually cleaner.
            atr_series = subset.groupby('Bin')['BaseATR_Live'].mean()
            
            # Reindex to match the bins structure
            # Categories must match EXACTLY what pd.cut produced above
            atr_series = atr_series.reindex(counts_series.index).fillna(0)
            
            matrix_atrs.append(atr_series.tolist())

    return matrix_pcts, matrix_counts, matrix_atrs, y_labels, x_labels
