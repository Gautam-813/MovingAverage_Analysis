import pandas as pd
import numpy as np

def calculate_heatmap_matrix(df, ranges, y_col='Impulse'):
    """
    Calculates a frequency matrix for Reversal % across specified ranges of a Y column.
    
    Args:
        df: DataFrame containing the data.
        ranges: List of tuples [(start, end), ...] representing ranges for the Y column.
        y_col: The column to use for the Y-axis (e.g. 'Impulse' or 'Impulse%').
        
    Returns:
        matrix_pcts, matrix_counts, matrix_atrs, y_labels, x_labels
    """
    if df.empty or not ranges:
        return [], [], [], [], []

    # 1. Define Reversal Bins (0-100% in 5% steps + Overflow)
    bins = list(range(0, 105, 5)) + [9999]  # Catch all up to 10000%
    x_labels = [f"{bins[i]}-{bins[i+1]}%" if bins[i+1] <= 100 else ">100%" for i in range(len(bins)-1)]
    
    matrix_counts = []
    matrix_pcts = []
    matrix_atrs = []
    matrix_total_pcts = []
    y_labels = []

    total_n = len(df)

    for start, end in ranges:
        # Filter Data for this Range in the specified Y column
        mask = (df[y_col] >= start) & (df[y_col] <= end)
        subset = df[mask].copy() # copy to avoid slice warnings
        
        # Create Label with Total Count and % of Total Data
        subset_n = len(subset)
        subset_pct_of_total = (subset_n / total_n * 100) if total_n > 0 else 0
        
        # Format requested: Impulse 0.5% (N=225 | 15% of total)
        unit = "%" if "Percent" in y_col or "%" in y_col else " pts"
        label = f"{y_col} {start}-{end}{unit} (N={subset_n} | {subset_pct_of_total:.1f}% of total)"
        y_labels.append(label)
        
        if subset.empty:
            matrix_counts.append([0] * len(x_labels))
            matrix_pcts.append([0] * len(x_labels))
            matrix_atrs.append([0] * len(x_labels))
            matrix_total_pcts.append([0] * len(x_labels))
        else:
            # Bin the Reversal % (including overflow)
            subset['Bin'] = pd.cut(subset['Reversal%'], bins=bins, include_lowest=True, right=False)
            counts_series = subset['Bin'].value_counts().sort_index()
            
            # Ensure all bins are present even if empty
            counts_series = counts_series.reindex(subset['Bin'].cat.categories).fillna(0)
            
            row_counts = counts_series.astype(int).tolist()
            matrix_counts.append(row_counts)
            
            # Use subset_n for perfect row-wise percentages
            matrix_pcts.append([(c / subset_n) * 100.0 if subset_n > 0 else 0.0 for c in row_counts])

            # Total Density % (Cell Count / Total dataframe count)
            matrix_total_pcts.append([(c / total_n) * 100.0 if total_n > 0 else 0.0 for c in row_counts])

            # ATR Calculation Logic
            atr_series = subset.groupby('Bin', observed=False)['BaseATR_Live'].mean()
            atr_series = atr_series.reindex(subset['Bin'].cat.categories).fillna(0)
            matrix_atrs.append(atr_series.tolist())

    return matrix_pcts, matrix_counts, matrix_atrs, matrix_total_pcts, y_labels, x_labels

def calculate_session_comparison_matrix(df):
    """
    Calculates a frequency matrix comparing Reversal % distributions across Sessions.
    """
    if df.empty:
        return [], [], [], [], [], []

    sessions = ["SYDNEY", "TOKYO", "LONDON", "NEW YORK"]
    # Bins including overflow
    bins = list(range(0, 105, 5)) + [9999]
    x_labels = [f"{bins[i]}-{bins[i+1]}%" if bins[i+1] <= 100 else ">100%" for i in range(len(bins)-1)]
    
    matrix_counts = []
    matrix_pcts = []
    matrix_atrs = []
    matrix_total_pcts = []
    y_labels = []

    total_n = len(df)

    for sess in sessions:
        mask = (df['Session_Peak'] == sess)
        subset = df[mask].copy()
        
        subset_n = len(subset)
        subset_pct = (subset_n / total_n * 100) if total_n > 0 else 0
        y_labels.append(f"{sess} (N={subset_n} | {subset_pct:.1f}% of total)")
        
        if subset.empty:
            matrix_counts.append([0] * len(x_labels))
            matrix_pcts.append([0] * len(x_labels))
            matrix_atrs.append([0] * len(x_labels))
            matrix_total_pcts.append([0] * len(x_labels))
        else:
            # Binning with overflow
            subset['Bin'] = pd.cut(subset['Reversal%'], bins=bins, include_lowest=True, right=False)
            counts_series = subset['Bin'].value_counts().sort_index()
            counts_series = counts_series.reindex(subset['Bin'].cat.categories).fillna(0)
            
            row_counts = counts_series.astype(int).tolist()
            matrix_counts.append(row_counts)
            
            # Pcts (Row-wise) using subset_n for perfect math
            matrix_pcts.append([(c / subset_n) * 100.0 if subset_n > 0 else 0.0 for c in row_counts])
            
            # Total Density %
            matrix_total_pcts.append([(c / total_n) * 100.0 if total_n > 0 else 0.0 for c in row_counts])

            # ATRs
            atr_series = subset.groupby('Bin', observed=False)['BaseATR_Live'].mean()
            atr_series = atr_series.reindex(subset['Bin'].cat.categories).fillna(0)
            matrix_atrs.append(atr_series.tolist())

    return matrix_pcts, matrix_counts, matrix_atrs, matrix_total_pcts, y_labels, x_labels
