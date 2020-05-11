from analysis_MULTI import get_data, title_stats
from grapher import line_plot,  stack_figures
import matplotlib.pyplot as plt
import pandas as pd

'''
  encode = {"Total-Tx":"Total-Tx (Mbps)",
            "maximum-latency":"maximum-latency (usec)",
            "Total-pkt-drop":"Total-pkt-drop (pkts)",
            "Total-tx-bytes":"Total-tx-bytes (bytes)",
            "average-latency":"average-latency (usec)",
            "CpuUtilization":"CpuUtilization"}# CPU has 2 units
'''

def main():
    data = get_data()
    stats = title_stats(data)
    #stats['m1']['Total-Tx (Mbps)']['mean']
    #print(stats)

    multiplier = []    # X
    total_tx = []       # y1
    max_latency = []# y2

    throughput = []
    
    for m in stats:
        multiplier.append(     int(m[1:]))
        max_latency.append( stats[m]['maximum-latency (usec)']['mean'])
        total_tx.append(        stats[m]['Total-tx-bytes (GB)']['mean'])
        
        throughput.append(stats[m]['Total-Tx (Mbps)']['mean'])

    X = [multiplier, multiplier]
    Y = [total_tx, max_latency]
    stack_figures(X,Y)
    plt.show()
    '''
    print(multiplier)
    print(total_tx)
    print(max_latency)
    print(throughput)
    '''
        
    
    
if __name__ == "__main__":
    main()
