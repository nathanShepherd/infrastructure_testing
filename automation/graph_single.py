import pandas as pd
import matplotlib.pyplot as plt

from parse_global_stats import global_tx_stats, mean_df, get_pS_data

def get_data(vendor='Arista', test='multi_http_simple', folder='m101000'):
    
    stats_table = global_tx_stats(vendor, test, folder=folder)
    df = mean_df(stats_table, folder=folder)
    return df

def describe_as_bar():
    df = get_data()['mean']

    df.describe().plot.bar()
    plt.show()

def line_plot(columns=['TxBw_port_0', 'TxBw_port_1', 'drop-rate']):
    df = get_data()['mean'][columns]
    df.plot()
    plt.show()

def bar_pS_data(vendor='Arista', test='pS_Simult_with_trexhttp_6cores'):
    # pSControl
    # pS_Simult_sfr_May2020_13h51m
    # pS_Simult_with_trexhttp_6cores
    rows = ['mean', 'max']
    df = get_pS_data(vendor, test)
    df_desc = df.describe()
    print(df_desc)
    
    df.plot.bar()
    plt.show()

def bar_combined_pS():
    '''
    control:
        max, thru = 1.49
        max, retrans = 39
        mean, thru = 1.12
        mean, retrans = 4

    pS_Simult_with_trexhttp_6cores
               throughput  retransmits
count   10.000000    10.000000
mean     1.154120    14.445455
std      0.238163    36.906714
min      0.993363     0.000000
25%      0.997168     0.000000
50%      1.000862     0.000000
75%      1.352221     0.000000
max      1.549091   116.454545

    simult_http_control
    TxBw 9.790286
    control_http_control
    TxBw 9.790286
    '''
    df = {'control_retransmits':[39],
              'control_pS_throughput':[1.5],
              'control_TRex_Throughput':[9.79],
              'Simult_retransmits':[64],
              'Simult_pS_throughput':[1.5],
              'Simult_TRex_Throughput':[9.79]}
    '''
    df = {'retransmits': pd.DataFrame({'control':[39],
                                                                   'simultaneous':[116],}),
                'pS_throughput':  pd.DataFrame({'control':[1.5],
                                                                   'simultaneous':[1.5],}),
              'TRex_Throughput': pd.DataFrame({'control':[9.79],
                                            'simultaneous':[9.79]}),
              }
    '''
    df = pd.DataFrame(df)
    df.plot.bar()
    plt.title("Simultaneous pS-Trex Tests, with control comparison")
    #df['Simultaneous'].plot.bar()

    #df['Control'].plot.bar()
    plt.show()
    
if __name__ == "__main__":
    #describe_as_bar()
    #line_plot()
    #bar_pS_data()
    bar_combined_pS()
    
