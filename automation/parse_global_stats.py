from os import listdir
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


plt.style.use('bmh')

b_to_GB =  ((( 1 / 1024) / 1024) / 1024)
def bytes_to_GB(num):
    return num * b_to_GB

def convert_to_Gbps(data):
    #print(data, 'XXXXXXXX')
    entry, units = float(data[:-4]), data[-4:]

    
        
    if units == 'Kbps':
        entry = (entry / 1024) / 1024
        
    elif units == 'Mbps':
        entry = (entry / 1024)
        
    elif units == 'Gbps':
        pass

    elif data[-3:] == 'bps':
        
        entry = float(data[:-3])
        entry = ((entry / 1024) / 1024) / 1024
    else:
        raise TypeError('cannot cast ' + str(entry) +' to num')
    return entry

def read_file(file_loc):

    test_name, file = file_loc.split('/')[-2:]
    print(f"Reading output from {test_name} test {file} ")
    
    stats_table = {}
    
    in_arr = []
    with open(file_loc, "r") as f:
        # Skip initializer info, get full text data

        full_test, summary = f.read().split(' *** TRex is shutting down ')

        #print(full_test, '\n %%%%%%%')
        #print(summary, '\n %%%%%%%')
        #quit()
        
        in_arr = full_test.split("-Per port stats table")[1:]
        
    ports_in_table = False
    
    for part in in_arr:
        #print(part + '\n%%%%%%%%%%%%%%\n')
        
        per_port, global_stats = part.split('-Global stats enabled')

        global_stats = global_stats.split('-Latency stats enabled')[0]
        
        for row in per_port.split('\n')[3:-2]:
            ''' Collect TRex output for each port '''
            
            row = row.replace(' ', '').split('|')
            metric, row = row[0], row[1:]

            if metric in ['ipackets', 'opackets', 'ibytes', 'oerrors']:
                continue
            
            if not ports_in_table:
                for n in range(len(row)):
                    stats_table[f'{metric}_port_{n}']  = []
            
            for i, column in enumerate(row):
                port_metric = f'{metric}_port_{i}' 
                
                if metric == 'TxBw':
                    stats_table[port_metric].append(convert_to_Gbps(column))
                elif metric == 'obytes':
                    stats_table[port_metric].append(bytes_to_GB(float(column)))
                else:
                    stats_table[port_metric].append(int(column))
                    
                     

        ports_in_table = True
        #print(stats_table)
        
        for row in global_stats.split('\n')[1:-2]:
            
            #print('XXXX', row.split('-')[0])
            
            if row.split('-')[0] not in [' Active', ' Open', '']:
                
                metric, stat = row.replace(" ", '').split(":")
                
                if metric[-3:] in ['-Rx', 'PPS', 'CPS', 'BPS',
                                   'tor', # Platform_factor
                                   #'ion', # test duration, Cpu Utilization
                                   'ull']: # total_queue_full
                    #print('XXXX', metric, row)
                    continue
                
                if metric not in stats_table:
                    stats_table[metric] = []
                
                    
                if metric  in ["drop-rate", "Total-Tx"]:
                    stats_table[metric].append(convert_to_Gbps(stat))
                                               
                elif metric in ['currenttime', 'testduration']:
                    stats_table[metric].append( float(stat[:-3])) # exclude 'sec'
                    
                elif metric == 'Total_queue_full':
                    stats_table[metric].append(int(stat))
                    
                elif metric == 'CpuUtilization':
                    stats_table[metric].append(float(stat.split('%')[0]))
                
            else: # TODO:  Active & Open rows
                pass

        #print(stats_table)                    
        #quit()
    
    start_date = file.split('_')[-1].replace('h', ':').replace('m',':').replace('s','')
    start_date = str(start_date +' ') * len(stats_table['currenttime'])
    start_date = pd.DataFrame({'datetime':start_date.split(' ')[:-1]})
    start_date = pd.to_datetime(start_date.values.flatten())

    stats_table = pd.DataFrame(stats_table)
    stats_table['datetime'] = start_date + pd.to_timedelta(stats_table['currenttime'].round(0), unit='S')
    
    #print(in_arr)
    #print(stats_table)
    return stats_table
    #quit()

