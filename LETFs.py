import os
import tkinter as tk
from tkinter import messagebox
from tabulate import tabulate
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest
import time
import requests

# Global variable for trading client
trading_client = None

# Check if connected to a whitelisted Wi-Fi network (Windows)
def is_whitelisted_network(whitelisted_networks=['Network 1', 'Network 2']):
    try:
        result = os.popen('netsh wlan show interfaces').read().strip()
        for line in result.split('\n'):
            if "SSID" in line:
                ssid = line.split(':')[1].strip()
                return ssid in whitelisted_networks
        return False
    except Exception as e:
        print(f"Error checking network: {e}")
        return False

# Define the leveraged ETFs to check
leveraged_etfs = {
    "TQQQ": "ProShares UltraPro QQQ",
    "SOXL": "Direxion Daily Semiconductor Bull 3X Shares",
    "USD": "ProShares Ultra Semiconductors",
    "TECL": "Direxion Daily Technology Bull 3X Shares",
    "FNGU": "MicroSectors FANG Index 3X Leveraged ETNs",
    "BULZ": "MicroSectors FANG & Innovation 3x Leveraged ETN",
    "NVDL": "GraniteShares 2x Long NVDA Daily ETF",
    "FNGO": "MicroSectors FANG Index 2X Leveraged ETNs",
}

def us_market_fees(quantity, price):
    commission = max(0.0049 * quantity, 0.99)
    platform_fee = max(0.005 * quantity, 1)
    settlement_fee = quantity * 0.003
    regulatory_fee = max(0.0000221 * (quantity * price), 0.01)
    trading_activity_fee = max(0.000166 * quantity, 0.01)
    fees = commission + platform_fee + settlement_fee + regulatory_fee + trading_activity_fee
    transaction_amount = quantity * price
    return fees, transaction_amount

def predict_future_price(current_price):
    return current_price * 1.01  # Assuming a 1% increase

def get_real_time_prices(api_key, secret_key, symbols):
    data_client = StockHistoricalDataClient(api_key, secret_key)
    request_params = StockLatestQuoteRequest(symbol_or_symbols=symbols)
    try:
        latest_quotes = data_client.get_stock_latest_quote(request_params)
        return {symbol: quote.ask_price for symbol, quote in latest_quotes.items()}
    except Exception as e:
        print(f"Error getting real-time prices: {e}")
        return {}

def get_invested_amount(trading_client, symbol):
    try:
        positions = trading_client.get_all_positions()
        for position in positions:
            if position.symbol == symbol:
                return float(position.market_value)
        return 0.0
    except Exception as e:
        print(f"Error getting invested amount for {symbol}: {e}")
        return 0.0

def close_positions(trading_client):
    try:
        positions = trading_client.get_all_positions()
        for position in positions:
            current_price = float(position.current_price)
            avg_entry_price = float(position.avg_entry_price)
            if current_price >= avg_entry_price * 1.01:
                order = MarketOrderRequest(
                    symbol=position.symbol,
                    qty=position.qty,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.GTC
                )
                trading_client.submit_order(order)
                print(f"Closed position for {position.symbol}")
    except Exception as e:
        print(f"Error closing positions: {e}")

def check_internet_connection():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False

def check_and_buy_etfs():
    global trading_client
    
    if not is_whitelisted_network():
        print("Not connected to a whitelisted network. Operation aborted.")
        return

    if not check_internet_connection():
        print("No internet connection. Operation aborted.")
        return

    api_key, secret_key = 'api-key', 'secret-key'
    trading_client = TradingClient(api_key, secret_key, paper=True)

    try:
        account = trading_client.get_account()
        if account.trading_blocked:
            print("Account is currently restricted from trading.")
            return

        portfolio_value = float(account.portfolio_value)

        buying_power = float(account.buying_power)
        if buying_power <= 0:
            print("Account balance is zero or negative. Cannot proceed with buying.")
            return

        num_etfs = len(leveraged_etfs)
        amount_per_etf = buying_power / num_etfs

        print(f"\nPortfolio Value: ${portfolio_value:.2f}")
        print(f"Buying Power: ${buying_power:.2f}")
        print(f"Allocated Amount per ETF: ${amount_per_etf:.2f}")

        symbols = list(leveraged_etfs.keys())
        real_time_prices = get_real_time_prices(api_key, secret_key, symbols)

        table_data = []

        for symbol in leveraged_etfs.keys():
            try:
                current_price = real_time_prices.get(symbol, None)
                if current_price is not None:
                    quantity = amount_per_etf / current_price
                    buy_fees, buy_transaction = us_market_fees(quantity, current_price)
                    future_price = predict_future_price(current_price)
                    sell_fees, sell_transaction = us_market_fees(quantity, future_price)
                    potential_profit = sell_transaction - sell_fees - (buy_transaction + buy_fees)

                    status = "Not Profitable"
                    invested_amount = get_invested_amount(trading_client, symbol)

                    if quantity < 1:
                        status = "Insufficient Funds"
                    elif potential_profit > 0:
                        order = MarketOrderRequest(
                            symbol=symbol,
                            qty=int(quantity),
                            side=OrderSide.BUY,
                            time_in_force=TimeInForce.GTC
                        )
                        trading_client.submit_order(order)
                        status = "Bought"
                        invested_amount = get_invested_amount(trading_client, symbol)

                    table_data.append([
                        symbol,
                        f"${current_price:.2f}",
                        f"${future_price:.2f}",
                        f"${potential_profit:.2f}",
                        f"${invested_amount:.2f}",
                        status
                    ])
                else:
                    table_data.append([
                        symbol,
                        "N/A",
                        "N/A",
                        "N/A",
                        f"${get_invested_amount(trading_client, symbol):.2f}",
                        "Price Unavailable"
                    ])
            except Exception as e:
                # print(f"Error processing {symbol}: {e}")
                table_data.append([
                    symbol,
                    "N/A",
                    "N/A",
                    "N/A",
                    f"${get_invested_amount(trading_client, symbol):.2f}",
                    f"Error: {str(e)}"
                ])

        headers = ["Symbol", "Current Price", "Predicted Price", "Potential Profit", "Invested Amount", "Status"]
        print("ETF Buying Results:")
        print(tabulate(table_data, headers, tablefmt="grid"))

    except Exception as e:
        print(f"An error occurred: {e}")

def start_automatic_check(interval_ms=60000):
    check_and_buy_etfs()
    close_positions(trading_client)
    root.after(interval_ms, start_automatic_check, interval_ms)

# Create the main window
root = tk.Tk()
root.title("Leveraged ETFs Buyer")
root.geometry("300x100")

# Create and pack the buttons
manual_buy_button = tk.Button(root, text="Manual Buy", command=check_and_buy_etfs)
manual_buy_button.pack(pady=10)

manual_close_button = tk.Button(root, text="Manual Close", command=lambda: close_positions(trading_client))
manual_close_button.pack(pady=10)

# Start the automatic check immediately
start_automatic_check()

# Start the GUI event loop
root.mainloop()