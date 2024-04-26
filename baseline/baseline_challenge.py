import datetime
import os
import math

import pandas as pd 
from pandas import DataFrame, Series
import matplotlib.pyplot as plt

def plot_requests_per_second(df: DataFrame, thresholds: list) -> None:

    datetime_min = df["date"].min().round('h')
    datetime_max = df["date"].max().round('h')

    # Ensure 'date' is in datetime format and set as the index
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    # Resample data to count the number of requests per second
    requests_per_second = df.resample('1s').count()

    # Reset index
    df.reset_index(inplace=True)

    # Plot the number of requests per second
    plt.figure(figsize=(10, 6))
    requests_per_second['ip'].plot()
    for threshold in thresholds:
       plt.axhline(y=threshold, color='r', linestyle='--', linewidth=3)
    plt.title('Number of Requests per Second in Baseline Traffic', fontsize=20, weight='bold')
    plt.xlabel('Time (Resampled Every 1 Second)', fontsize=20, weight='bold')
    plt.ylabel('Number of Requests', fontsize=20, weight='bold')

    # Set Y-limit
    if thresholds:
        max_value = max(requests_per_second['ip'].max(), max(thresholds)+5)
    else:
        max_value = requests_per_second['ip'].max()
    max_value = math.ceil(max_value / 5) * 5
    plt.ylim(0, max_value)

    if max_value <= 10:
        step_size = 1
    else:
        step_size = 5

    # Set Ticks
    xticks = pd.date_range(datetime_min, datetime_max, freq='3h')
    plt.xticks(xticks, [xtick.strftime('%H %p') for xtick in xticks], fontsize=15, rotation=0)    
    yticks = range(0, max_value+1, step_size)
    plt.yticks(yticks, fontsize=15)


    plt.grid(True)
    plt.tight_layout()

def find_timestamp_above_threshold(df: DataFrame, timestamp_column: str, threshold: int) -> datetime:
    # Convert 'date' column to datetime format
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
    
    # Set 'date' as the index
    df.set_index(timestamp_column, inplace=True)
    
    # Resample to one-second intervals and get the number of requests per second
    requests_per_second = df.resample('1s').size()

    # Get the timestamps where the number of requests per second is greater than the threshold
    above_threshold = requests_per_second[requests_per_second > threshold]

    #Reset index
    df.reset_index(inplace=True)

    # Get the first timestamp where the count exceeds the threshold
    if not above_threshold.empty:
        first_timestamp = above_threshold.index[0]
        return first_timestamp
    else:
        return None

def get_max_requests_per_second(df: DataFrame) -> int:
    # Ensure 'date' is in datetime format and set as the index
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Resample data to count the number of requests per second
    requests_per_second = df.resample('1s').count()

    # Reset index
    df.reset_index(inplace=True)
    
    # Get the maximum number of requests per second
    max_requests = requests_per_second['ip'].max()
    print(f"The maximum requests per second in baseline traffic is {max_requests}")
    return max_requests

def main():
    # Set directories
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Calculate max requests per second 
    df = pd.read_csv(os.path.join(current_directory, 'baseline.csv'))
    max_requests = get_max_requests_per_second(df)

    # Plot baseline
    plot_requests_per_second(df,[])
    plt.savefig(os.path.join(current_directory, 'baseline.png'),dpi=200, format='png', bbox_inches='tight')

main()



