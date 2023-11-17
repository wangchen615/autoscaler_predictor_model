# This is a sample Python script.


# Press ⇧F10 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime

SAMPLING_INTERVAL = 15  # in minutes
MAX_CPU = 200 # in vCPU cores
MIN_CPU = 50 # in vCPU cores
CPU_VAR = 40
MAX_MEM = 200 # in GB
MIN_MEM = 20 # in GB
MEM_VAR = 10
MAX_REQUESTS = 1000  # in requests per second
MIN_REQUESTS = 50    # in requests per second
REQUESTS_VAR = 10

PEAK_HOUR = 10  # 10:00 AM


def utilization_pattern(time, peak_time, min_val, max_val, variation):
    # Convert time to minutes since midnight
    minutes_since_midnight = time.hour * 60 + time.minute
    # Sine wave pattern
    value = np.sin(2 * np.pi * (minutes_since_midnight - peak_time) / 1440)
    # Scale to min and max values
    value = min_val + (max_val - min_val) * (value + 1) / 2
    # Add random variation
    value += np.random.uniform(-variation, variation)
    return int(max(min_val, min(max_val, value)))

#  python script that generates a periodic CPU/Memory utilization values for 4 weeks.
#  The data is sampled every 15 minutes starting from 0:00 am.
#  The CPU and Memory usage always peaks at 10:00 am every day on weekdays and drops to the bottom around 00:00 am at midnight.
#  On weekends, the peak hours are around 20:00 pm and drops at the bottom at 6:00 am.
#  The maximum CPU usage is around 200 vCPU cores and the maximum memory usage is about 200 GB.
#  The minimum CPU usage can drop to 20 vCPU cores and the minimum memory usage can drop to 20 GB.
#  The diurnal and weekly patterns are significant with very small variations across a particular time in a day.
#  The variations are within 10 vCPUs and 10 GB memory.
def synthesize_data(num_weeks, type='resource'):
    # Constants
    period = num_weeks * 7 * 24 * 60  # 4 weeks in minutes

    # Time range
    timestamps = pd.date_range(start="00:00", periods=period // SAMPLING_INTERVAL, freq=f"{SAMPLING_INTERVAL}min")

    # Generate utilization data
    if type == 'resource':
        cpu_usage = []
        mem_usage = []
    else:
        requests_ts = []

    for time in timestamps:
        if type == 'resource':
            cpu = utilization_pattern(time, PEAK_HOUR * 60, MIN_CPU, MAX_CPU, CPU_VAR)  # Peak at 10:00 AM
            mem = utilization_pattern(time, PEAK_HOUR * 60, MIN_MEM, MAX_MEM, MEM_VAR)
            cpu_usage.append(cpu)
            mem_usage.append(mem)
        else:
            requests = utilization_pattern(time, PEAK_HOUR * 60, MIN_REQUESTS, MAX_REQUESTS, REQUESTS_VAR)
            requests_ts.append(requests)

    # Create DataFrame
    if type == 'resource':
        ts_df = pd.DataFrame({'timestamp': timestamps, 'cpu': cpu_usage, 'memory': mem_usage})
    else:
        ts_df = pd.DataFrame({'timestamp': timestamps, 'requests': requests_ts})

    ts_df.set_index('timestamp', inplace=True)
    return ts_df

def plot_synthesized_data(df, type='resource'):
    # Plot sample data
    plt.figure(figsize=(15, 5))

    if type == 'resource':
        plt.plot(df.index, df.cpu, label='CPU Usage (vCPU cores)')
        plt.plot(df.index, df.memory, label='Memory Usage (GB)')
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        plt.title('Sample Resource Utilization')
    else:
        plt.plot(df.index, df.requests, label='Requests (per second)')
        plt.xlabel('Time')
        plt.ylabel('Requests')
        plt.title('Sample Requests')
    plt.legend()


    # Save plot & data
    current_time_string = datetime.now().strftime("%y-%m-%d-%H-%M")

    plt.savefig('./imgs/{}-{}.png'.format(type, current_time_string))
    plt.savefig('./imgs/{}-{}.pdf'.format(type, current_time_string))

    df.to_csv('./data/{}-{}.csv'.format(type, current_time_string))

    plt.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    rsc_df = synthesize_data(4, 'resource')
    plot_synthesized_data(rsc_df, 'resource')

    req_df = synthesize_data(1, 'requests')
    plot_synthesized_data(req_df, 'requests')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
