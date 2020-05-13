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
    avg_latency = []
    
    latency_sigma = [] # for errorbars
    avg_latency_sigma = []

    throughput = [] #y2

    total_tx = []
    cpu = []
    cpu_sigma = []
    
    
    for m in stats:
        multiplier.append(     int(m[1:]))
        if stats[m]['maximum-latency (usec)']['mean'] > 15:
            max_latency.append( stats[m]['maximum-latency (usec)']['min'])
        else:
            max_latency.append( stats[m]['maximum-latency (usec)']['mean'])
        latency_sigma.append( stats[m]['maximum-latency (usec)']['StdDev'])
        
        avg_latency.append( stats[m]['average-latency (usec)']['mean'] )
        avg_latency_sigma.append( stats[m]['average-latency (usec)']['StdDev'] )
        
        total_tx.append(        stats[m]['Total-tx-bytes (GB)']['mean'])        
        throughput.append(stats[m]['Total-Tx (Gbps)']['mean'])

        cpu.append(stats[m]['CpuUtilization (%)']['mean'])
        cpu_sigma.append(stats[m]['CpuUtilization (%)']['StdDev'])

        
    '''
    print(multiplier)
    print(total_tx)
    print(max_latency)
    print(throughput)
    '''
    print(cpu)

    z = list(zip(multiplier, throughput,
                 max_latency, latency_sigma,
                 avg_latency, avg_latency_sigma,
                 cpu, cpu_sigma,
                 total_tx))
    z.sort(key= lambda x: x[0])

    max_idx = 32
    start_idx = 15
    z = np.array(z)

    
    
    multiplier =        z[start_idx:max_idx, 0]
    throughput =     z[start_idx:max_idx, 1]
    
    max_latency =   z[start_idx:max_idx, 2]
    latency_sigma = z[start_idx:max_idx,3]
    
    avg_latency =     z[start_idx:max_idx,4]
    avg_latency_sigma = z[start_idx:max_idx,5]
    
    cpu =                  z[start_idx:max_idx,6]
    cpu_sigma =     z[start_idx:max_idx,7]

    total_tx =          z[start_idx:max_idx,8]

    
    X = [multiplier, multiplier]
    Y = [throughput, total_tx]

    # Bar graph
    width = .4
    x_idx = np.arange(len(multiplier))
    plt.bar(x_idx, throughput, width=width,
            color='orange', label='Throughput (Gbps)')
    plt.bar(x_idx + width, total_tx, width=width,
            color='purple', label='Total Transmit (GB)')
    plt.xticks(ticks=x_idx, label=multiplier)
    plt.xlabel('Multiplier (10k)')
    plt.title("Arista Pressure Test, 10sec, 4cpu cores")
    plt.legend()
    #plt.show()

    fig, axes = plt.subplots(2)
    fig.suptitle("Arista: http_simple, 10sec, 4cpu cores")
    
    axes[0].plot(X[0], Y[0], color="g")
    axes[0].set(ylabel='Throughput (Gbps)')

    
    #axes[1].errorbar(X[1], Y[1], yerr=np.sqrt(cpu_sigma), color='blue', alpha=0.5)
    axes[1].plot(X[1], Y[1], color='b')
    
    #'CpuUtilization (%)'
    axes[1].set(ylabel='Total Transmitted (GB)', xlabel='Multiple')
    
    
    #stack_figures(X,Y)
    plt.show()
    
        
    
    
if __name__ == "__main__":
    main()
