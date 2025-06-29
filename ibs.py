import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def download_historical_data(ticker, start_date, end_date):
    """
    Download historical price data for a given ticker
    
    Parameters:
    - ticker: Stock symbol (e.g., 'AAPL')
    - start_date: Start date for historical data (format: 'YYYY-MM-DD')
    - end_date: End date for historical data (format: 'YYYY-MM-DD')
    
    Returns:
    - pandas DataFrame with historical price data
    """
    try:
        # Download historical data
        data = yf.download(ticker, start=start_date, end=end_date)
        
        # Select only the columns we need
        data = data[['Open', 'High', 'Low', 'Close']]
        
        return data
    except Exception as e:
        print(f"Error downloading data: {e}")
        return None

def calculate_ibs(data):
    """
    Calculate Internal Bar Strength (IBS) for each day
    
    IBS = (Close - Low) / (High - Low)
    
    Parameters:
    - data: DataFrame with OHLC prices
    
    Returns:
    - pandas Series with IBS values
    """
    # Avoid division by zero
    data['IBS'] = np.where(
        (data['High'] - data['Low']) != 0,
        (data['Close'] - data['Low']) / (data['High'] - data['Low']),
        0
    )
    
    return data['IBS']

def backtest_strategy(data, ibs_threshold_buy=0.2, ibs_threshold_sell=0.8):
    """
    Backtest a trading strategy based on IBS
    
    Parameters:
    - data: DataFrame with price and IBS data
    - ibs_threshold_buy: Lower IBS threshold for buying
    - ibs_threshold_sell: Upper IBS threshold for selling
    
    Returns:
    - DataFrame with strategy signals and returns
    """
    # Copy the original data to avoid modifying the input
    strategy_data = data.copy()
    
    # Generate buy and sell signals based on IBS
    strategy_data['Buy_Signal'] = (strategy_data['IBS'] <= ibs_threshold_buy).astype(int)
    strategy_data['Sell_Signal'] = (strategy_data['IBS'] >= ibs_threshold_sell).astype(int)
    
    # Calculate daily returns
    strategy_data['Daily_Return'] = strategy_data['Close'].pct_change()
    
    # Calculate strategy returns
    strategy_data['Strategy_Return'] = np.where(
        strategy_data['Buy_Signal'] == 1,  # When buy signal is triggered
        strategy_data['Daily_Return'],
        0
    )
    
    return strategy_data

def plot_strategy_performance(strategy_data):
    """
    Plot cumulative returns of the strategy
    
    Parameters:
    - strategy_data: DataFrame with strategy returns
    """
    # Calculate cumulative returns
    strategy_data['Cumulative_Market_Return'] = (1 + strategy_data['Daily_Return']).cumprod() - 1
    strategy_data['Cumulative_Strategy_Return'] = (1 + strategy_data['Strategy_Return']).cumprod() - 1
    
    # Plot cumulative returns
    plt.figure(figsize=(12, 6))
    plt.plot(strategy_data.index, strategy_data['Cumulative_Market_Return'], label='Market Return')
    plt.plot(strategy_data.index, strategy_data['Cumulative_Strategy_Return'], label='Strategy Return')
    plt.title('Strategy Performance: IBS Trading')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.legend()
    plt.show()

def main():
    # Configuration
    ticker = 'AAPL'  # Example: Apple Inc.
    start_date = '2014-01-01'
    end_date = '2024-01-01'
    
    # Download historical data
    data = download_historical_data(ticker, start_date, end_date)
    
    if data is not None:
        # Calculate IBS
        data['IBS'] = calculate_ibs(data)
        
        # Backtest strategy
        strategy_data = backtest_strategy(data)
        
        # Plot performance
        plot_strategy_performance(strategy_data)
        
        # Print summary statistics
        print("\nStrategy Summary:")
        print(f"Total Strategy Return: {strategy_data['Strategy_Return'].sum():.2%}")
        print(f"Number of Buy Signals: {strategy_data['Buy_Signal'].sum()}")
        print(f"Number of Sell Signals: {strategy_data['Sell_Signal'].sum()}")

if __name__ == "__main__":
    main()
