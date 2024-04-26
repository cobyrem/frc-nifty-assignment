import re
import argparse
import random
import datetime
import gzip
import math
import os


from faker import Faker
fake = Faker()
import pandas as pd 
from pandas import DataFrame, Series
import matplotlib.pyplot as plt
import numpy as np

def parse_file(filename: str) -> DataFrame:
    # Regex to parse log file
    line_regex = r'(?P<ip>.*?) (?P<remote_log_name>.*?) (?P<userid>.*?) \[(?P<date>.*?)(?= ) (?P<timezone>.*?)\] \"(?P<request_method>.*?) (?P<path>.*?)(?P<request_version> HTTP/.*)?\" (?P<status>.*?) (?P<length>.*?)'
    # Compile the regex for reuse
    line_object = re.compile(line_regex)
    # Create a dictionary to hold lists of data
    data_dict = {
        "ip": [],
        "date": [],
        "method": [],
        "path": [],
        "status": [],
        "length": []
    }
    # Read in the file and add data to the dictionary
    with gzip.open(filename, 'rt', encoding='latin1') as log_file: 
        line_no = 0
        for line in log_file:
            try:
                line_no += 1
                line_data = line_object.match(str(line))
                # print(line_data)
                # print(type(line_data))
                data_dict['ip'].append(line_data.group('ip'))
                data_dict['date'].append(line_data.group('date'))
                data_dict['method'].append(line_data.group('request_method'))
                data_dict['path'].append(line_data.group('path'))
                data_dict['status'].append(line_data.group('status'))
                data_dict['length'].append(line_data.group('length'))
            except AttributeError:
                print (line_no)       
    # Create a DataFrame from the dictionary
    df = pd.DataFrame(data_dict)
    df['date'] = pd.to_datetime(df['date'], format='%d/%b/%Y:%H:%M:%S')

    # Drop the method, status, and length columns
    df.drop(['method', 'status', 'length'], axis=1, inplace=True)

    # Replace any instances of 1995 with 2023
    df['date'] = df['date'].apply(lambda dt: dt.replace(year=2023))
    df['path'] = df['path'].str.replace('1995', '2023')

    return df

def get_unique_paths(df: DataFrame, column_name: str) -> list:
    return list(df[column_name].unique())

# Generate pool of random ips/sources
def generate_fake_ips(size: int):
    ips = []
    for _ in range(size):
        source_type = random.randint(1,2)
        if source_type == 1:
            ips.append(fake.ipv4())
        elif source_type == 2:
            # 1 or 2 levels in domain name
            ips.append(fake.domain_name(random.randint(1,3)))
    return ips

# Generate fake dict
# Path percentage: percentage of unique paths to choose from
def generate_fake_data_dict(ip_pool, unique_paths: list, timestamp: datetime, iterations: int, path_percentage: int = 100) -> DataFrame:
    
    fake_data_df = pd.DataFrame(columns=["ip", "date", "path"])
    
    for iteration in range(iterations):
        fake_source = ip_pool[random.randint(0, len(ip_pool) - 1)]
        fake_timestamp = timestamp.strftime('%d/%b/%Y:%H:%M:%S')
        num_paths = max(math.floor((path_percentage/100) * len(unique_paths)),1)
        path = unique_paths[random.randint(0, num_paths - 1)]
        
        fake_data_df = fake_data_df._append({
            "ip": fake_source,
            "date": fake_timestamp,
            "path": path
        }, ignore_index=True)
        
    return fake_data_df

def calculate_exponential_change(sec: int, N_0: int, max_value: int, duration: int, is_decay: bool):
    if is_decay:
        # Exponential decay formula
        num_reqs = max_value * np.exp(-np.log(max_value / N_0) * (sec / duration))
    else:
        # Exponential growth formula
        num_reqs = N_0 * np.exp(np.log(max_value / N_0) * (sec / duration))
    
    # Add a bit more randomness to the number of requests
    return math.floor(num_reqs) if random.choice([True, False]) else math.ceil(num_reqs)

