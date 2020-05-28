from analysis import get_data, title_stats
from parse_global_stats import global_tx_stats, mean_df

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.style.use('bmh')

'''
TODO
    Set a range for x&y axes
    add legend for error bars and data point markers

Optional
    combine graph of avg_latency and max_latency with filled color
    
Done
    add functional notations
    update process to access vendor data from root directory

    graph
        x = cpu_util (%)
        y = throughput
'''

def select_from(data, where=""):
    #return df.filter(like='where', axis=0)

    df = {'multiple':[]}# name of directories

    directories = list(data.keys())
    example = directories[0]
    
    for metric in data[example]:
            df[metric] = []

    
    for dir_name in directories:
        df['multiple'].append( int(dir_name[1:]) )
                               
        for metric in data[dir_name]:            
            df[metric].append(data[dir_name][metric][where])
                
        
    #print(df.head())
            
    return pd.DataFrame(df)
    

def preprocess(data, stats_list, index):
    ''' Return dictionary of DataFrames representing Data

        data is accessed like:
            data['m1']['Total-Tx (Mbps)']['mean']
            
        Each df:
            has columns set to stats_list
            index set to index
            sorted by index
    '''
    

    #df = pd.DataFrame(data)
    #print(df.columns) # ['m1', 'm5', 'm9', ...]

    dataframe_dict = {}
    
    for statistic in stats_list:
        df = select_from(data, statistic)
        df = df.set_index(index).sort_index()

        df = df.groupby(index).mean()
        
        dataframe_dict[statistic] = df
       
    
    return dataframe_dict


def get_vendor_data(device_name, test_name,
                                        sort_by_idx = 'multiple', start_end=[0, 19]):
    
    names = [device_name, test_name]
   
    data = get_data(device_name, test_name)
    stats, stats_list = title_stats(data)
    #stats['m1']['Total-Tx (Mbps)']['mean']

    
    
    dataframe_dict = preprocess(stats, stats_list, index= sort_by_idx)
    
    return dataframe_dict, names, start_end

def get_max_test_data(vendor, test):
    ''' Max test statistic for each division in full TRex Output'''
    stats_table = global_tx_stats( vendor, test, folder=None)

    #columns = ['TxBw_port_0', 'TxBw_port_1']#,'drop-rate','currenttime']
    columns = ['obytes_port_0', 'obytes_port_1', 'ierrors_port_0', 'ierrors_port_1',
       'TxBw_port_0', 'TxBw_port_1', 'CpuUtilization', 'Total-Tx', 'drop-rate',
       'currenttime', 'testduration',]

    
    folders_sorted = sorted(list(map(lambda x: int(x[1:]),
                                                             list(stats_table.keys()))))

    out_df = {'TxBw_port_0':[], 'TxBw_port_1':[], 'multiple':[]}
    for column in columns:
        if column not in out_df:
            out_df[column] = []
            
    for folder in folders_sorted:
        df = mean_df(stats_table, folder='m' + str(folder))
    
        #df['mean'].plot()
        #print(f'\n---> {vendor} {test} {folder}')
        #print(df['mean'][columns].describe().loc[['max']])
        #out_df[folder] = df['mean'][columns].describe().loc[['max']]
        for column in columns:
            
            out_df[column].append(float(df['mean'][column].describe().loc[['max']]))
        out_df['multiple'].append(folder)
        
    out_df = pd.DataFrame(out_df)
    out_df.set_index('multiple', inplace=True)
    
    return out_df

def pandas_graph(info):

    dataframe_dict, names, rng = info
    device_name, test_name = names
    start_idx, end_idx = rng
    
    for stat in dataframe_dict:
        df = dataframe_dict[stat]
        df = df[start_idx:end_idx]
        
        df.plot()
        
        plt.title(device_name + " " + stat)
        plt.show()

        quit()

