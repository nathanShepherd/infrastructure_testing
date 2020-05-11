from trex_archiver_MULTI import collect_archive
from math import sqrt

def viz_simple_stats(simple_stats):
        for t in simple_stats:
                print(t)
                for tt in simple_stats[t]:
                        if t == "CpuUtilization":
                                tt = tt.split("Gb/core")[0].split("%")
                                tt = tt[0] +" % "+ tt[1] + " Gb/core"
       
                        print("\t" + str(tt))

                        if tt in ["0", "1"]:
                                for ttt in simple_stats[t][tt]:
                                        print("\t" + ttt)
                                        for tttt in simple_stats[t][tt][ttt]:
                                                print("\t\t" + tttt)

def clean(archive):
        outs = {}
        for title in archive:
                temp = {}
                for test in archive[title]:
                        if test not in ["CpuUtilization", "ports"]:
                                temp[test] = archive[title][test]
                                outs[title] = temp
        return outs

def mean(in_arr):
	return sum(in_arr)/len(in_arr)

def sigma(arr, mean):
	summ = 0
	for el in arr:
		summ += (el - mean) ** 2
	return sqrt(el)

def title_stats(json):
        outs = {}
        for title in json:
                outs[title] = {}
                for test in json[title]:
                        outs[title][test] = {}
                        entries = json[title][test]
                        if '' in entries:
                                continue

                        mu = mean(entries)
                        outs[title][test]["mean"] = mu 
                        outs[title][test]["StdDev"] = sigma(entries, mu)
                        outs[title][test]["num"] = len(entries)

        return outs
			
def print_gen_stats(archive):
        for title in archive:
                print("\n--> " + title)
                for el in archive[title]:
                        print(el)
                        for stat in archive[title][el]:
                                out = '\t' + stat + "\t" 
                                print(out + str(archive[title][el][stat]))
                                
def get_data():
        data = {}
        collect_archive(data)
        return clean(data)

def main_print():
        hive = get_data()

        for title in hive:
                print("||| TITLE ||| ::: " + title)
                viz_simple_stats(hive[title])
        
        hive_stat = title_stats(hive)
        print_gen_stats(hive_stat)
        
if __name__ == "__main__":
        main_print()
