import datetime
import os
import math

import pandas as pd 
from pandas import DataFrame, Series
import matplotlib.pyplot as plt

def plot_requests_per_second(df: DataFrame, thresholds: list) -> None:

    # Ensure 'date' is in datetime format and set as the index
    df['date'] = pd.to_datetime(df['date'])

    datetime_min = df["date"].min().round('h')
    datetime_max = df["date"].max().round('h')

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
    plt.title('Number of Requests per Second in a DDoS Attack', fontsize=20, weight='bold')
    plt.xlabel('Time (Resampled Every 1 Second)', fontsize=20, weight='bold')
    plt.ylabel('Number of Requests', fontsize=20, weight='bold')

    # Set Y-limit
    if thresholds:
        max_value = max(requests_per_second['ip'].max(), max(thresholds)+5)
    else:
        max_value = requests_per_second['ip'].max()
    max_value = math.ceil(max_value / 5) * 5
    plt.ylim(0, max_value)

    if max_value < 10:
        step_size = 1
    else:
        step_size = 5

    # Set Ticks
    xticks = pd.date_range(datetime_min, datetime_max, freq='h')
    plt.xticks(xticks, [xtick.strftime('%H:%M %p') for xtick in xticks], fontsize=15, rotation=0)    
    yticks = range(0, max_value+1, step_size)
    plt.yticks(yticks, fontsize=15)


    plt.grid(True)
    plt.tight_layout()

def plot_avg_request_rate_per_client(df: pd.DataFrame) -> None:

    # Ensure 'date' is in datetime format and set as the index
    df['date'] = pd.to_datetime(df['date'])

    datetime_min = df["date"].min().round('h')
    datetime_max = df["date"].max().round('h')

    df.set_index('date', inplace=True)
    
    # Resample to count requests per time period per minute for each IP
    request_counts = df.groupby('ip').resample('1min').count()['path']
    
    # Now calculate the mean of these counts across all IPs for each time period
    mean_requests_per_client = request_counts.groupby(level=1).mean()  # Level 1 is the resampled time index

    # Reset index
    df.reset_index(inplace=True)

    # Plot the mean requests per client sampled every 1 minute
    plt.figure(figsize=(10, 6))
    mean_requests_per_client.plot()
    plt.title('Average Request Rate per Client per 1 Minute', fontsize=20, weight='bold')
    plt.xlabel('Time (Resampled Every 1 Minute)', fontsize=20, weight='bold')
    plt.ylabel('Average Requests per Client', fontsize=20, weight='bold')

     # Set Y-limit
    max_value = mean_requests_per_client.max()
    max_value = math.ceil(max_value / 5) * 5
    plt.ylim(0, max_value)

    if max_value <= 10:
        step_size = 1
    else:
        step_size = 5

    # Set Ticks
    xticks = pd.date_range(datetime_min, datetime_max, freq='h')
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
        print(f"Flash crowd at or above {threshold} requests/second detected at {first_timestamp}")
        return first_timestamp
    else:
        print(f"Flash crowd at or above {threshold} requests/second was not detected")
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

    print(f"The maximum requests per second in the flash crowd is {max_requests}")
    return max_requests

def find_timestamp_above_threshold_updated(df: DataFrame, timestamp_column: str, threshold: float) -> datetime.datetime:
    # Ensure 'date' column is in datetime format and set it as the index
    df[timestamp_column] = pd.to_datetime(df[timestamp_column])
    df.set_index(timestamp_column, inplace=True)
    
    # Resample to count requests per time period per minute for each IP
    request_counts = df.groupby('ip').resample('1min').count()['path']
    
    # Calculate the mean of these counts across all IPs for each time period
    mean_requests_per_client = request_counts.groupby(level=1).mean()  # Level 1 is the resampled time index
    
    # Find the first time when the mean requests per client per minute exceed the threshold
    above_threshold = mean_requests_per_client[mean_requests_per_client > threshold]
    
    # Reset index
    df.reset_index(inplace=True)

    if not above_threshold.empty:
        # Get the first timestamp where the mean exceeds the threshold
        first_timestamp = above_threshold.index[0]
        print(f"DDoS attack at or above {threshold} requests/client detected at {first_timestamp}")
        return first_timestamp
    else:
        print(f"Flash crowd or DDoS attack not detected at {threshold} requests/client. Use the original script to detect flash crowds")
        return None

def main():
    # Set directories
    current_directory = os.path.dirname(os.path.abspath(__file__))
    flash_crowd_directory = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'flash_crowd')

    # Set thresholds
    requests_per_client_threshold = 10
    detection_threshold = 50
    denial_of_service_threshold = 60

    # Read CSV(s) and convert to DataFrames
    ddos_df = pd.read_csv(os.path.join(current_directory, 'ddos.csv'))
    flash_crowd_df = pd.read_csv(os.path.join(flash_crowd_directory, 'flash_crowd.csv'))

    # Calculate max requests per second 
    max_requests = get_max_requests_per_second(ddos_df)
    # print(f"The maximum requests per second in the DDoS attack is {max_requests}")

    # Calculate when flash crowd is detected, but using DDoS Data.
    print("Running flash crowd detection algorithm but with DDoS data.")
    timestamp = find_timestamp_above_threshold(ddos_df, 'date', detection_threshold)
    print("DDoS attack was detected as a flash crowd")
    # print(f"Flash crowd (but using DDoS data) at or above {detection_threshold} requests/second detected at {timestamp}")

    # Plot DDoS attack
    plot_requests_per_second(ddos_df,[detection_threshold,denial_of_service_threshold])
    plt.savefig(os.path.join(current_directory, 'ddos.png'))

    # Plot DDoS requests per client
    plot_avg_request_rate_per_client(ddos_df)
    plt.savefig(os.path.join(current_directory, 'ddos_client.png'))

    # Plot flash crowd requests per client
    plot_avg_request_rate_per_client(flash_crowd_df)
    plt.savefig(os.path.join(current_directory, 'flash_crowd_client.png'))

    # Calculate when DDoS is detected
    timestamp = find_timestamp_above_threshold_updated(ddos_df, 'date', requests_per_client_threshold)
    # print(f"DDoS attack above an average of {requests_per_client_threshold} requests/client every minute detected at {timestamp}")

    # Calculate when flash crowd is detected
    timestamp = find_timestamp_above_threshold_updated(flash_crowd_df, 'date', requests_per_client_threshold)
    # print(f"Flash crowd above an average of {requests_per_client_threshold} requests/client every minute detected at {timestamp}")

main()