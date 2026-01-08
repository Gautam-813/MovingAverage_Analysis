import pandas as pd
import io
import config

def validate_dataframe(df, expected_cols):
    """General validation logic for any dataframe."""
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns: {missing_cols}")
    return df.dropna(subset=[expected_cols[0], expected_cols[1]]) # Drop rows missing key identifiers

def load_and_validate_stats(uploaded_file):
    """Loads and validates Stats CSV from an uploaded file object."""
    df = pd.read_csv(uploaded_file)
    df = validate_dataframe(df, config.COLS_STATS)
    
    # DateTime conversion
    df['StartTime'] = pd.to_datetime(df['StartTime'])
    df['EndTime'] = pd.to_datetime(df['EndTime'])
    
    # Direction validation
    df['Direction'] = df['Direction'].str.upper()
    df = df[df['Direction'].isin(config.VALID_DIRECTIONS)]
    
    # Logical numeric validation
    df = df[df['StartPrice'] > 0]
    df['Distance'] = df['Distance'].astype(float)
    
    return df

def load_and_validate_impulse(uploaded_file):
    """Loads and validates Impulse CSV from an uploaded file object."""
    df = pd.read_csv(uploaded_file)
    df = validate_dataframe(df, config.COLS_IMPULSE)
    
    # DateTime conversion
    df['Time'] = pd.to_datetime(df['Time'])
    
    # Direction validation
    df['Direction'] = df['Direction'].str.upper()
    df = df[df['Direction'].isin(config.VALID_DIRECTIONS)]
    
    # Logical numeric validation
    df = df[df['BasePrice'] > 0]
    df['Reversal%'] = df['Reversal%'].astype(float)
    
    return df