def read_directory(file_table, data_loc, folder):
    file_table[folder] = {}
    for file in listdir(data_loc +folder):
            file_table[folder][file] = read_file(data_loc + folder +'/'+ file)
        
def global_tx_stats(vendor, test, folder=None):
    # "get flow level data"
    
    
    # Get "ONE" file
    data_loc = '../vendor_data/' + vendor +'/'+ test +'/'
    global_table = {}

    if folder != None:
        read_directory(global_table, data_loc, folder)
        #print(global_table[folder].keys())
        return global_table
    
    for dir in listdir(data_loc):
        
        if  dir.find('.') == -1 and dir != '__pycache__':
            read_directory(global_table, data_loc, dir)
                
            # Remove below to get more files    
            #break
    #print(global_table)
    print(global_table.keys())
    return global_table



def mean_df(stats_table, folder=None):
    ''' Summarize test statitics from a directory of folders
        Each folder contains multiple tests run with the same parameters'''
    
    stats_list = ["mean", "min", "max", "variance","num"]
    out_df = {} # summary statistics for sample from folder

    if folder != None:

        all_files = []
        
        for i, file in enumerate(stats_table[folder]):
            g = pd.DataFrame(stats_table[folder][file])
            all_files.append(g)

        #print(all_files[0].columns)

        mean_df = {} # mean of all files in folder for all tests        
        for col in all_files[0].columns:    
            values = []
            for file in all_files:
                values.append(file[col].values)
                
            values = np.array(values)

            mean_df[col] = np.mean(values.T, axis=1)

                    
        out_df['mean'] = pd.DataFrame(mean_df) #, index=mean_df['currenttime'])
            
        return out_df

        
    else:
        print(" Unsupported Option: folder is None")
        '''
        for folder in stats_table:
            #summary_df
            for file in stats_table[folder]:
                g = pd.DataFrame(stats_table[folder][file],
                                                 index=stats_table[folder][file]['currenttime'])
        '''
def read_pS_file(global_table, data_loc):
    in_arr = []
    test_init = ''
    with open(data_loc, "r") as f:
        # Skip initializer info, get full text data

        intro, full_test = f.read().split('* Stream ID 5')
        
        in_arr = full_test.split("Summary")[0].split('\n')
        test_init = intro
        

        
    
    
    titles, in_arr = in_arr[1], in_arr[2:]
    stats = {'pS_throughput':[], 'retransmits':[], 'interval':[]}

    # Select Throughput, retransmit cols by row in interval table
    for row in in_arr[:-2]: # skip empty newlines and column headers

        # Record 'interval' (first column in table)
        #print(row[:15].replace(' ', '').split('-')); quit()
        interval = int(row[:15].replace(' ', '').split('-')[-1].split('.')[0])
        
        row  = row[15:] 
        #print(row)
        gb_rate, row = row.split('ps') # split on Gb(ps), Mb(ps), ...
        if gb_rate[-2:] == 'Kb':
            gb_rate = (float(gb_rate[:-2]) /1024) / 1024
        if gb_rate[-2:] == 'Mb':
            gb_rate = float(gb_rate[:-2]) /1024
        elif gb_rate[-2:] == 'Gb':
            gb_rate = float(gb_rate[:-2])
        else:
            print(f"Unsupported scale in Throughput: {gb_rate}")
            quit()

        stats['interval'].append(interval)
        stats['pS_throughput'].append(gb_rate)
        stats['retransmits'].append(int(row[4:11]))

    file = data_loc.split('/')[-1]
    df = pd.DataFrame(stats)

    #start_date = intro.split('Starts ')[-1].split(' (')[0].split('T')[-1][:-3]
    print(file, data_loc)
    start_date = file.split('_')[-1].replace('h', ':').replace('m',':').replace('s', '')
    start_date = str(start_date +' ') * len(df['interval'].values)
    start_date = pd.DataFrame({'date':start_date.split(' ')[:-1]})
    print(start_date.values)
    start_date = pd.to_datetime(start_date.values.flatten())
    print(start_date)
    
    df['datetime'] =  start_date + pd.to_timedelta(df['interval'], unit='S')
    global_table[file] = pd.DataFrame(df)
    
    #global_table[file].set_index('interval', inplace=True)
        