def combined_graph(info, stat='mean',
                                      x_axis = 'multiple', # <--sort and group, x-axis
                                      y1_label='Throughput (Gbps)',
                                      y2_label='Total-tx-bytes (GB)'):
    dataframe_dict, names, rng = info
    device_name, test_name = names
    start, end = rng

    max_df = get_max_test_data(device_name, test_name)
    merged = pd.merge(dataframe_dict[stat], max_df, how='outer', on='multiple')
    
    #print(merged);
    #quit()
    '''
    columns = ['TxBw_port_0', 'TxBw_port_1','maximum-latency (usec)', 'CpuUtilization (%)',
                        'Total-pkt-drop (pkts)', 'average-latency (usec)',]
    merged = merged[columns]
    '''

    ''' chng idx '''
    if x_axis != 'multiple':
        merged = merged.set_index(x_axis)

    merged.describe().plot.bar()
    plt.show()
    quit()
    
    X = merged.index[start:end]
    Y = merged.iloc[start:end]
    fig, ax1 = plt.subplots()
    #plt.plot(X, Y['TxBw_port_0'], label='TxBw_port_0')
    ax1_label = y1_label
    plt.plot(X, Y[ax1_label], color = 'purple',
                 label=ax1_label, marker='+')
    
    plt.ylabel(ax1_label)
    
    plt.legend(loc='center left')
    '''
    legend loc
                    best
	upper right
	upper left
	lower left
	lower right
	right
	center left
	center right
	lower center
	upper center
	center
    '''
    if x_axis in ['TxBw_port_0', 'TxBw_port_1']:
        x_axis = "Throughput (Gbps)"
    elif x_axis == 'Throughput (Gbps)':
        x_axis = 'Summary Throughput (Gbps)'
    plt.xlabel(x_axis)
    

    ax2 = ax1.twinx()
    ax2_label = y2_label
    #ax2.set(ylim=(-2, 10))
    ax2.plot(X, Y[ax2_label], color = 'orange',
             label = ax2_label, marker='x')
    plt.ylabel(ax2_label)
    
    plt.legend(loc='lower center')
    plt.title(f"{device_name} {test_name} Merged Level Tx")
    
    
    plt.show()

def graph(info, stat='mean',
                  sort_by_idx = 'multiple', # <--sort and group, x-axis
                  y1_label='Throughput (Gbps)',
                  y2_label='Total-tx-bytes (GB)'):
    
    
    dataframe_dict, names, rng = info
    device_name, test_name = names
    start, end = rng

    #print(dataframe_dict[stat])
    
    
    X = dataframe_dict[stat].index[start:end]
    Y = dataframe_dict[stat][[y1_label, y2_label]].iloc[start:end]

    print(Y.head(), "\n Y Shape: ", Y.shape)
    #print(len(X), Y.shape)
    
    # Bar grapht
    width = .4
    x_idx = np.arange(len(X))
    plt.bar(x_idx, Y[y1_label], width=width,
            color='orange', label=y1_label)
    plt.bar(x_idx + width, Y[y2_label], width=width,
            color='purple', label=y2_label)
    plt.xticks(ticks=x_idx, label=X)
    plt.xlabel(sort_by_idx)
    plt.title(device_name + " Pressure Test, 10sec, 4cpu cores")
    plt.legend()
    #plt.show()

    fig, axes = plt.subplots(2)
    fig.suptitle(device_name + ": "+ test_name +", 10sec, 4cpu cores")
    
    
    axes[0].plot(X, Y[y1_label], color="g")
    axes[0].set(ylabel=y1_label)

        
    y2_sigma = dataframe_dict['StdDev'][y2_label].iloc[start:end]
    if y2_sigma.shape[0] == len(X):
        axes[1].errorbar(X, Y[y2_label],
                                     yerr=np.sqrt( y2_sigma ),
                                     color='blue', alpha=0.1)
        
    axes[1].plot(X, Y[y2_label], color='purple')
    
    #'CpuUtilization (%)'
    axes[1].set(ylabel=y2_label, xlabel=sort_by_idx)
    
    plt.show()
    
'''  
Data Metrics Available:

    "Throughput (Gbps)"
    "maximum-latency (usec)"
    "Total-pkt-drop (pkts)"
    "Total-tx-bytes (GB)"
    "average-latency (usec)"
    "CpuUtilization (%)" 

Statistics Available for each Data Metric:
    stats_list = ["mean", "min", 
                          "max", "StdDev",
                          "num"]
    --> assign with stat='stats_list'[idx]
'''

def main():
    
    x_axis = 'multiple'
    combined_x_axis = 'TxBw_port_1'
    y1_label = 'CpuUtilization (%)' #"CpuUtilization"
    y2_label = "average-latency (usec)"
    
    val_range = [0, 200]
    device_name = "Arista"
    test_name =  'multi_many_clients' #"multi_http_simple" 
    get_max_test_data(device_name, test_name)

    
    
    info = get_vendor_data(device_name, test_name,
                                               sort_by_idx = x_axis,
                                               start_end=val_range)
    
    #pandas_graph(info)
    '''
    Combined graph included the following metrics
    From get_max_test_data()
        'TxBw_port_0'
        'TxBw_port_1'
        #,'drop-rate','currenttime']
    '''
   
    combined_graph(info, x_axis=combined_x_axis,
                                    y1_label=y1_label,
                                    y2_label=y2_label)
    #quit()
    '''
    graph(info,
            y1_label=            'Throughput (Gbps)',
            y2_label=            "maximum-latency (usec)",
            )
    '''
    #sort_by_idx="CpuUtilization (%)" )
    #y2_label='avg-latency (usec)'
    #
    
if __name__ == "__main__":
    main()