def generate_flash_crowd_data(data_dict: DataFrame, unique_paths: list, start_time: datetime, end_time: datetime, N_0: int, max_value: int, cap_time_percentage: float) -> DataFrame:
    
    # Calculate durations
    duration = (end_time - start_time).total_seconds()
    cap_time_seconds = int(duration * cap_time_percentage)
    ramp_up_duration = cap_time_seconds
    wind_down_duration = duration - ramp_up_duration

    # Set up
    ips = generate_fake_ips(50000)  # Assuming generate_fake_ips is defined elsewhere
    fake_data_df = pd.DataFrame(columns=["ip", "date", "path"])
    
    # Ramp up period
    for sec in range(int(ramp_up_duration)):
        start_time = start_time + datetime.timedelta(seconds=1)
        num_reqs = calculate_exponential_change(sec, N_0, max_value, ramp_up_duration, False)
        data_dict = generate_fake_data_dict(ips, unique_paths, start_time, math.floor(num_reqs + random.randint(-3,1)))
        fake_data_df = fake_data_df._append(data_dict, ignore_index=True)
    
    # Wind down period
    for sec in range(int(wind_down_duration)):
        start_time = start_time + datetime.timedelta(seconds=1)
        num_reqs = calculate_exponential_change(sec, N_0, max_value, wind_down_duration, True)
        data_dict = generate_fake_data_dict(ips, unique_paths, start_time, math.floor(num_reqs + random.randint(-3,1)))
        fake_data_df = fake_data_df._append(data_dict, ignore_index=True)


    fake_data_df['date'] = pd.to_datetime(fake_data_df['date'], format='%d/%b/%Y:%H:%M:%S')
    return fake_data_df
   
def generate_flash_crowd(log_filename: str, data_start_datetime: str, data_end_datetime: str, 
                          flash_start_datetime: str, flash_end_datetime: str, N_0: int, max_value: int, 
                          cap_time_percentage: float, csv_filename: str) -> None:

    # Parse the log file
    nasa_df = parse_file(log_filename)

    # Use unique paths for resampling data
    unique_paths = get_unique_paths(nasa_df, 'path')
    
    # Convert string dates to datetime objects for the flash crowd event
    flash_start_date = datetime.datetime.strptime(flash_start_datetime, '%Y-%m-%d %H:%M:%S')
    flash_end_date = datetime.datetime.strptime(flash_end_datetime, '%Y-%m-%d %H:%M:%S')

    # Generate flash crowd data using the new parameters
    flash_df = generate_flash_crowd_data(nasa_df, unique_paths, flash_start_date, 
                                         flash_end_date, N_0, max_value, 
                                         cap_time_percentage)

    # Convert strings to datetime for the original data range
    data_start_date = pd.to_datetime(data_start_datetime)
    data_end_date = pd.to_datetime(data_end_datetime)
    
    # Set 'date' as the index for the original DataFrame for filtering
    nasa_df.set_index('date', inplace=True)

    # Filter the DataFrame for the original data
    filtered_df = nasa_df.loc[data_start_date:data_end_date]

    # Set 'date' as the index for the flash crowd DataFrame for sorting
    flash_df.set_index('date', inplace=True)
    
    # Concatenate and sort the original and flash crowd data
    combined_flash_df = pd.concat([filtered_df, flash_df])
    final_flash_df = combined_flash_df.sort_values(by='date')
    
    # Reset index to bring 'date' back as a column
    final_flash_df.reset_index(inplace=True)
    
    # Define column order
    column_order = ['ip', 'path', 'date']
    
    # Save to CSV without index and with specified column order
    final_flash_df.to_csv(csv_filename, index=False, columns=column_order)

