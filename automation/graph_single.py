import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from parse_global_stats import global_tx_stats, get_pS_data

def get_data(vendor='Arista', test='multi_http_simple', folder='m101000'):
    
    stats_table = global_tx_stats(vendor, test, folder=folder)
    df = collect_agg_files(stats_table, folder=folder)
    return df

def describe_as_bar():
    df = get_data()['mean']

    df.describe().plot.bar()
    plt.show()

def line_plot(columns=['TxBw_port_0', 'TxBw_port_1', 'drop-rate']):
    df = get_data()['mean'][columns]
    df.plot()
    plt.show()



def bar_pS_data(vendor='Arista', test='pSControl_5May2020'):
    # pSControl
    # pS_Simult_sfr_May2020_13h51m
    # pS_Simult_with_trexhttp_6cores
    rows = ['mean', 'max']
    all_files = get_pS_data(vendor, test)

    # Aggregate pscheduler data
    agg_col_name = 'pScheduler Throughput (Gbps)'
    all_files[agg_col_name] = all_files['pS_throughput'].rolling(25).max()
    all_files = all_files.dropna()

    #agg_count = all_files['pS_throughput'].unique()
    #print(agg_count)

    # Calc P(observed_throughput | actual Throughput)
    
    agg_count = {}
    agg_count_total = 0
    agg_values = all_files[agg_col_name].values
    for i in range(len(agg_values)):
        if agg_values[i] not in agg_count:
            agg_count[agg_values[i]] = 1
        else:
            agg_count[agg_values[i]] += 1
        agg_count_total += 1

    expected_value = 0
    for num in agg_count:
        agg_count[num] /= agg_count_total
        expected_value += num * agg_count[num]

    print("Expected Value: " + agg_col_name +' '+ str(expected_value))

    prob_obs_given_thru = {'Probability of Throughput':agg_count}
    pd.DataFrame(prob_obs_given_thru).plot.bar()
    plt.title('Isolated pScheduler on Arista')
    plt.xlabel(agg_col_name)
    plt.show()
        
    

    display_ax = [agg_col_name]
    all_files = all_files[display_ax]

    
    df_desc = all_files.describe()
    print(df_desc)
    
    all_files.plot.bar()
    plt.title('Isolated pScheduler on Arista')
    plt.xlabel('Independent Test ID')
    plt.show()

def bar_combined_pS():
    pass
    
if __name__ == "__main__":
    #describe_as_bar()
    #line_plot()
    bar_pS_data()
    #bar_combined_pS()
    
