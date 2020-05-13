
from os import listdir

def read_file(test_file, out_json, test_type):
  in_arr = []
  with open(test_file, "r") as f:
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
  

#%%%%%%%%%%%%%%%%%%%%%%%%
# Populate archive from keys in json and directories in ./

def collect_archive(archive):
  '''
  json = {"pS_thruput":{},
          "http_simple":{},
          "imix_64_100k":{},
    	  "sfr_delay_10_1g":{},
	  "sfr_delay_10_1g_no_bundeling":{}}
  '''
  json = {}
  

  for dir in listdir('./'):
    if dir.find('.') == -1 and dir != "__pycache__":
      for file in listdir('./' + dir):

        print("Reading output from testtype "+ dir +" file "+ file)

        json[dir] = {} #### ADDED for multi
        read_file(dir +'/'+ file, json, dir)


  simple_stats = {"ports":{"0":{"ibytes":[],"obytes":[],"Tx":[]},
                           "1":{"ibytes":[],"obytes":[],"Tx":[]}},
                  "average-latency":[], "maximum-latency":[],
                  "Total-pkt-drop":[], "Total-tx-bytes":[],
                  "Total-Tx":[],"CpuUtilization":[]}
  '''
  tags = ["sfr_delay_10_1g_no_bundeling",
         "sfr_delay_10_1g",
         "imix_64_100k" ,
         "http_simple",
         "pS_thruput",]
  '''
  
  encode = {"Total-Tx":"Total-Tx (Mbps)",
            "maximum-latency":"maximum-latency (usec)",
            "Total-pkt-drop":"Total-pkt-drop (pkts)",
            "Total-tx-bytes":"Total-tx-bytes (bytes)",
            "average-latency":"average-latency (usec)",
            "CpuUtilization":"CpuUtilization"}# CPU has 2 units

  #for tag in tags: 
  for tag in json.keys(): ##### added for multi

    if tag == 'm1':
      continue
    print("Archiving test " + tag)

    # Store read test entries in arrays
    temp = {"Total-tx-bytes (GB)":[]}

    for title in simple_stats:
      if title not in ["ports", "Total-tx-bytes"]:
        temp[encode[title]] = []
      else:
        temp["ports"] = simple_stats["ports"]
    
    # Reading statistics from filesystem
    for file in json[tag]:
      for stat in json[tag][file]:
        if stat == "port : 0 ":
          for top in simple_stats["ports"]["0"]:
            temp["ports"]["0"][top].append(json[tag][file]["port : 0 "][top])
        elif stat == "port : 1 ":
          for top in simple_stats["ports"]["1"]:
            temp["ports"]["1"][top].append(json[tag][file]["port : 1 "][top])
        else:
          for metric in json[tag][file][stat]:
            if metric in simple_stats:
              # Remove units from test statistics

              entry = json[tag][file][stat][metric]
              if metric == encode[metric] or entry == "":
                temp[encode[metric]].append(entry)
                continue

              units = encode[metric].split('(')[-1][:-1]

              if entry.find(units) == -1:
                if entry[:-4] == 'Kbps':
                  num = 0
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
                #num = float(num) * 0.000001
                num = float(num) / 1024 # B to KB
                num /= 1024 # KB to MB
                num /= 1024 # MB to GB
                temp["Total-tx-bytes (GB)"].append( num)
                continue

              temp[encode[metric]].append(num)

    archive[tag] = temp

if __name__ == "__main__":
  archive = {}
  collect_archive(archive)
