import pandas as pd
from historical_positions import historical_portfolio
from functions import portfolio_today
from assets import asset_universe, investments, uk_stocks, liq_investments
import yfinance as yf
from datetime import date, datetime, timedelta



def pnl_by_stock_latest(tx_df, custom_prices_df, asset_universe, start_date):

    from datetime import datetime, timedelta

    # Load historical prices of the individual stocks
    print(liq_investments)
    quotes = yf.download(tickers=list(liq_investments), start=start_date, interval="1d")
    df_quotes = quotes['Adj Close'].ffill()
    latest_asset_prices = df_quotes[-1:].T
    latest_asset_prices = latest_asset_prices.reset_index()
    latest_asset_prices.columns = ["Asset", "Price"]
    latest_asset_prices = latest_asset_prices.set_index("Asset")
    latest_asset_prices = latest_asset_prices.to_dict()["Price"]
    last_custom_prices = custom_prices_df.groupby('Asset')['Unit Price'].last().to_dict()
    latest_asset_prices.update(last_custom_prices)
    latest_asset_prices = {k: float(v) for k, v in latest_asset_prices.items()}
    print(latest_asset_prices)

    # create a transactions dataframe with only investments
    transactions = tx_df.loc[(tx_df["Class"] == "Investment") | (tx_df["Class"] == "Venture") | (tx_df["Class"] == "Income")]
    transactions["Quantity"] = pd.to_numeric(transactions["Quantity"], errors='coerce')
    transactions["Cost"] = pd.to_numeric(transactions["Cost"], errors='coerce')
    transactions

    # New dictionary with revised prices
    revised_prices_dict = {}

    # Divide prices by 100 if key ends with ".L"
    for key, value in latest_asset_prices.items():
        if key in uk_stocks:
            value = value / 100
        revised_prices_dict[key] = value

    # group the transactions by asset
    grouped_transactions = transactions.groupby("Underlying_Asset")
    print("grouped_transactions")
    print(grouped_transactions)
    for key, item in grouped_transactions:
        print("KEY")
        print(grouped_transactions.get_group(key), "\n\n")


    # create a dictionary to store the current market prices for each asset
    market_prices = revised_prices_dict
    print("market_prices")
    print(market_prices)

    # calculate the net profit or loss for each stock
    profits_losses = []
    for asset, transactions in grouped_transactions:

        print("asset in grouped tx")
        print(asset)

        sell_transactions = transactions[transactions["Type"]=="SELL"]
        buy_transactions = transactions[transactions["Type"].isin(["BUY", "IMPORT"])]
        income_transactions = transactions[transactions["Type"]=="DIVIDEND / INTEREST"]

        # calculate the net profit or loss from sell transactions
        sell_profit_loss = (-sell_transactions["Quantity"]*sell_transactions["Cost"]).sum() if not sell_transactions.empty else 0
        sell_profit_loss = float(sell_profit_loss)
        # calculate the net profit or loss from buy transactions
        buy_profit_loss = (buy_transactions["Quantity"]*buy_transactions["Cost"]).sum() if not buy_transactions.empty else 0
        buy_profit_loss = float(buy_profit_loss)
        # calculate the market value of the remaining shares
        remaining_quantity = buy_transactions["Quantity"].sum() + sell_transactions["Quantity"].sum()
        current_market_value = remaining_quantity * market_prices[asset] if remaining_quantity > 0 else 0
        print(current_market_value)
        current_market_value = float(current_market_value)
        # add dividends
        total_dividends = income_transactions["Quantity"].sum()
        # calculate the total profit or loss
        total_profit_loss = sell_profit_loss - buy_profit_loss + current_market_value + total_dividends
        # add the result to the list
        profits_losses.append(total_profit_loss)

    # create a new dataframe to store the results
    results = pd.DataFrame({"asset": grouped_transactions.groups.keys(), "profits_losses": profits_losses})
    print("results")
    print(results)


    ### EXTRACTING THE LIST OF INVESTMENTS IN ASSET UNIVERSE
    currency_dict = {k: v['Ccy'] for k, v in asset_universe.items() if v['Class'] == 'Investment'}
    print("#########    currency_dict")
    print(currency_dict)
    asset_fx_prices = {}

    for asset, ccy in currency_dict.items():
        print(asset)
        print(ccy)
        if ccy == "SGD":
            asset_fx_prices[asset] = 1
        else:
            try:
                asset_fx_prices[asset] = yf.download(tickers=ccy, start=date.today() - timedelta(days=5), interval="1d").tail(1)["Adj Close"][0]
                print(yf.download(tickers=ccy, start=date.today() - timedelta(days=5), interval="1d").tail(1)["Adj Close"][0])
            except:
                print("could not find fx rate")

    mapped_dict = {}
    for asset in results['asset']:
        print(asset)
        if asset in currency_dict:
            ccy = currency_dict[asset]
            print(ccy)
            mapped_dict[asset] = results.loc[results['asset'] == asset, 'profits_losses'].values[0] * asset_fx_prices[asset]

    sorted_data = dict(sorted(mapped_dict.items(), key=lambda x: x[1], reverse=True))
    print(sorted_data)
    print("total PNL in SGD")
    print(sum(sorted_data.values()))
    return sorted_data