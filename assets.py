from google_api_functions import get_spreadsheet_data_into_a_df

### QUICK BUILD OF ASSETS UNIVERSE
fx_universe = {
    "USD": {"Name": "USD", "Ticker": "USDSGD=X"},
    "EUR": {"Name": "EUR", "Ticker": "EURSGD=X"},
    "GBP": {"Name": "GBP", "Ticker": "GBPSGD=X"},
}


master_spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1EK1vfs6kxowWl8FBCmUpvU2ldRkPQwTE5HAH3965-8Q/edit#gid=0'

asset_universe_df = get_spreadsheet_data_into_a_df(master_spreadsheet_url, sheet_name="Asset_Universe")
print("asset_universe_df")
print(asset_universe_df)

asset_universe = {}

for index, row in asset_universe_df.iterrows():
    asset_universe[row['Ticker']] = {
        'Ccy': row['Ccy'],
        'Class': row['Class'],
        'Name': row['Name']
    }


### EXTRACTING THE LIST OF INVESTMENTS IN ASSET UNIVERSE
asset_universe_inv = {k:v for (k,v) in asset_universe.items() if "Investment" in v["Class"] or "Venture" in v["Class"]}
liq_asset_universe_inv = {k:v for (k,v) in asset_universe.items() if "Investment" in v["Class"]}
venture_inv = {k:v for (k,v) in asset_universe.items() if "Venture" in v["Class"]}

liq_investments = liq_asset_universe_inv.keys()
investments = asset_universe_inv.keys()
venture_assets = venture_inv.keys()

### EXTRACTING THE LIST OF UK STOCKS IN ASSET UNIVERSE
uk_stocks_dict = {k:v for (k,v) in asset_universe.items() if "GBPSGD=X" in v["Ccy"] and "Investment" in v["Class"]}
uk_stocks = list(uk_stocks_dict.keys())
uk_stocks

