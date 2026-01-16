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
    "EndPrice", "MaxMinPrice", "Distance", "MAValue", 
    "StartATR_Closed", "StartATR_Live", 
    "PeakATR_Closed", "PeakATR_Live",
    "EndATR_Closed", "EndATR_Live",
    "PriceMove%",
    "Session_Start", "Session_Peak", "Session_End",
    "Symbol", "TF", "MAPeriod", "MAType", "ScanStart", "ScanEnd"
]

COLS_IMPULSE = [
    "Time", "Direction", "BasePrice", "Peak", 
    "TriggerPrice", "Impulse", "Pullback", "Reversal%",
    "BaseATR_Closed", "BaseATR_Live",
    "PeakATR_Closed", "PeakATR_Live",
    "RevATR_Closed", "RevATR_Live",
    "Impulse%", "Reversal%_Peak",
    "Session_Base", "Session_Peak", "Session_Trigger",
    "Symbol", "TF", "MAPeriod", "MAType", "ScanStart", "ScanEnd"
]

# --- Validation Settings ---
STRICT_VALIDATION = True
VALID_DIRECTIONS = ["BULLISH", "BEARISH"]

# --- UI Settings ---
APP_TITLE = "Market Research Engine MVP"
APP_SUBTITLE = "Objective Quant Analysis of MA Crossover Behavior"