def generate_ddos_data(data_dict: DataFrame, unique_paths: list, start_time: datetime, end_time: datetime, N_0: int, max_value: int, cap_time_percentage: float) -> DataFrame:
    
    # Calculate durations
    duration_seconds = (end_time - start_time).total_seconds()
    plateau_duration = int(duration_seconds * cap_time_percentage)
    ramp_up_and_wind_down_duration = int(duration_seconds - plateau_duration)
    ramp_up_duration = ramp_up_and_wind_down_duration // 2
    wind_down_duration = ramp_up_and_wind_down_duration - ramp_up_duration

    # Set up
    ips = generate_fake_ips(50)  # Assuming generate_fake_ips is defined elsewhere
    fake_data_df = pd.DataFrame(columns=["ip", "date", "path"])
    
    # Ramp up period
    for sec in range(int(ramp_up_duration)):
        start_time = start_time + datetime.timedelta(seconds=1)
        num_reqs = calculate_exponential_change(sec, N_0, max_value, ramp_up_duration, False)
        data_dict = generate_fake_data_dict(ips, unique_paths, start_time, math.floor(num_reqs + random.randint(-3,1)))
        fake_data_df = fake_data_df._append(data_dict, ignore_index=True)
    
    # Plateau period
    for sec in range(int(plateau_duration)):
        start_time = start_time + datetime.timedelta(seconds=1)
        # num_reqs = calculate_exponential_change(sec, N_0, max_value, plateau_duration, True)  # Assuming it remains constant during the plateau
        num_reqs = 55
        data_dict = generate_fake_data_dict(ips, unique_paths, start_time, math.floor(num_reqs + random.randint(-7,2)))
        fake_data_df = fake_data_df._append(data_dict, ignore_index=True)

    # Wind down period
    for sec in range(int(wind_down_duration)):
        start_time = start_time + datetime.timedelta(seconds=1)
        num_reqs = calculate_exponential_change(sec, N_0, max_value, wind_down_duration, True)
        data_dict = generate_fake_data_dict(ips, unique_paths, start_time, math.floor(num_reqs + random.randint(-3,1)))
        fake_data_df = fake_data_df._append(data_dict, ignore_index=True)


    fake_data_df['date'] = pd.to_datetime(fake_data_df['date'], format='%d/%b/%Y:%H:%M:%S')
    return fake_data_df
   
def generate_ddos(log_filename: str, data_start_datetime: str, data_end_datetime: str, 
                          ddos_start_datetime: str, ddos_end_datetime: str, N_0: int, max_value: int, 
                          cap_time_percentage: float, csv_filename: str) -> None:
    # Parse the log file
    nasa_df = parse_file(log_filename)

    # Use unique paths for resampling data
    unique_paths = get_unique_paths(nasa_df, 'path')
    
    # Convert string dates to datetime objects for the ddos attack
    ddos_start_date = datetime.datetime.strptime(ddos_start_datetime, '%Y-%m-%d %H:%M:%S')
    ddos_end_date = datetime.datetime.strptime(ddos_end_datetime, '%Y-%m-%d %H:%M:%S')

    # Generate ddos data using the new parameters
    ddos_df = generate_ddos_data(nasa_df, unique_paths, ddos_start_date, 
                                         ddos_end_date, N_0, max_value, 
                                         cap_time_percentage)

    # Convert strings to datetime for the original data range
    data_start_date = pd.to_datetime(data_start_datetime)
    data_end_date = pd.to_datetime(data_end_datetime)
    
    # Set 'date' as the index for the original DataFrame for filtering
    nasa_df.set_index('date', inplace=True)

    # Filter the DataFrame for the original data
    filtered_df = nasa_df.loc[data_start_date:data_end_date]

    # Set 'date' as the index for the ddos attack DataFrame for sorting
    ddos_df.set_index('date', inplace=True)
    
    # Concatenate and sort the original and ddos data
    combined_ddos_df = pd.concat([filtered_df, ddos_df])
    final_ddos_df = combined_ddos_df.sort_values(by='date')
    
    # Reset index to bring 'date' back as a column
    final_ddos_df.reset_index(inplace=True)
    
    # Define column order
    column_order = ['ip', 'path', 'date']
    
    # Save to CSV without index and with specified column order
    final_ddos_df.to_csv(csv_filename, index=False, columns=column_order)


def generate_frc_data(data_dict: DataFrame, unique_paths: list, start_time: datetime, end_time: datetime) -> DataFrame:
    
    # Calculate durations
    duration_seconds = (end_time - start_time).total_seconds()

    # Set up
    ips = generate_fake_ips(50)  # Assuming generate_fake_ips is defined elsewhere
    fake_data_df = pd.DataFrame(columns=["ip", "date", "path"])
    
    # Plateau period
    for _ in range(int(duration_seconds)):
        start_time = start_time + datetime.timedelta(seconds=1)
        num_reqs = 20
        data_dict = generate_fake_data_dict(ips, unique_paths, start_time, math.floor(num_reqs + random.randint(-7,2)),50)
        fake_data_df = fake_data_df._append(data_dict, ignore_index=True)


    fake_data_df['date'] = pd.to_datetime(fake_data_df['date'], format='%d/%b/%Y:%H:%M:%S')
    return fake_data_df

