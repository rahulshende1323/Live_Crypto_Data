import requests
import pandas as pd
import time
import datetime
from openpyxl import Workbook
import schedule

# Function to fetch live cryptocurrency data
def fetch_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": False
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

# Function to process and structure the data
def process_crypto_data(data):
    if not data:
        print("No data fetched. Check API response.")
        return pd.DataFrame()  # Return empty DataFrame if no data

    crypto_list = []
    
    for crypto in data:
        crypto_list.append([
            crypto["name"],
            crypto["symbol"].upper(),
            crypto["current_price"],
            crypto["market_cap"],
            crypto["total_volume"],
            crypto["price_change_percentage_24h"]
        ])
    
    columns = ["Name", "Symbol", "Current Price (USD)", "Market Cap", "24h Volume", "24h Price Change (%)"]
    df = pd.DataFrame(crypto_list, columns=columns)
    
    return df

# Function to identify the top 5 cryptocurrencies by market cap
def top_5_cryptos(df):
    return df.nlargest(5, "Market Cap")

# Function to calculate the average price of the top 50 cryptocurrencies
def average_price(df):
    return df["Current Price (USD)"].mean()

# Function to analyze the highest and lowest 24-hour percentage price change
def price_change_analysis(df):
    highest_change = df.loc[df["24h Price Change (%)"].idxmax()]
    lowest_change = df.loc[df["24h Price Change (%)"].idxmin()]
    return highest_change, lowest_change

# Function to write data to an Excel file with a timestamp
def write_to_excel(df):
    if df.empty:
        print("No data to write to Excel.")
        return
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"Live_Crypto_Data.xlsx"  
    df.to_excel(file_name, index=False)
    print(f"Updated data written to {file_name}")

# Main function to fetch, process, analyze, and write data
def update_live_data():
    print("\nFetching latest cryptocurrency data...")
    data = fetch_crypto_data()
    df = process_crypto_data(data)

    if df.empty:
        print("Skipping update due to missing data.")
        return

    # Perform analysis
    top_5 = top_5_cryptos(df)
    avg_price = average_price(df)
    highest_change, lowest_change = price_change_analysis(df)

    # Print key insights
    print("\nTop 5 Cryptos by Market Cap:\n", top_5)
    print("\nAverage Price of Top 50 Cryptos: $", round(avg_price, 2))
    print("\nHighest 24h Change:\n", highest_change)
    print("\nLowest 24h Change:\n", lowest_change)

    # Write to Excel
    write_to_excel(df)

# Run the script 
update_live_data()

# Schedule the task to run every 5 minutes
schedule.every(5).minutes.do(update_live_data)

print("\n Starting live crypto data update... Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(1)
