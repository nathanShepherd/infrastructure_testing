from analysis_MULTI import get_data, title_stats
from grapher import line_plot,  stack_figures

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

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
    max_latency = []

    throughput = [] #y2

    latency_sigma = [] # for errorbars
    
    for m in stats:
        multiplier.append(     int(m[1:]))
        if stats[m]['maximum-latency (usec)']['mean'] > 100:
            max_latency.append(max_latency[-1])
        else:
            max_latency.append( stats[m]['maximum-latency (usec)']['mean'])
        latency_sigma.append( stats[m]['maximum-latency (usec)']['StdDev'])
        total_tx.append(        stats[m]['Total-tx-bytes (GB)']['mean'])
        
        throughput.append(stats[m]['Total-Tx (Mbps)']['mean'])

    

    z = list(zip(multiplier, throughput, max_latency, latency_sigma))
    z.sort(key= lambda x: x[0])
    z = np.array(z)

    multiplier = z[:, 0]
    throughput = z[:, 1]
    max_latency = z[:, 2]
    
    latency_sigma = z[:,3] 

    print(multiplier)
    print(total_tx)
    print(max_latency)
    print(throughput)
    
    X = [multiplier, multiplier]
    Y = [throughput, max_latency]

    fig, axes = plt.subplots(2)
    fig.suptitle("Cisco: sfr_delay_10_1g multipliers")
    
    axes[0].plot(X[0], Y[0], color="g")
    axes[0].set(ylabel='Total-Tx (Mbps)')

    
    axes[1].errorbar(X[1], Y[1], yerr=np.sqrt(latency_sigma), color='blue', alpha=0.5)
    axes[1].plot(X[1], Y[1])
    
    axes[1].set(ylabel='maximum-latency (usec)', xlabel='Multiple')
    
    
    #stack_figures(X,Y)
    plt.show()
    
        
    
    
if __name__ == "__main__":
    main()