def get_pS_throughput(vendor='Arista', test='pS_Control'):
    data_loc = '../vendor_data/' + vendor +'/' +test +'/'
    global_table = {}

    for file in listdir(data_loc):
        read_pS_file(global_table, data_loc + file)
    return global_table
                


def get_pS_data(vendor='Arista', test='pSControl'):
    stats_table = get_pS_throughput(vendor, test)
    all_files = []
    
    for i, file in enumerate(stats_table):
        g = pd.DataFrame(stats_table[file])
        all_files.append(g)

        #print(all_files[0].columns)

    mean_df = {} # mean of all files in folder for all tests
    for col in all_files[0].columns:
            
        values = []
        for file in all_files:
            values.append(file[col].values)
                
        values = np.array(values)

        mean_df[col] = np.mean(values.T, axis=1)

    df = pd.DataFrame(mean_df)
    return df
    
def single_file_stats():
    
    stats_table = global_tx_stats('Arista', 'control_sfr_delay_10_1g_6cores',
                                                          folder='m21')
    '''
    file = 'http_simple_11May2020_09h47m16s'
    '''
    
    for folder in stats_table:
        for file in stats_table[folder]:
            g = pd.DataFrame(stats_table[folder][file],
                                             index=stats_table[folder][file]['currenttime'])
            print(g.tail())
            g.plot()
            plt.title(file)
            plt.show()

def describe_all(vendor='Arista', test='multi_http_simple'):
    stats_table = global_tx_stats( vendor, test, folder=None)

    columns = ['TxBw_port_0', 'TxBw_port_1','CpuUtilization','currenttime']
    '''
    some possible columns:
    ['obytes_port_0', 'obytes_port_1', 'ierrors_port_0', 'ierrors_port_1',
       'TxBw_port_0', 'TxBw_port_1', 'CpuUtilization', 'Total-Tx', 'drop-rate',
       'currenttime', 'testduration']
    '''
    folders_sorted = sorted(list(map(lambda x: int(x[1:]),
                                                             list(stats_table.keys()))))
    for folder in folders_sorted:
        df = mean_df(stats_table, folder='m' + str(folder))
        
    
        #print(df['mean'].columns); quit()
        print(f'\n---> {vendor} {test} {folder}')
        print(df['mean'][columns].describe().loc[['max', 'mean']])
            
def plot_all_folders(vendor='Arista', test='multi_http_simple'):
    stats_table = global_tx_stats( vendor, test, folder=None)

    columns = ['TxBw_port_0', 'TxBw_port_1', 'drop-rate']

    for folder in stats_table:
        df = mean_df(stats_table, folder=folder)
    
        df['mean'][columns].plot()
        
        plt.title(f'{vendor} {test} {folder}')
        plt.show()
    
def plot_single_folder(vendor='Arista', test='multi_http_simple', folder='m101000'):
    stats_table = global_tx_stats(vendor, test, folder=folder) 
    df = mean_df(stats_table, folder=folder)

    columns = ['TxBw_port_0', 'TxBw_port_1', 'drop-rate']
    df['mean'][columns].plot()
    plt.title(f'{vendor} {test} {folder}')
    plt.show()

if __name__ == "__main__":
    #plot_all_folders()
    #describe_all(test='control_http_6cores')# pS_Simult_http_6cores control_http_6cores

    read_file('../vendor_data/Arista/All_Flows_28May2020/cap2_http_simple_yaml/m1/02h15m34s')
    #single_file_stats()
    #plot_single_folder(test='pS_Simult_http_6cores',folder = 'm101000')
    #plot_single_folder(test='control_sfr_delay_10_1g_6cores',folder = 'm21')
    #get_pS_throughput()
    #graph_pS()
    #print(get_pS_throughput('Arista', 'pS_Control_throughput_28May2020'))
