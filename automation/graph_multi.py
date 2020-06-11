from analysis import get_data, title_stats
from parse_global_stats import * #global_tx_stats, mean_df, get_pS_data
from os import listdir

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





def dual_fig_graph(info, stat='mean',
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
    
    # Bar graph
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










def get_max_tx_data(vendor, test, stat='max'):
    ''' Max test statistic for each division in full TRex Output'''
    stats_table = global_tx_stats( vendor, test, folder=None)
        
    #columns = ['TxBw_port_0', 'TxBw_port_1']#,'drop-rate','currenttime']
    columns = ['obytes_port_0', 'obytes_port_1', 'ierrors_port_0', 'ierrors_port_1',
       'TxBw_port_0', 'TxBw_port_1', 'CpuUtilization', 'Total-Tx', 'drop-rate',
       'currenttime', 'testduration','average_latency_port_1', 'average_latency_port_0']

    
    folders_sorted = sorted(list(map(lambda x: int(x[1:]),
                                                             list(stats_table.keys()))))

    out_df = {'TxBw_port_0':[], 'TxBw_port_1':[], 'multiple':[]}
    for column in columns:
        if column not in out_df:
            out_df[column] = []

   
    
    
    for folder in folders_sorted:
        s_folder = 'm' + str(folder)
        
        for file in stats_table[s_folder]:
            del stats_table[s_folder][file]['datetime']
             
        
        df = collect_agg_files(stats_table, folder=s_folder)
    

        # Combine files in folder by max of each column (metric)
        # ---> Choose df['max'] for max aggregate
        # --> Choose df['mean']  for mean aggregate
        for column in columns:
            out_df[column].append(float(df[stat][column]))
        
        out_df['multiple'].append(folder)

    out_df = pd.DataFrame(out_df)
    
    
    #print(out_df.columns)
    
    
    return out_df






def vendor_tx_viz(   test_name='multi_http_simple',
                                      stat='mean',
                                      x_axis = 'multiple',
                                      y1_label='Throughput (Gbps)',
                                      y2_label='Total-tx-bytes (GB)'):
    '''
    Graph both the Summary of each Trex test as well as stat per sec during each test
    '''
    info = get_vendor_data('Arista', test_name,
                                                sort_by_idx = 'multiple', start_end=[0, 2000])
    dataframe_dict, names, rng = info
    device_name, test_name = names
    start, end = rng

    max_df = get_max_tx_data(device_name, test_name, stat=stat)
    merged = pd.merge(dataframe_dict[stat], max_df, how='outer', on='multiple')
    # Clean data by selecting max at each second
    merged.dropna()
    merged = merged.groupby('currenttime').agg('max').reset_index()
    #merged = merged.groupby('TxBw_port_1').agg('max').reset_index()
    #merged = merged.groupby('obytes_port_1').agg('max').reset_index()
    merged = merged.groupby('multiple').agg('max').reset_index()
    
    # Inlcude data from Cisco's Dell
    
    C_dataframe_dict = {}
    C_dataframe_dict, names, start_end = get_vendor_data('Cisco', test_name,
                                                                        sort_by_idx = 'multiple', start_end=[start, end])

    C_max_df = get_max_tx_data('Cisco', test_name, stat=stat)

    C_merged = pd.merge(C_dataframe_dict[stat], C_max_df, how='outer', on='multiple')
    # Clean data by selecting max at each second
    C_merged.dropna()
    C_merged = C_merged.groupby('currenttime').agg('max').reset_index()
    #C_merged = C_merged.groupby('TxBw_port_1').agg('max').reset_index()
    #C_merged = C_merged.groupby('obytes_port_1').agg('max').reset_index()
    C_merged = C_merged.groupby('multiple').agg('max').reset_index()

    
    
    
    merged['Device'] = ['Arista' for i in range(merged['currenttime'].values.shape[0])]
    C_merged['Device'] = ['Cisco' for i in range(C_merged['currenttime'].values.shape[0])]

    ''' TEST COLS '''
    print('Arista\n', merged[['multiple', 'CpuUtilization', 'TxBw_port_1']])
    print('\nCisco\n', C_merged[['multiple', 'CpuUtilization', 'TxBw_port_1']])
    
    #merged = pd.merge(merged, C_max_df, how='outer', on='multiple') #'multiple')
    merged = merged.reset_index().merge(C_merged, how='outer', on='multiple')
    
    ''' TEST COLS '''
    #import pdb; pdb.set_trace()
    merged = merged.set_index('multiple')
    merged = merged.sort_index()
    print('\nMerged Vendors\n', merged[[ 'CpuUtilization_x', 'CpuUtilization_y', 'Device_x']])    
    merged[['TxBw_port_1_x',
            'TxBw_port_1_y']] =  merged[['TxBw_port_1_x',
                                         'TxBw_port_1_y']].interpolate(method='polynomial', order=2)
    print('\nMerged Vendors\n', merged[[ 'CpuUtilization_x', 'CpuUtilization_y']])    

    merged = merged.reset_index()
    #merged = merged.set_index('TxBw_port_1_x') # multiple 
    cols = ['CpuUtilization_y', 'CpuUtilization_x','TxBw_port_1_x']
    merged = merged[cols]
    merged = merged.interpolate(method='linear', order=2)

    ax1_label = 'Dell Cpu Utilization (%)'
    plt.plot(merged['TxBw_port_1_x'], merged[cols[1]], color = 'purple',
                  label= 'Arista', marker='+')
    plt.plot(merged['TxBw_port_1_x'], merged[cols[0]], color = 'orange',
                  linestyle=':', label= 'Cisco', marker='x')
    
    plt.ylim(-2, 100)
    plt.ylabel(ax1_label)
    plt.xlabel("Dell Throughput (Gbps)")
    plt.title('Vendor System Limit Comparison')
    
    plt.legend(loc='center right')
    plt.show()
 






def tx_combined_graph(info, stat='mean',
                                      x_axis = 'multiple',
                                      y1_label='Throughput (Gbps)',
                                      y2_label='Total-tx-bytes (GB)'):
    '''
    Graph both the Summary of each Trex test as well as stat per sec during each test
    '''
    dataframe_dict, names, rng = info
    device_name, test_name = names
    start, end = rng

    max_df = get_max_tx_data(device_name, test_name, stat=stat)
    merged = pd.merge(dataframe_dict[stat], max_df, how='outer', on='multiple')
    # Clean data by selecting max at each second
    merged.dropna()
    merged = merged.groupby('currenttime').agg('max').reset_index()
    #merged = merged.groupby('TxBw_port_1').agg('max').reset_index()
    #merged = merged.groupby('obytes_port_1').agg('max').reset_index()
    #merged = merged.groupby('multiple').agg('max').reset_index()

        
    
    # Calc running average
    #merged['Cp


    ''' change index '''
    if x_axis != 'multiple':
        merged = merged.set_index(x_axis)
    

    X = merged.index[start:end]
    Y = merged.iloc[start:end]
    fig, ax1 = plt.subplots()
    

    
    if x_axis == 'currenttime':
        X = list( map(lambda x: x/60, X))
        x_axis = 'currenttime (min)'
        #print(X)
    
    ax1_label = y1_label
    plt.plot(X, Y[ax1_label], color = 'purple',
                 label= device_name + ax1_label,
                 marker='+')
    #plt.ylim(-2, 100)
    plt.ylabel(device_name + ax1_label)
    
    plt.legend(loc='lower left')
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
    if x_axis in ['TxBw_port_0', 'TxBw_port_1_y']:
        x_axis = "TRex Throughput (Gbps)"
    elif x_axis == 'Throughput (Gbps)':
        x_axis = 'Summary Throughput (Gbps)'
    plt.xlabel(x_axis)

    if y2_label != None:
    
        ax2 = ax1.twinx()
        ax2_label = y2_label
        ax2.set(ylim=(-2, 100))
        ax2.plot(X, Y[ax2_label], color = 'orange',
                 label = ax2_label, 
                 marker='x')
        plt.ylabel(ax2_label) 
        
    
        plt.legend(loc='center left')
    
    plt.title(f"{device_name} {test_name} Merged Level Tx")
    
    
    plt.show()

   

def TRex_viz_main():
    
    
    '''  
    Possible x_axis for summary_data:
        'multiple'
        "Throughput (Gbps)"
        "maximum-latency (usec)"
        "Total-pkt-drop (pkts)"
        "Total-tx-bytes (GB)"
        "average-latency (usec)"
        "CpuUtilization (%)"
    '''
    x_axis = 'multiple' # for groupy function on each folder
    
    combined_x_axis = 'TxBw_port_1' #'multiple' # ''TxBw_port_1'
    agg_files_stat = 'mean' # max or mean
    
    '''
    Possible combined_x_axis
    from  combined summary and max_lvl TRex data:
        # TODO: add multiple to this list
        ['obytes_port_0', 'obytes_port_1', # High cov with Gbps
        'CpuUtilization',                                  # System Limit
       'TxBw_port_0', 'TxBw_port_1'       # Gbps by port

       'average-latency (usec)',                    # Further research needed
       'maximum-latency (usec)' ,               # Further research needed
                                                                      # - Try rolling avg  
       
       'Total-Tx',                                            # Total Gb by port
                                                                      # - Scales linearly w/Gbps
        'multiple',                                             # Same as Total-Tx
        'drop-rate',                                          # Typically Zero
        'ierrors_port_0', 'ierrors_port_1',  # Typically Zero
       'currenttime', 'testduration',]
    '''

    # Possible y-labels are all possible x_axes
    y1_label = 'CpuUtilization'
    y2_label = None # 'CpuUtilization' # 'average-latency (usec)' # None
    
    val_range = [0, 10000]
    device_name = "Arista"
    test_name =  'multi_http_simple' #"multi_http_simple" 
    

    
    
    info = get_vendor_data(device_name, test_name,
                                               sort_by_idx = x_axis,
                                               start_end=val_range)
    
    
    tx_combined_graph(info, x_axis=combined_x_axis,
                                        y1_label=y1_label,
                                        y2_label=y2_label,
                                        stat=agg_files_stat)

    '''
    dual_fig_graph(info,
                                 y1_label=            'Throughput (Gbps)',
                                 y2_label=            "maximum-latency (usec)",
                                 )
    '''

def trex_viz_all_flows(vendor='Arista', all_flow_dir='All_Flows_28May2020'):
    test_dir = './../vendor_data/Arista/' + all_flow_dir + '/'
    vendor += '/' + all_flow_dir
    flow_arr = []
    for flow_multiples_dir in listdir(test_dir):
        print(flow_multiples_dir)
        max_df = get_max_tx_data(vendor, flow_multiples_dir, stat='max')
        # Add column of traffic type (flow)
        num_rows = max_df.shape[0]
        row_values = ((flow_multiples_dir[:-5] + ' ') * num_rows).split(' ')
        traffic_type = {'Traffic Type': row_values}
        max_df['Traffic Type'] = pd.DataFrame(traffic_type)
        
        flow_arr.append(max_df)
       # print(max_df.columns); quit()
    all_flows = pd.concat(flow_arr)

    print(all_flows.columns)
    columns = ['Total-Tx', 'CpuUtilization','average_latency_port_1',
                        'Traffic Type', 'multiple']
    all_flows = all_flows[columns]

    # Extract max multiple and del col
    all_flows = all_flows[all_flows['multiple'] == 55]
    del all_flows['multiple']
    #del all_flows['average_latency_port_1']

    x_axis = 'CpuUtilization'
    
    #all_flows = all_flows.set_index(x_axis).sort_index()
    print(all_flows)
    #all_flows.plot.bar()
    #plt.show()
        
def graph_flow_from_all(vendor='Arista',
                                             all_flow_dir='All_Flows_28May2020'):
    flows = ['cap2_imix_64_fast_yaml', 'cap2_imix_9k_yaml']
    
    test_dir = './../vendor_data/Arista/' + all_flow_dir + '/'
    vendor += '/' + all_flow_dir
    flow_arr = []
    
    for flow_multiples_dir in listdir(test_dir):
        print(flows)
        if flow_multiples_dir in flows:
            max_df = get_max_tx_data(vendor, flow_multiples_dir, stat='max')
            # Add column of traffic type (flow)
            num_rows = max_df.shape[0]
            row_values = ((flow_multiples_dir[:-5] + ' ') * num_rows).split(' ')
            traffic_type = {'Traffic Type': row_values}
            max_df['Traffic Type'] = pd.DataFrame(traffic_type)
        
            flow_arr.append(max_df)
           # print(max_df.columns); quit()
    all_flows = pd.concat(flow_arr)

    print(all_flows.columns)
    columns = ['CpuUtilization',
                        #'Total-Tx',
                        #'average_latency_port_1','multiple'
                        'Traffic Type', ]
    all_flows = all_flows[columns]
    print(all_flows)
    all_flows.plot()
    
    
    

def graph_Simult_pS(vendor='Arista',
                                        ps_test='pS_Simult_throughput_29May2020',
                                         trex_test='simult_pS_throughput_http_6cores'):

    stats_table = get_pS_throughput(vendor, ps_test)
    all_files = []
    
    for i, file in enumerate(stats_table):
        g = pd.DataFrame(stats_table[file])
        all_files.append(g)

        #print(all_files[0].columns)
    '''
    pS_df = {} # mean of all files in folder for all tests
    for col in all_files[0].columns:
            
        values = []
        for file in all_files:
            values.append(file[col].values)
                
        values = np.array(values)

        pS_df[col] = np.mean(values.T, axis=1)
    '''
    
    
    pS_df = pd.concat(all_files)
    #print(pS_df)
    
    # Collect Trex Data
    tx_data = global_tx_stats(vendor, trex_test)
    tx_df = []
    for folder in tx_data:
        for file in tx_data[folder]:
            tx_df.append(tx_data[folder][file].head())

    

    tx_df = pd.concat(tx_df)
    tx_df['datetime'] = tx_df[['datetime']] - pd.to_timedelta("18:59:21")
    
    #print(tx_df)
    '''
    # TODO : trying to find best time correction to maximize tests that occur at the same time
    orig = tx_df['datetime']
    for i in range(15, 30):
        if i < 10:
            ss = '0' + str(i)
        else:
            ss = str(i)
        tx_df['datetime'] = orig - pd.to_timedelta(f"18:59:{ss}")
        print(pS_df.reset_index().merge(tx_df, how='inner', on='datetime').values.shape)
        
    '''

    merged_cols= ['pS_throughput', 'retransmits', 'interval', 'obytes_port_0',
                               'obytes_port_1', 'ierrors_port_0', 'ierrors_port_1', 'TxBw_port_0',
                               'TxBw_port_1', 'CpuUtilization', 'Total-Tx', 'drop-rate', 'currenttime',
                               'testduration', 'datetime']

    
    
    merged = pS_df.reset_index().merge(tx_df, how='inner', on='datetime')
    print(merged.columns)
    
    
    y_axis= ['pS_throughput']    
    x_axis = 'datetime' # 'TxBw_port_1' # 'datetime'
    aggregate = 'max'

    merged['TRex Throughput (Gbps)'] = merged[['TxBw_port_1']]
    merged = merged.groupby(x_axis, as_index=False).agg(aggregate)
    
    if 'TxBw' in x_axis:
        
        graph_maxes = pd.DataFrame({'pScheduler Throughput (Gbps)': [2, 1.5, 1.42],
                                                                'TRex Throughput (Gbps)': [0, 5, 7.5]})
        graph_maxes.set_index('TRex Throughput (Gbps)', inplace=True)
        
        graph_maxes.plot()
        plt.title(vendor + ' Throughput Comparison')
        #plt.show()
        
        #merged['TRex Throughput (Gbps)'] = merged['TRex Throughput (Gbps)'].rolling(1).max()
        x_axis ='TRex Throughput (Gbps)'
        merged = merged.set_index(x_axis, drop=False).sort_index()
        '''
        # Add column of pScheduler throughput rolling mean
        avg = {'pS_average_Gbps': merged['pS_throughput'].values, }
        for i, raw_num in enumerate(avg['pS_average_Gbps']):
            if i != len(avg['pS_average_Gbps']) - 1:
                mean = (raw_num + avg['pS_average_Gbps'][i + 1]) / 2
                avg['pS_average_Gbps'][i] = mean
                print(mean)
        '''
        #
        #import pdb; pdb.set_trace()
        
        #merged['pS_mean_Gbps'] = pd.concat(pd.DataFrame(avg),
         #                                  merged['TRex Throughput (Gbps)'])
        
        #y_axis.append('pS_mean_Gbps')

    
    print(merged.head())
    
    merged.plot.bar(x_axis, y_axis[0:],)
    plt.show()

    #import pdb; pdb.set_trace()
    
    #merged[y_axis].plot()
    #plt.title(vendor + " Throughput Comparison")
    #plt.show()
    '''
    fig, axes = plt.subplots()
    fig.suptitle(vendor + ": "+ "Simultanious pScheduler and TRex")
    colors = ['green', 'purple', 'orange']
    marks = ['x', '+']
    
    # Support only 2 y_axis
    for i, y in enumerate(y_axis):
        if i > 0:
            axes = axes.twinx()
        axes.scatter(merged[x_axis], merged[y],
                             c=colors[i], marker=marks[i])
        #axes.set(ylabel=y) # does not work in loop
    plt.xlabel(x_axis)
    plt.legend(loc='center left')
    '''

    #plt.show()
    
    #max_df = get_max_tx_data(vendor, trex_test)
    #print(max_df.head())
    #max_df.rename({'currenttime': 'interval'}, inplace=True)

    # At the same time Arista ==  01:03:13, trex = 20:02:40
    # python datetime is different on each device
    # Arista: 29May2020_01h46m50s,  trex: 28May2020_20h46m11s
    
    # Difference in clocks, Arista is 5hrs, 1min, 37sec ahead
    # pd.to_timedelta('20:46:11') -  pd.to_timedelta('1:46:50', unit='second')
    # ==  18:59:21 
    '''
    interv_times = max_df[['currenttime']].values.flatten()
    curr_times = interv_times
    for i in range(len(curr_times)):        
        interv_times[i] = int(curr_times[i])
    curr_t = pd.DataFrame({'currenttime': curr_times,
                                                'interval':interv_times})#, index=trex_times)
    
    #print(max_df)
    trex_df = pd.merge(max_df, curr_t, how='outer', on='currenttime')
    
    

    
    #print( df)
    merged = pd.merge(df, trex_df, how='inner', on='interval')

    merged.set_index('interval', inplace=True)
    print(merged)
    print(trex_df); quit()
    '''
    ## TODO: Combine max_df and trex_df on interval ##
    # Calculate time since start of test to allign intervals
    
    #df.rename(columns ={'throughput': 'Arista_pS_Throughput'})
    '''
    df.plot()
    plt.title(vendor + " " + test)
    plt.xlabel('Time since start of test (sec)')
    plt.show()
    '''
    
if __name__ == "__main__":
    #graph_flow_from_all()
    #trex_viz_all_flows()
    
    #TRex_viz_main()
    vendor_tx_viz()
    
    #graph_Simult_pS(vendor='Arista')

