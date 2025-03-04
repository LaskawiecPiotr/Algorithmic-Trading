import pandas as pd
import numpy as np
from signal_generator import signal_generation
from trade_simulator import Trade_Simulator
from sklearn.preprocessing import StandardScaler

def extract_features_labels(stock, data, strategy, window_size=60, feature_days=30, delay=2):
    """
    Extracts features and labels from stock data using 60-day rolling windows.

    Parameters:
    - stock: str, stock ticker symbol
    - data: pd.DataFrame, stock data (should include 'Close' and 'Volume')
    - strategy: str, trading strategy to evaluate
    - window_size: int, total length of each window (default = 60 days)
    - feature_days: int, number of days used for feature extraction (default = 30)
    - delay: int, cooldown period for trading signals in Trade_Simulator
    
    Returns:
    - X: np.array, extracted feature set (shape: num_samples x num_features x num_days)
    - y: np.array, binary labels (1 = profitable, 0 = not profitable)
    """

    X, y = [], []
    
    for start in range(len(data) - window_size):
        end = start + window_size
        window_data = data.iloc[start:end]  # Extract rolling 60-day window
        
        # 🔹 Normalize Price Data (Z-score normalization)
        price_data = window_data["Close"][:feature_days].values.reshape(-1, 1)
        price_scaler = StandardScaler()
        normalized_price = price_scaler.fit_transform(price_data).flatten()

        # 🔹 Extract Trading Signals & Technical Indicators
        long_signal, short_signal, features = signal_generation(stock, window_data[:feature_days], strategy)
        features = np.array(features)  # Convert to numpy array

        # 🔹 Combine Normalized Price with Extracted Features
        all_features = np.vstack([normalized_price, features])  # Stack vertically
        all_features = all_features.T  # Transpose to match CNN input format

        # 🔹 Determine Profitability Label from Trade Simulator
        trade_log = Trade_Simulator(stock, window_data, strategy, stop_loss=False, delay=delay, log=True,plot=False)
        
        if trade_log is not None and not trade_log.empty:
            final_entry = trade_log.iloc[-1]  # Last trade log entry
            profit = 1 if final_entry["Final Capital"] > 10000 else 0  # Compare to initial capital

            X.append(all_features)  # Store feature matrix
            y.append(profit)  # Store label

    return np.array(X), np.array(y)
