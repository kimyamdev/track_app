from flask import Flask, render_template, request
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
#from google.oauth2.service_account import Credentials
from datetime import date, datetime, timedelta
import base64
import yfinance as yf
import os.path
import pandas as pd
import matplotlib.pyplot as plt
from units_summary import units_summary
from historical_positions import historical_portfolio


def benchmark_history(ticker, startdate, date_range):

    quote = yf.download(tickers=ticker, start=startdate, interval="1d")
    prices = quote['Adj Close'].ffill()
    df_prices = pd.DataFrame({'Price': prices})
    df_days = pd.DataFrame({'Date': date_range})
    df_prices = df_days.merge(df_prices, on="Date", how="outer")
    df_prices.loc[:, 'Price'] = df_prices.loc[:, 'Price'].ffill() / df_prices.loc[:, 'Price'].iloc[0]
    return df_prices

def portfolio_vs_benchmark(tx_df, custom_prices_df, date_range):

    hist_ptf_df = historical_portfolio(tx_df, custom_prices_df)
    list_values_NAV = get_NAV(tx_df = tx_df, date_range = date_range, hist_ptf_df=hist_ptf_df)
    bench = request.form['benchmark']
    if bench != "":
        benchmark_hist = benchmark_history(bench, startdate=date_range[0], date_range=date_range)
        list_values_benchmark = benchmark_hist['Price'].tolist()
        portfolio_vs_benchmark_df = pd.DataFrame([date_range, list_values_benchmark, list_values_NAV], index=['Date', bench, 'portfolio'])
    else:
        portfolio_vs_benchmark_df = pd.DataFrame([date_range, list_values_NAV], index=['Date', 'portfolio'])
    return portfolio_vs_benchmark_df


def orders_by_stock_over_time(tx_df, type, calendar):
    print("type")
    print(type)
    tx_df["Date"] = pd.to_datetime(tx_df['Date'])
    orders = tx_df[(tx_df['Type']==type) & ((tx_df['Class']=="Investment") | (tx_df['Class']=="Venture"))]
    print("orders in orders_by_stock_over_time")
    print(orders)
    orders.loc[:, 'FX'] = pd.to_numeric(orders['FX'])
    orders.loc[:, 'Quantity'] = pd.to_numeric(orders['Quantity'])
    orders.loc[:, 'Cost'] = pd.to_numeric(orders['Cost'])
    orders['Amount'] = orders['FX']  * orders['Quantity'] * orders['Cost']
    orders['Date'] = pd.to_datetime(orders['Date'])
    print("orders in orders_by_stock_over_time 2")
    print(orders)
    print(calendar["Date"])
    print(orders["Date"])
    historical_orders = calendar.merge(orders, on="Date", how="outer")
    historical_orders = historical_orders.fillna(0)
    print("################### historical orders ##################")
    print(historical_orders)
    if type == "SELL":
        historical_orders['Amount'] = - historical_orders['Amount']
    print("################### historical orders 2 ##################")
    print(historical_orders)
    return historical_orders


def cumul_invested(transactions_df, calendar):

    invested = transactions_df[transactions_df['Type']=='IMPORT']
    # print("########## INVESTED")
    # print(invested)
    invested.loc[:, 'Amount'] = pd.to_numeric(invested.loc[:, 'FX'])  * pd.to_numeric(invested.loc[:, 'Quantity']) * pd.to_numeric(invested.loc[:, 'Cost'])
    imports_by_day = invested.groupby('Date')['Amount'].sum()
    imports_by_day_df = pd.DataFrame(imports_by_day).reset_index()
    imports_by_day_df['Date'] = pd.to_datetime(imports_by_day_df['Date'])
    # print("calendar['Date']")
    # print(calendar['Date'])
    # print("imports_by_day_df['Date']")
    # print(imports_by_day_df['Date'])
    cumul_invested = calendar.merge(imports_by_day_df, on="Date", how="outer")
    cumul_invested['Amount'] = cumul_invested['Amount'].fillna(0)
    cumul_invested['Cumul'] = cumul_invested['Amount'].cumsum()
    
    return cumul_invested

def hist_ptf_value_and_cumul_invested(tx_df, calendar, custom_prices_df):

    hist_ptf_value_and_cumul_invested = cumul_invested(tx_df, calendar)[['Date', 'Cumul']].merge(historical_portfolio(tx_df, custom_prices_df), on="Date", how="outer")
    hist_ptf_value_and_cumul_invested = hist_ptf_value_and_cumul_invested.set_index('Date')
    hist_ptf_value_and_cumul_invested['Gains_Losses'] = hist_ptf_value_and_cumul_invested['Total Portfolio Value (SGD)'] - hist_ptf_value_and_cumul_invested['Cumul']
    return hist_ptf_value_and_cumul_invested

def portfolio_today(tx_df, custom_prices_df, asset_universe):

    hist_ptf_df = historical_portfolio(tx_df, custom_prices_df)
    p = hist_ptf_df.tail(1).T.reset_index()
    p = p.rename(columns={p.columns[0]: "attr", p.columns[1]: "val"})
    portfolio_today = p.loc[p.attr.str.match('total_position_.*'), :]
    portfolio_today = portfolio_today.sort_values(by="val", ascending=False)
    portfolio_today['Asset'] = portfolio_today['attr'].map(lambda x: x.lstrip('total_position_').rstrip(''))
    portfolio_today = portfolio_today[['Asset', 'val']]
    portfolio_today = portfolio_today.loc[(portfolio_today['val'] > 0)]
    portfolio_today['Asset_Name'] = portfolio_today['Asset'].map({k: v['Name'] for k, v in asset_universe.items()})
    return portfolio_today

def units_history(tx_df, date_range, hist_ptf_df):
    units_summary_df = units_summary(tx_df, date_range, hist_ptf_df)
    return units_summary_df

def get_NAV(tx_df, date_range, hist_ptf_df):
    list_values_NAV = units_history(tx_df = tx_df, date_range = date_range, hist_ptf_df = hist_ptf_df)['unit price'].tolist()
    return list_values_NAV

def generate_nav_chart_image(dates, nav_prices):

    plt.switch_backend('Agg')
    plt.plot(dates, nav_prices)
    plt.xlabel('Date')
    plt.ylabel('NAV')
    plt.title('NAV evolution')
    nav_chart_path = 'static/nav_chart.png'
    plt.savefig(nav_chart_path)
    return nav_chart_path

