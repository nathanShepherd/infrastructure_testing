from os import system, listdir
import pandas as pd

loc = '../vendor_data/Arista/All_Flows_28May2020/'
total_reached_terminal = 0

for flow in listdir(loc):
    if 'm1' in listdir(loc + flow):
        total_reached_terminal += 1


print(total_reached_terminal)

def to_time (string):
    return string.replace('h', ':').replace('m',':').replace('s','')

file_sizes = []
for flow in listdir(loc):
    if 'm1' in listdir(loc + flow):
        #print(loc + flow)
        file_dir = loc + flow + '/m1'
        for i, file in enumerate(listdir(file_dir)):
            print(i, file)
            with open(loc + flow +'/m1/'+ file , 'r') as text:
                text = text.read()
                file_size = len(text.split('\n'))

                if file_size > 50 and file_size < 1000:
                    #print(flow +' file '+ file +' size '+ str(file_size))
                    #print('\'' + flow.replace('_', '/', 1)[:-5] + '.yaml\'', end=', ')
                    file_sizes.append(file_size)
                if i + 1 < len(listdir(file_dir)):
                    print('hi')
                    start = pd.to_datetime(to_time(file))
                    end = pd.to_datetime(to_time(listdir(file_dir)[i + 1]))
                    print(pd.Timedelta(end - start).seconds)
                    
                    

print('Files within condition ' + str(len(file_sizes)))




