from flask import Flask, render_template, request, send_file, url_for
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials

#import libraries
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import os.path
import googleapiclient.discovery
import pandas as pd
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from test_gmail_api import send
import json, base64
from io import BytesIO

# import functions
from functions import generate_nav_chart_image, \
units_history, get_NAV, benchmark_history, portfolio_vs_benchmark, orders_by_stock_over_time, \
hist_ptf_value_and_cumul_invested, portfolio_today, latest_investment_tx
from google_api_functions import get_spreadsheet_data_into_a_df, send_email
from pnl import pnl_by_stock_latest

from historical_positions import historical_portfolio
from charts import NAV_chart, current_vs_invested, scatter_orders_over_time, pnl_by_stock, portfolio_today_chart
from assets import asset_universe, investments, uk_stocks

# import charts

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-report', methods=['POST'])
def generate_report():
    # Get the URL of the Google spreadsheet from the form data
    spreadsheet_url = request.form['url']

    # Get the tx data from the spreadsheet
    tx_df = get_spreadsheet_data_into_a_df(spreadsheet_url, sheet_name="Transaction_History")
    print(tx_df)

    # Get the custom asset prices data from the spreadsheet
    custom_prices_df = get_spreadsheet_data_into_a_df(spreadsheet_url, sheet_name="Custom_Prices")
    print(custom_prices_df)


    # Set report date range
    startdate=tx_df["Date"][1]
    date_range = pd.date_range(start=startdate, end=date.today(), freq='D')
    # Convert datetime objects to dates
    date_range_no_datetime = [dt.date() for dt in date_range]

    # print("DATE RANGE IN APP.PY")
    # print(date_range)
    # print("###############")

    # Build historical portfolio
    hist_ptf_df = historical_portfolio(tx_df = tx_df, custom_prices_df=custom_prices_df)

    # Build units summary
    units_history_df = units_history(tx_df = tx_df, date_range = date_range, hist_ptf_df=hist_ptf_df)

    # Build portfolio NAV
    list_values_NAV = get_NAV(tx_df = tx_df, date_range = date_range, hist_ptf_df=hist_ptf_df)

    # Generate the chart
    nav_chart_path = generate_nav_chart_image(dates = date_range, nav_prices = list_values_NAV)

    # Send the chart to the user's email
    # send_email(request.form['email'], subject="test subject", body="test body", image_path=nav_chart_path)

    # build dictionary for content variables

    dict_vars = {
        "nav_chart_path": nav_chart_path,
        "date_range_no_datetime": date_range_no_datetime,
        "list_values_NAV": list_values_NAV
    }

    # Return a response to the user
    return render_template("report.html", content=dict_vars)

@app.route('/generate-report-py', methods=['GET', 'POST'])
def generate_report_py():

    # selections from form
    bench = request.form['benchmark']
    url = request.form['url']
    report_name = request.form['report_name']
    note = request.form['note']

    # Get the tx data and custom prices from the spreadsheet
    tx_df = get_spreadsheet_data_into_a_df(url, sheet_name="Transaction_History")
    tx_df["Date"] = pd.to_datetime(tx_df["Date"])
    print("tx_df")
    print(tx_df)

    custom_prices_df = get_spreadsheet_data_into_a_df(url, sheet_name="Custom_Prices")
    # print("BEFORE CUSTOM PRICES DF")
    # print(custom_prices_df)
    # print(custom_prices_df["Date"])
    custom_prices_df['Date'] = pd.to_datetime(custom_prices_df['Date'], format='%d/%m/%Y')
    # print("AFTER CUSTOM PRICES DF")
    # print(custom_prices_df)

    # Set report date range and convert datetime objects to dates
    date_range = pd.date_range(start=tx_df["Date"][0], end=date.today(), freq='D')
    date_range_no_datetime = [dt.date() for dt in date_range]
    df_days = pd.DataFrame({'Date': date_range})
    df_days.loc[:, "Date"] = pd.to_datetime(df_days["Date"], format="%Y-%m-%d")

    
    buys_df = orders_by_stock_over_time(tx_df, "BUY", df_days)
    buys_df = buys_df[buys_df['Amount']!= 0]
    print("BUYS DF")
    print(buys_df)
    buy_bubble_sizes = buys_df['Amount'] / 100

    sells_df = orders_by_stock_over_time(tx_df, "SELL", df_days)
    sells_df = sells_df[sells_df['Amount']!=0]
    print("SELLS DF")
    print(sells_df)
    sell_bubble_sizes = sells_df['Amount'] / 100

    hist_ptf_value_and_cumul_invested_df = hist_ptf_value_and_cumul_invested(tx_df, df_days, custom_prices_df)
    hist_ptf_value_and_cumul_invested_df.to_csv("hist_ptf_value_and_cumul_invested_df.csv")
    sorted_data = pnl_by_stock_latest(tx_df, custom_prices_df, asset_universe, start_date=tx_df["Date"][0])
    sorted_data = {k: v for k, v in sorted_data.items() if v != 0}

    portfolio_today_df = portfolio_today(tx_df, custom_prices_df, asset_universe)

    # generate nav chart
    plt.switch_backend('Agg')

    chart_NAV = NAV_chart(tx_df, custom_prices_df, date_range, bench)
    chart_current_vs_invested = current_vs_invested(hist_ptf_value_and_cumul_invested_df)
    # print(hist_ptf_value_and_cumul_invested_df)
    # print(buys_df)
    # print(sells_df)
    chart_scatter_orders_over_time = scatter_orders_over_time(hist_ptf_value_and_cumul_invested_df.reset_index(), buys_df, sells_df, buy_bubble_sizes, sell_bubble_sizes)
    chart_pnl = pnl_by_stock(sorted_data)
    portfolio_today_chart_file = portfolio_today_chart(portfolio_today_df)

    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")


    dict_vars = {
        "nav_chart": chart_NAV,
        "current_vs_invested_chart": chart_current_vs_invested,
        "scatter_orders_over_time": chart_scatter_orders_over_time,
        "pnl_chart": chart_pnl,
        "portfolio_today_chart": portfolio_today_chart_file,
        "now": now,
        "date_range_no_datetime": date_range_no_datetime,
        "report_name": report_name,
        "note": note,
        "latest_tx": latest_investment_tx(tx_df)
    }

    # Return a response to the user
    return render_template("report_py.html", content=dict_vars)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))