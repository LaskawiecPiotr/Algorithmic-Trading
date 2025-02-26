def Trade_Simulator(data,strategy=["OLS","BB"]):
    data["Long Signal"]  = data[f"Spread_{strategy[0]}"] < data[f'{strategy[1]}_Lower_{strategy[0]}']
    data["Short Signal"] = data[f"Spread_{strategy[0]}"] > data[f'{strategy[1]}_Upper_{strategy[0]}']
    data["Exit Signal"]  = abs(data[f"Spread_{strategy[0]}"] - data[f'{strategy[1]}_Exit_{strategy[0]}']) < 0.03
    capital = 10000
    position_size = 1000
    capital_over_time = []
    in_position = False
    trade_type = None
    entry_prices = {}
    trade_log = []
    trading_start = 20

    for i in range(trading_start, len(data)):
        if in_position:
            # Check exit
            if data["Exit Signal"].iloc[i]:
                exit_price_PEP = data[stock1].iloc[i]
                exit_price_KO  = data[stock2].iloc[i]
                if trade_type == "long":
                    profit_PEP = (exit_price_PEP - entry_prices["PEP"]) * position_size
                    profit_KO  = (entry_prices["KO"] - exit_price_KO)  * position_size
                else:
                    # short
                    profit_PEP = (entry_prices["PEP"] - exit_price_PEP) * position_size
                    profit_KO  = (exit_price_KO - entry_prices["KO"])   * position_size
                
                capital += (profit_PEP + profit_KO)
                trade_log.append({
                    "Date": data.index[i],
                    "Type": "EXIT",
                    "Exit Price PEP": exit_price_PEP,
                    "Exit Price KO":  exit_price_KO,
                    "Profit PEP":     profit_PEP,
                    "Profit KO":      profit_KO,
                    "Total Profit":   profit_PEP + profit_KO
                })
                in_position = False
                trade_type = None
                entry_prices = {}
        else:
            # Check entry
            if data["Long Signal"].iloc[i]:
                entry_prices["PEP"] = data[stock1].iloc[i]
                entry_prices["KO"]  = data[stock2].iloc[i]
                trade_type = "long"
                in_position = True
                trade_log.append({
                    "Date": data.index[i],
                    "Type": "BUY (Long PEP, Short KO)",
                    "Entry Price PEP": entry_prices["PEP"],
                    "Entry Price KO":  entry_prices["KO"]
                })
            elif data["Short Signal"].iloc[i]:
                entry_prices["PEP"] = data[stock1].iloc[i]
                entry_prices["KO"]  = data[stock2].iloc[i]
                trade_type = "short"
                in_position = True
                trade_log.append({
                    "Date": data.index[i],
                    "Type": "SELL (Short PEP, Long KO)",
                    "Entry Price PEP": entry_prices["PEP"],
                    "Entry Price KO":  entry_prices["KO"]
                })
        capital_over_time.append(capital)

    trade_log_df = pd.DataFrame(trade_log)

    # Plot the Spread with Trade Markers
    plt.figure(figsize=(12,6))
    plt.plot(data.index, data[f"Spread_{strategy[0]}"], label=f"Spread ({strategy[0]})", color="black")
    plt.plot(data.index, data[f'{strategy[1]}_Upper_{strategy[0]}'], color='red', linestyle='--', label='Upper Threshold')
    plt.plot(data.index, data[f'{strategy[1]}_Lower_{strategy[0]}'], color='green', linestyle='--', label='Lower Threshold ')
    plt.plot(data.index, data[f'{strategy[1]}_Exit_{strategy[0]}'],  color='blue', linestyle='--', label='Exit Threshold ')

    for _, trade in trade_log_df.iterrows():
        if "BUY" in trade["Type"]:
            plt.scatter(trade["Date"], data.loc[trade["Date"], f"Spread_{strategy[0]}"], marker="^", color="green", s=100)
        elif "SELL" in trade["Type"]:
            plt.scatter(trade["Date"], data.loc[trade["Date"], f"Spread_{strategy[0]}"], marker="v", color="red", s=100)
        elif "EXIT" in trade["Type"]:
            plt.scatter(trade["Date"], data.loc[trade["Date"], f"Spread_{strategy[0]}"], marker="o", color="blue", s=70)

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    plt.title("Pairs Trading Strategy - Trade Execution Points")
    plt.xlabel("Date")
    plt.ylabel("Spread")
    plt.show()

    # Capital over time
    plt.figure(figsize=(12,6))
    plt.plot(capital_over_time, label="Capital over time", color="black")
    plt.title("Strategy Equity Curve")
    plt.legend()
    plt.show()