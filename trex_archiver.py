

def read_file(test_file, out_json, test_type):
  in_arr = []
  with open(test_file, "rb") as f:
    in_arr = f.read().split("\n")

  divide = 0
  for i in range(len(in_arr) - 1, 0, -1):
    if in_arr[i] == "port : 0 ":
      divide = i
      break

  in_arr = in_arr[divide:-2]

  #print(in_arr)

  
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
    
  out_json[test_type][test_file] = json
  


json = {"http_simple":{},
	"imix_64_100k":{},
  	"sfr_delay_10_1g":{},
	"sfr_delay_10_1g_no_bundeling":{}}
  
from os import listdir
  
for dir in listdir('./'):
  if dir.find('.') == -1 and dir != "initial_testing":
    for file in listdir('./' + dir):
      print("Reading output from testtype "+ dir +" file "+ file)
      read_file(dir +'/'+ file, json, dir)

#print(json)

simple_stats = {"ports":{"0":{"ibytes":[],"obytes":[],"Tx":[]},
                         "1":{"ibytes":[],"obytes":[],"Tx":[]}},
                "average-latency":[], "maximum-latency":[],
                "Total-pkt-drop":[], "Total-tx-bytes":[],
                "Total-Tx":[],"CpuUtilization":[]}

# "port : 0 "

######[ change simple stats directory here ]######
# "sfr_delay_10_1g_no_bundeling"
# "sfr_delay_10_1g"
# "imix_64_100k" 
# "http_simple"
tag = "http_simple"

for file in json[tag]:
  for stat in json[tag][file]:
    if stat == "port : 0 ":
      for top in simple_stats["ports"]["0"]:
        simple_stats["ports"]["0"][top].append(json[tag][file]["port : 0 "][top])
    elif stat == "port : 1 ":
      for top in simple_stats["ports"]["1"]:
        simple_stats["ports"]["1"][top].append(json[tag][file]["port : 1 "][top])

    else:
      for metric in json[tag][file][stat]:
        if metric in simple_stats:
          simple_stats[metric].append(json[tag][file][stat][metric])

print(simple_stats)

#import json
#output = json.dumps(simple_stats,
#                    sort_keys=True, indent=4, separators=(',', ':'))

for t in simple_stats:
  print(t)
  for tt in simple_stats[t]:
    if t == "Total-tx-bytes":
      tt = str(float(tt.split("bytes")[0]) / 10000000000) + " GB"
    if t == "CpuUtilization":
      tt = tt.split("Gb/core")[0].split("%")
      tt = tt[0] +" % "+ tt[1] + " Gb/core"
       
    print("\t" + tt)

    if tt in ["0", "1"]:
      for ttt in simple_stats[t][tt]:
        print("\t" + ttt)
        for tttt in simple_stats[t][tt][ttt]:
          print("\t\t" + tttt)

'''
for r in json:
  print(r)
  for r2 in json[r]:
    print(r2)
    for r3 in json[r][r2]:
      print("\t" + r3)
      for r4 in json[r][r2][r3]:
        print("\t" + r4)
        print("\t\t" + json[r][r2][r3][r4])
'''

# Output test statistics
'''
for lay1 in json:
  print(lay1)

  temp = ""
  for stat in json[lay1]:
    if lay != "ports":
      temp += stat + "\t" + json[lay1][stat] + "\n"
    else:
      for metric in json[lay1][stat]:
        temp += metric + "\t" + stat + "\t" + simple_stats[

  print(temp)
'''

