
from os import listdir
import json


def find_file_stats_idx(arr):
  for i in range(len(arr) - 1, 0, -1):
    if arr[i] == "port : 0 ":
      return i

def digest_file_stats(in_arr):
  token = ""
  json = {"port : 0 ": 	{'opackets':"",'obytes':"","ipackets":"","ibytes":"","Tx":""},
          "port : 1 ": 	{'opackets':"",'obytes':"","ipackets":"","ibytes":"","Tx":""},
          " summary stats ": {'Total-pkt-drop':"",
  			'Total-tx-bytes':"",
  			'Total-tx-sw-bytes':"",
  			'Total-rx-bytes':'',
  			'Total-tx-pkt':"",
  			'Total-rx-pkt':"",
  			'Total-sw-tx-pkt':"",
  			'Total-sw-err':"",
  			'TotalARPsent':"",
  			'TotalARPreceived':"",
  			'maximum-latency':"",
  			'average-latency':""},
          "Active-flows":	{"drop-rate":"",}, 
          "CpuUtilization": {"CpuUtilization":"",
  			 "Platform_factor":"",
  			 "Total-Tx":"",
  			 "Total-Rx":"",
  			 "Total-PPS":"",
  			 "Total-CPS":"",
  			 "Expected-PPS":"",
  			 "Expected-CPS":"",
  			 "Expected-BPS":""}}
  
  
  for item in in_arr:
    if item in json:
      token = item
      #print("***TOKEN***", item)
    else:
      #item.replace(" ", "")
      item = item.replace(" ", "").split(":")
      #print(item)
      try:   
        if item[0] == "Active-flows":
          pass # TODO handle flows
  
        if item[0] in json[token]:
          json[token][item[0]] = item[1]
  
        if item[0] in json:
          token = item[0]
          json[token][item[0]] = item[1]
  
          #print("***TOKEN***", item)
          
      except IndexError as e:
        print(e)
        
  return json

#%%%%%%%%%%%%%%%%%%%%%%%%#

def read_file(test_file, out_json, test_type):
  # Read output from a TRex output .txt
  #   convert to json object (dict)  
  in_arr = []
  with open(test_file, "r") as f:
    in_arr = f.read().split("\n")

  # Find End of Test stats, remove data appearing before
  divide = find_file_stats_idx(in_arr)
  in_arr = in_arr[divide:-2]

  # Format stats into a known dictionary
  json = digest_file_stats(in_arr)
  out_json[test_type][test_file] = json
  

#%%%%%%%%%%%%%%%%%%%%%%%%#

def collect_archive(archive, vendor, test):
  # Format test data to keys in json and directories in ./
  json = {}

  data_loc = '../vendor_data/' + vendor +'/'+ test +'/'

  for dir in listdir(data_loc):
    if dir.find('.') == -1 and dir != "__pycache__":
      json[dir] = {} #### ADDED for multi
      
      for file in listdir(data_loc + dir):

        print("Reading output from testtype "+ dir +" file "+ file)

        
        read_file(data_loc + dir +'/'+ file, json, dir)


  simple_stats = {"ports":{"0":{"ibytes":[],"obytes":[],"Tx":[]},
                           "1":{"ibytes":[],"obytes":[],"Tx":[]}},
                  "average-latency":[], "maximum-latency":[],
                  "Total-pkt-drop":[], "Total-tx-bytes":[],
                  "Total-Tx":[],"CpuUtilization":[]}
  
  encode = {"Total-Tx":"Throughput (Gbps)",
            "maximum-latency":"maximum-latency (usec)",
            "Total-pkt-drop":"Total-pkt-drop (pkts)",
            "Total-tx-bytes":"Total-tx-bytes (bytes)",
            "average-latency":"average-latency (usec)",
            "CpuUtilization":"CpuUtilization"}# CPU has 2 units

  #for tag in tags: 
  for dir_name in json.keys(): ##### added for multi
    if dir_name == 'm1':
      continue
    print("Archiving test " + dir_name)

    # Store read test entries in arrays
    temp = {"Total-tx-bytes (GB)":[]}

    for title in simple_stats:
      if title not in ["ports", "Total-tx-bytes"]:
        temp[encode[title]] = []
      else:
        temp["ports"] = simple_stats["ports"]
    
    # Reading statistics from filesystem
    for file in json[dir_name]:
      for stat in json[dir_name][file]:
        if stat == "port : 0 ":
          for top in simple_stats["ports"]["0"]:
            temp["ports"]["0"][top].append(json[dir_name][file]["port : 0 "][top])
        elif stat == "port : 1 ":
          for top in simple_stats["ports"]["1"]:
            temp["ports"]["1"][top].append(json[dir_name][file]["port : 1 "][top])

        else: # Extract non-port level data
          #print(dir_name, file, stat)
          #---> m1000 m1000/http_simple_11May  'summary stats'
          #print(json[dir_name][file][stat]); quit()
          for metric in json[dir_name][file][stat]:
            if metric in simple_stats:
              # Remove units from test statistics

              entry = json[dir_name][file][stat][metric]
              if metric == encode[metric] or entry == "":
                temp[encode[metric]].append(entry)
                continue

              # Attemp to get units from assumed encoding
              units = encode[metric].split('(')[-1][:-1]
              
              # TODO: get units from entry and do conversion #####################

              # If units not in assumed format, convert to Gbps
              if entry.find(units) == -1:
                units = entry[-4:]
                num = float(entry[:-4])
                
                if entry[-4:] == 'Kbps':
                  num = (num / 1024) / 1024
                  temp[encode[metric]].append(num)
                  continue
                elif entry[-4:] == 'Mbps':
                  num = num / 1024
                  temp[encode[metric]].append(num)
                  continue
                elif entry[-4:] == 'Gbps':
                  temp[encode[metric]].append(num)
                  continue
                else:
                  raise TypeError('cannot cast ' + str(entry) +' to num')
                
              num = entry.split(units)[0]

              if metric == "Total-pkt-drop": 
                num = int(num) 
              elif metric != "Total-tx-bytes":
                #print(metric) ### ERROR
                num = float(num)
              else:
                # convert bytes to GB
                num = float(num) / 1024 # B to KB
                num /= 1024 # KB to MB
                num /= 1024 # MB to GB
                temp["Total-tx-bytes (GB)"].append( num)
                continue

              temp[encode[metric]].append(num)

    #print(temp); break
    archive[dir_name] = temp

if __name__ == "__main__":
  archive = {}
  collect_archive(archive, 'Arista', 'multi_http_simple')
  
