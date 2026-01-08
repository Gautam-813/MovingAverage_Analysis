import pandas as pd
import numpy as np

def calculate_distribution_stats(series):
    """Calculates higher-order statistics for a series."""
    return {
        "Mean": series.mean(),
        "Median": series.median(),
        "Std Dev": series.std(),
        "Skewness": series.skew(),
        "Kurtosis": series.kurtosis(),
        "Count": len(series)
    }

def calculate_quantiles(series):
    """Calculates key trading quantiles."""
    return series.quantile([0.25, 0.50, 0.75, 0.90, 0.95])

def calculate_efficiency(distance, duration_seconds):
    """Calculates distance per unit of time (minutes)."""
    duration_minutes = duration_seconds / 60
    return distance / duration_minutes if duration_minutes > 0 else 0