def generate_frc(log_filename: str, data_start_datetime: str, data_end_datetime: str, csv_filename: str) -> None:
    # Parse the log file
    nasa_df = parse_file(log_filename)

    # Use unique paths for resampling data
    unique_paths = get_unique_paths(nasa_df, 'path')
    
    # Convert string dates to datetime objects for the ddos attack
    data_start_date = pd.to_datetime(data_start_datetime)
    data_end_date = pd.to_datetime(data_end_datetime)

    # Generate frc data using the new parameters
    frc_df = generate_frc_data(nasa_df, unique_paths, data_start_date, data_end_date)
    
    # Set 'date' as the index for the original DataFrame for filtering
    nasa_df.set_index('date', inplace=True)

    # Filter the DataFrame for the original data
    filtered_df = nasa_df.loc[data_start_date:data_end_date]

    # Set 'date' as the index for the frc DataFrame for sorting
    frc_df.set_index('date', inplace=True)
    
    # Concatenate and sort the original and ddos data
    combined_frc_df = pd.concat([filtered_df, frc_df])
    final_frc_df = combined_frc_df.sort_values(by='date')
    
    # Reset index to bring 'date' back as a column
    final_frc_df.reset_index(inplace=True)
    
    # Define column order
    column_order = ['ip', 'path', 'date']
    
    # Save to CSV without index and with specified column order
    final_frc_df.to_csv(csv_filename, index=False, columns=column_order)

def generate_baseline(log_filename: str, data_start_datetime: str, data_end_datetime: str, csv_filename: str) -> None:
    # Parse the log file
    nasa_df = parse_file(log_filename)
    
    # Convert string dates to datetime objects for the ddos attack
    data_start_date = pd.to_datetime(data_start_datetime)
    data_end_date = pd.to_datetime(data_end_datetime)
    
    # Set 'date' as the index for the original DataFrame for filtering
    nasa_df.set_index('date', inplace=True)

    # Filter the DataFrame for the original data
    final_baseline_df = nasa_df.loc[data_start_date:data_end_date]
    
    # Reset index to bring 'date' back as a column
    final_baseline_df.reset_index(inplace=True)
    
    # Define column order
    column_order = ['ip', 'path', 'date']
    
    # Save to CSV without index and with specified column order
    final_baseline_df.to_csv(csv_filename, index=False, columns=column_order)

def main():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    generate_baseline(
        log_filename="NASA_access_log_Jul95.gz",
        data_start_datetime='2023-07-01 00:00:00',
        data_end_datetime='2023-07-01 23:59:59',
        csv_filename= os.path.join(current_directory,"baseline/baseline.csv")
    )

    generate_flash_crowd(
        log_filename="NASA_access_log_Jul95.gz",
        data_start_datetime='2023-07-03 06:00:00',
        data_end_datetime='2023-07-03 12:00:00',
        flash_start_datetime='2023-07-03 06:30:00',
        flash_end_datetime='2023-07-03 11:30:00',  # Example end time based on a hypothetical duration
        N_0=1,
        max_value=60,
        cap_time_percentage=0.80,  # 80% of the event duration is for the rise phase
        csv_filename= os.path.join(current_directory,"flash_crowd/flash_crowd.csv")
    )

    generate_ddos(
        log_filename="NASA_access_log_Jul95.gz",
        data_start_datetime='2023-07-10 06:00:00',
        data_end_datetime='2023-07-10 12:00:00',
        ddos_start_datetime='2023-07-10 06:30:00',
        ddos_end_datetime='2023-07-10 11:30:00',  # Example end time based on a hypothetical duration
        N_0=1,
        max_value=55,
        cap_time_percentage=0.90,  # 90% of the event duration is for the plateau phase
        csv_filename= os.path.join(current_directory,"ddos/ddos.csv")
    )

    generate_frc(
        log_filename="NASA_access_log_Jul95.gz",
        data_start_datetime='2023-07-15 06:00:00',
        data_end_datetime='2023-07-15 12:00:00',
        csv_filename= os.path.join(current_directory,"frc/frc.csv")
    )

main()
