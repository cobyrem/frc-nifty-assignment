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
    plt.title('Number of Requests per Second in an FRC Attack', fontsize=20, weight='bold')
    plt.xlabel('Time (Resampled Every 1 Second)', fontsize=20, weight='bold')
    plt.ylabel('Number of Requests', fontsize=20, weight='bold')

    # Set Y-limit
    if thresholds:
        max_value = max(requests_per_second['ip'].max(), max(thresholds)+5)
    else:
        max_value = requests_per_second['ip'].max()
    max_value = (math.ceil(max_value / 5) * 5) + 5
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

def calculate_attack_cost(cost_per_gb=0.09, requests_per_second=5, request_size=0.000015, duration=60*60*24*30):
    # Calculate the total amount of data transferred
    total_data_transferred = requests_per_second * request_size * duration
    
    # Calculate the total cost
    total_cost = total_data_transferred * cost_per_gb
    
    # Return the rounded total cost
    return f"{total_cost:.2f}"

def main():
    # Set directories
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Set thresholds
    nuissance_activity_threshold = 10
    detection_threshold = 50

    # Calculate max requests per second 
    df = pd.read_csv(os.path.join(current_directory, 'frc.csv'))
    max_requests = get_max_requests_per_second(df)

    # Plot FRC attack
    plot_requests_per_second(df,[nuissance_activity_threshold,detection_threshold])
    plt.savefig(os.path.join(current_directory, 'frc.png'))

    # Baseline scenario
    baseline_cost = calculate_attack_cost(requests_per_second=5)
    print(f"Baseline Scenario Cost: ${baseline_cost}")

    # FRC Attack Scenario 1 (High intensity)
    attack_scenario_1_cost = calculate_attack_cost(requests_per_second=45)
    print(f"FRC Attack Scenario 1 Cost: ${attack_scenario_1_cost}")

    # FRC Attack Scenario 2 (Low intensity, longer duration)
    attack_scenario_2_cost = calculate_attack_cost(duration=60*60*24*90, requests_per_second=15)
    print(f"FRC Attack Scenario 2 Cost: ${attack_scenario_2_cost}")

main()



