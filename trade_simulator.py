import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from signal_generator import signal_generation
from plot_generation import plot_generator
def Trade_Simulator(stock, data, strategy, stop_loss=False):
    """
    A trading simulator supporting multiple strategies.
    
    Parameters:
    - stock: str, the stock ticker (column name in `data`)
    - data: pd.DataFrame, closing prices
    - strategy: str, trading strategy name
    - stop_loss: bool, whether to use stop-loss exits
    - second_stock: str, for pairs trading
    
    Returns:
    - trade_log_df: pd.DataFrame, trade execution log
    """
    long_signal, short_signal,curve_data=signal_generation(stock,data,strategy)
    data=data["Close"]
    capital = 10000.0
    position_size=100
    capital_over_time = []
    in_position = False
    trade_type = None
    trade_log = []
    
    for i in range(20, len(data)):
        if in_position:
            stop_loss_price = 0.95 * data[stock].iloc[i] if trade_type == "long" else 1.05 * data[stock].iloc[i]
            if stop_loss and ((trade_type == "long" and data[stock].iloc[i] < stop_loss_price) or (trade_type == "short" and data[stock].iloc[i] > stop_loss_price)):
                capital += position_size * data[stock].iloc[i] if trade_type == "long" else position_size* data[stock].iloc[i]
                trade_log.append({"Date": data.index[i], "Type": "STOP-LOSS EXIT", "Exit Price": data[stock].iloc[i], "Final Capital": capital})
                in_position = False
                trade_type = None
                shares = 0
            elif (trade_type == "long" and short_signal.iloc[i]) or (trade_type == "short" and long_signal.iloc[i]):
                capital += position_size * data[stock].iloc[i] if trade_type == "long" else position_size * data[stock].iloc[i]
                trade_log.append({"Date": data.index[i], "Type": "EXIT", "Exit Price": data[stock].iloc[i], "Final Capital": capital})
                in_position = False
                trade_type = None
                shares = 0
        else:
            if long_signal.iloc[i]:
                capital -= position_size * data[stock].iloc[i]
                in_position = True
                trade_type = "long"
                trade_log.append({"Date": data.index[i], "Type": "LONG", "Remaining Capital": capital})
            elif short_signal.iloc[i]:
                capital += position_size * data[stock].iloc[i]
                in_position = True
                trade_type = "short"
                trade_log.append({"Date": data.index[i], "Type": "SHORT", "Remaining Capital": capital})
        capital_over_time.append(capital)
    trade_log_df=pd.DataFrame(trade_log)

    plot_generator(stock,data,curve_data,strategy,trade_log_df,capital_over_time)
    return trade_log_df  # Return trade log for analysis
