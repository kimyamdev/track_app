from datetime import date, datetime, timedelta
import yfinance as yf
from static_meta import fx_universe, asset_universe, investments, uk_stocks
import pandas as pd


def historical_portfolio(tx_df, custom_prices_df):

    ### DEFINING THE HISTORICAL RANGE (CALENDAR) IN A DATAFRAME THAT WE WILL RE-USE
    startdate = tx_df["Date"][0]
    # print("############### start date ###################")
    # print(startdate)
    date_range = pd.date_range(start=startdate, end=date.today(), freq='D')
    df_days = pd.DataFrame({'Date': date_range})
    df_days.loc[:, "Date"] = pd.to_datetime(df_days["Date"], format="%Y-%m-%d")
    # print("DF DAYS")
    # print(df_days)


    ### BUILDING DAILY HISTORICAL PRICES OF ASSETS AND THEIR FX
    assets_data = {}
    for asset in tx_df['Asset'].unique():

        if asset == 'SGD':
            num = [1] * len(date_range)
            s = pd.Series(num)

            df_prices = pd.DataFrame({'Date': date_range, 'Price': s})
            fx_prices = pd.DataFrame({'Date': date_range, 'FX_Price': s})
            df_days = pd.DataFrame({'Date': date_range})

            asset_prices = df_days.merge(df_prices, on="Date", how="outer")
            asset_prices = asset_prices.ffill()
            asset_prices_df = pd.DataFrame({'Date': date_range, 'Price': asset_prices['Price']})
            asset_prices_df = asset_prices_df.set_index('Date')

            assets_data[asset] = {"Prices": asset_prices_df}

            fx_prices_df = df_days.merge(fx_prices, on="Date", how="outer")
            fx_prices_df = fx_prices_df.ffill()
            fx_prices_df = pd.DataFrame({'Date': date_range, 'FX_Price': fx_prices_df['FX_Price']})
            fx_prices_df = fx_prices_df.set_index('Date')

            assets_data[asset]["FX_Prices"] = fx_prices_df

        if asset == 'JPYSGD=X':
            num = [1] * len(date_range)
            s = pd.Series(num)

            df_prices = pd.DataFrame({'Date': date_range, 'Price': s * 0.01})
            fx_prices = pd.DataFrame({'Date': date_range, 'FX_Price': s * 0.01})
            df_days = pd.DataFrame({'Date': date_range})

            asset_prices = df_days.merge(df_prices, on="Date", how="outer")
            asset_prices = asset_prices.ffill()
            asset_prices_df = pd.DataFrame({'Date': date_range, 'Price': asset_prices['Price']})
            asset_prices_df = asset_prices_df.set_index('Date')

            assets_data[asset] = {"Prices": asset_prices_df}

            fx_prices_df = df_days.merge(fx_prices, on="Date", how="outer")
            fx_prices_df = fx_prices_df.ffill()
            fx_prices_df = pd.DataFrame({'Date': date_range, 'FX_Price': fx_prices_df['FX_Price']})
            fx_prices_df = fx_prices_df.set_index('Date')

            assets_data[asset]["FX_Prices"] = fx_prices_df

        elif asset_universe[asset]["Class"] in ["Investment", "Cash"]:

            if asset_universe[asset]["Ccy"] == "SGD":

                assets_data[asset] = asset
                quote = yf.download(tickers=asset, start=startdate, interval="1d")
                prices = quote['Adj Close'].ffill()
                asset_prices = pd.DataFrame({'Price': prices})
                assets_data[asset] = {"Prices": asset_prices}


                num = [1] * len(date_range)
                s = pd.Series(num)
                fx_prices = pd.DataFrame({'Date': date_range, 'FX_Price': s})
                fx_prices_df = df_days.merge(fx_prices, on="Date", how="outer")
                fx_prices_df = fx_prices_df.ffill()
                fx_prices_df = pd.DataFrame({'Date': date_range, 'FX_Price': fx_prices_df['FX_Price']})
                fx_prices_df = fx_prices_df.set_index('Date')
                assets_data[asset]["FX_Prices"] = fx_prices_df

            elif asset_universe[asset]["Ccy"] == "JPYSGD=X":

                assets_data[asset] = asset
                quote = yf.download(tickers=asset, start=startdate, interval="1d")
                prices = quote['Adj Close'].ffill()
                asset_prices = pd.DataFrame({'Price': prices})
                assets_data[asset] = {"Prices": asset_prices}


                num = [0.01] * len(date_range)
                s = pd.Series(num)
                fx_prices = pd.DataFrame({'Date': date_range, 'FX_Price': s})
                fx_prices_df = df_days.merge(fx_prices, on="Date", how="outer")
                fx_prices_df = fx_prices_df.ffill()
                fx_prices_df = pd.DataFrame({'Date': date_range, 'FX_Price': fx_prices_df['FX_Price']})
                fx_prices_df = fx_prices_df.set_index('Date')
                assets_data[asset]["FX_Prices"] = fx_prices_df

            else:
                if asset in uk_stocks:
                    assets_data[asset] = asset
                    quote = yf.download(tickers=asset, start=startdate, interval="1d") / 100
                else:
                    assets_data[asset] = asset
                    # print(" THIS asset")
                    # print(asset)
                    quote = yf.download(tickers=asset, start=startdate, interval="1d")
                    # print("################ THIS quote ################")
                    # print(quote)

                prices = quote['Adj Close'].ffill()
                asset_prices = pd.DataFrame({'Price': prices})
                assets_data[asset] = {"Prices": asset_prices}

                fx_quote = yf.download(tickers=asset_universe[asset]["Ccy"], start=startdate, interval="1d")
                fx_prices = fx_quote['Adj Close'].ffill()
                fx_prices = pd.DataFrame({'FX_Price': fx_prices})
                # print("############ fx prices per asset ###############")
                # print(asset)
                # print(fx_prices)
                assets_data[asset]["FX_Prices"] = fx_prices

        elif asset_universe[asset]["Class"] == "Venture":

            #### FILTER CUSTOM PRICES JUST FOR THIS ASSET AND REBUILD DAILY HISTORICAL PRICES
            filtered_custom_prices_df = custom_prices_df[custom_prices_df['Asset'] == asset]
            filtered_custom_prices_df.loc[:, 'Unit Price'] = pd.to_numeric(filtered_custom_prices_df['Unit Price'])
            # print("BEFORE")
            # print(filtered_custom_prices_df)
            filtered_custom_prices_df.loc[:, "Date"] = pd.to_datetime(filtered_custom_prices_df["Date"])
            # print("AFTER")
            # print(filtered_custom_prices_df)
            # print("###################### ASSET ##########################")
            print(asset)
            # print("filtered_custom_prices_df")
            # print(filtered_custom_prices_df)
            # print("LEN FILTERED CUSTOM PRICES")
            # print(len(filtered_custom_prices_df))

            if not filtered_custom_prices_df.empty:
                local_start_date=filtered_custom_prices_df["Date"].iloc[0]
            else:
                print("Dataframe is empty!")

            # local_date_range = pd.date_range(start=local_start_date, end=date.today(), freq='D')
            # local_df_days = pd.DataFrame({'Date': local_date_range})
            # print("df_days")
            # print(df_days)
            # print("ONE")
            # print(df_days["Date"])
            # print("TWO")
            # print(filtered_custom_prices_df["Date"])

            prices = df_days.merge(filtered_custom_prices_df, on="Date", how="outer")
            prices = prices.sort_values(by="Date", ascending=True)
            prices = prices.ffill()
            # print("PRICES 1")
            # print(prices)
            prices = prices[prices['Date'] >= startdate]
            # print("PRICES 2")
            # print(prices)
            # print("LEN DATES")
            # print(len(date_range))
            # print(date_range)
            # print("LEN PRICES")
            # print(len(prices))
            # print(prices)
            asset_prices_df = pd.DataFrame({'Date': date_range, 'Price': prices['Unit Price']})
            asset_prices = asset_prices_df.set_index('Date')
            # print("PRICES 3")
            # print(asset_prices)
            assets_data[asset] = {"Prices": asset_prices}
            fx_quote = yf.download(tickers=asset_universe[asset]["Ccy"], start=startdate, interval="1d")
            fx_prices = fx_quote['Adj Close'].ffill()
            fx_prices = pd.DataFrame({'FX_Price': fx_prices})
            assets_data[asset]["FX_Prices"] = fx_prices
            # print("############ assets_data[asset] #################")
            # print(assets_data[asset])

        else:
            print("Can't find this asset")

    ### ADDING HISTORICAL CUMUL QUANTITIES FOR EACH ASSET TO ASSETS DATA DICT

    for asset in tx_df['Asset'].unique():

        # print("############ " + asset + " ############")
        asset_transactions = tx_df[(tx_df['Asset']==asset)]
        asset_transactions = asset_transactions.assign(Date = pd.to_datetime(asset_transactions['Date']))
        asset_transactions = asset_transactions.assign(Quantity = pd.to_numeric(asset_transactions['Quantity']))
        asset_transactions = asset_transactions.groupby('Date').sum()
        asset_transactions = df_days.merge(asset_transactions, on="Date", how="outer")
        asset_transactions = asset_transactions.fillna(0)
        asset_transactions["Cumul_Qty"] = asset_transactions['Quantity'].cumsum()
        asset_transactions = asset_transactions[['Date', 'Cumul_Qty']]
        assets_data[asset]["Qty"] = asset_transactions.set_index(['Date'])
        # print("Done!")

    historical_positions = []
    historical_asset_cl = []

    for asset in tx_df['Asset'].unique():
    
        # print("#####" + asset + "######")

        df_list = [assets_data[asset]['Prices'], assets_data[asset]['Qty'], assets_data[asset]['FX_Prices']]
        df = pd.concat(df_list, axis=1).reset_index()
        df['Price'] = df['Price'].ffill()
        df['FX_Price'] = df['FX_Price'].ffill()
        df['Asset'] = asset
        df['Class'] = asset_universe[asset]["Class"]
        df['Currency'] = asset_universe[asset]["Ccy"]
        df['Asset_Class'] = asset_universe[asset]["Asset_Class"]
        df = df.fillna(0)
        print("Df")
        print(df)
        historical_asset_cl.append(df[['Date', 'Price', 'Cumul_Qty', 'FX_Price', 'Asset', 'Class', 'Currency', 'Asset_Class']])

        if asset_universe[asset]['Class'] == 'Cash':
            df[str('total_position_'+ asset)] = df['Cumul_Qty'] * df['Price']
        else:
            df[str('total_position_' + asset)] = df['Cumul_Qty'] * df['Price'] * df['FX_Price']
        df = df.fillna(0)
        print("############ DF FILL NA ################")
        print(df)
        # if asset == "CFA.SI":
        #     df.to_csv("CFA.SI.csv")
        # if asset == "CLR.SI":
        #     df.to_csv("CLR.SI.csv")
        historical_positions.append(df)

    concat_list = []

    vertical_concat = pd.concat(historical_asset_cl, axis=0)
    print("vertical_concat")
    print(vertical_concat)

    vertical_concat['Position_SGD'] = vertical_concat['Price'] * vertical_concat['Cumul_Qty'] * vertical_concat['FX_Price']

    # Assuming your DataFrame is named df
    new_df = vertical_concat.groupby(['Date', 'Asset_Class'])['Position_SGD'].sum()

    print(new_df)
    new_df.to_csv("new_df.csv")

    for df in historical_positions:
        filtered_df = df.filter(regex=("total_position_.*"))
        print("filtered_df")
        print(filtered_df)
        concat_list.append(filtered_df)

    hist_ptf_df = pd.concat(concat_list, axis=1)
    hist_ptf_df = hist_ptf_df.ffill()
    # print("hist_ptf_df 2")
    # print(hist_ptf_df)

    cols = hist_ptf_df.columns
    # print("#################### hist_ptf_df ####################")
    # print(hist_ptf_df)
    
    hist_ptf_df["Total Portfolio Value (SGD)"] = hist_ptf_df.sum(axis=1)
    # print("hist_ptf_df 2")
    # print(hist_ptf_df)
    hist_ptf_df[cols]  = hist_ptf_df[cols].div(hist_ptf_df[cols].sum(axis=1), axis=0)
    # print("hist_ptf_df 3")
    # print(hist_ptf_df)
    hist_ptf_df = hist_ptf_df.set_index(date_range)
    hist_ptf_df = hist_ptf_df.reset_index()
    hist_ptf_df = hist_ptf_df.rename({'index': 'Date'}, axis=1)

    # print("################ hist_ptf_df final ######################")
    # print(hist_ptf_df)

    return hist_ptf_df, new_df