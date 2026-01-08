import os

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

# Expected filenames (Sync with MQL5 EA)
CSV_STATS = "Crossover_Stats.csv"
CSV_IMPULSE = "Impulse_Reversal.csv"

# --- Column Definitions ---
COLS_STATS = [
    "StartTime", "EndTime", "Direction", "StartPrice", 
    "EndPrice", "MaxMinPrice", "Distance", "MAValue"
]

COLS_IMPULSE = [
    "Time", "Direction", "BasePrice", "Peak", 
    "TriggerPrice", "Impulse", "Pullback", "Reversal%"
]

# --- Validation Settings ---
STRICT_VALIDATION = True
VALID_DIRECTIONS = ["BULLISH", "BEARISH"]

# --- UI Settings ---
APP_TITLE = "Market Research Engine MVP"
APP_SUBTITLE = "Objective Quant Analysis of MA Crossover Behavior"
