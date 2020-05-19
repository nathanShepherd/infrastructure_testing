from os import listdir
import pandas as pd
import matplotlib.pyplot as plt

import numpy as np

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
                                   'ion', # test duration, Cpu Utilization
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
        
        
    #print(in_arr)
    #print(stats_table)
    return stats_table
    #quit()

def read_directory(file_table, data_loc, folder):
    file_table[folder] = {}
    for file in listdir(data_loc +folder):
            file_table[folder][file] = read_file(data_loc + folder +'/'+ file)
        
def global_tx_stats(vendor, test, folder='m11'):
    # "get flow level data"
    
    
    # Get "ONE" file
    data_loc = '../vendor_data/' + vendor +'/'+ test +'/'
    global_table = {}

    if folder != None:
        read_directory(global_table, data_loc, folder)

        return global_table
    
    for dir in listdir(data_loc):
        
        if  dir.find('.') == -1 and dir != '__pycache__':
            read_directory(global_table, data_loc, dir)
                
            # Remove below to get more files    
            #break
    #print(global_table)
    print(global_table.keys())
    return global_table



def preprocess(stats_table, folder=None):
    ''' Summarize test statitics from a directory of folders
        Each folder contains multiple tests run with the same parameters'''
    
    
    stats_list = ["mean", "min", "max", "variance","num"]
    out_df = {} # summary statistics for sample from folder

    if folder != None:

        all_files = []
        
        for i, file in enumerate(stats_table[folder]):
            g = pd.DataFrame(stats_table[folder][file],
                                             index=stats_table[folder][file]['currenttime'])
            all_files.append(g)

        #print(all_files)

        mean_df = {}
        for col in all_files[0].columns:
            
            values = []
            for file in all_files:
                values.append(file[col].values)
                
            values = np.array(values)
            #print(values)
            #print(values.shape)

            mean_df[col] = np.mean(values.T, axis=1)
            #print(mean_df, mean_df.shape)
            
            
        out_df['mean'] = pd.DataFrame(mean_df, index=mean_df['currenttime'])
            
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

def single_file_stats():
    
    global_tx_stats('Arista', 'multi_http_simple',
                                                          folder='m1000000')
    '''
    file = 'http_simple_11May2020_09h47m16s'
    
    table = stats_table[file]
    
    for row in table:
        print(row, len(table[row]), table[row])
    
    
    df = pd.DataFrame(stats_table[file])
    print(df.head())
    df.plot()
    plt.show()
    '''

    
    for folder in stats_table:
        for file in stats_table[folder]:
            g = pd.DataFrame(stats_table[folder][file],
                                             index=stats_table[folder][file]['currenttime'])
            print(g.tail())
            g.plot()
            plt.title(file)
            plt.show()
        
            
            
    
if __name__ == "__main__":
    stats_table = global_tx_stats( 'Arista', 'multi_http_simple',
                                                          folder=None) #'m101000')
    df = preprocess(stats_table, folder='m101000')
    df['mean'].plot()
    plt.show()
    '''
    for folder in stats_table:
        df = preprocess(stats_table, folder=folder)
    
        df['mean'].plot()
        plt.show()
    '''
