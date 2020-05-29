from os import system, listdir
from time import time
import datetime

timestmp = datetime.datetime.fromtimestamp
no_bundle = "sfr_delay_10_1g_no_bundeling"
_exe = "./t-rex-64 "

OUT = "/opt/trex/v2.57/test_dir/"
#OUT = "/home/root/"

# TODO:	Define dictionary T in separate yaml file

# Dictionary T (test) defines each test including the associated executable
# Usage: T[ testname ] returns TRex command for test type "testname"
T = {"pS_thruput":"",
	"initial_testing":_exe +"-f cap2/http_simple.yaml -c 4 -m 10 -d 1 -l 1000",

	"imix_64_100k": _exe +"-f cap2/imix_64_100k.yaml -c 6 -m 2 -d 1 -l 1000",

	no_bundle:_exe +"-f avl/"+ no_bundle +".yaml -c 6 -m 20 -d 1 -l 1000 --ipv6",


	"sfr_delay_10_1g":_exe+"-f avl/sfr_delay_10_1g.yaml -c 4 -m 35 -d 100 -l 1000 -p",
	"sfr_delay_10_1g_6cores":_exe+"-f avl/sfr_delay_10_1g.yaml -c 6 -m 21 -d 100 -l 1000 -p",

	"many_clients": "./t-rex-64 -f cap2/many_client_example.yaml -c 6 -m 1 -d 3 -l 1000",
	"http_both_ports_client": _exe +"-f cap2/http_simple.yaml -c 6 -m 100 -d 1 -l 1000 -p",

	"http_simple": _exe +"-f cap2/http_simple.yaml -c 4 -m 100 -d 1 -l 1000",
	"http_6cores": _exe +"-f cap2/http_simple.yaml -c 6 -m 100 -d 1 -l 1000",
	}

def link(title):
        ''' Execute one test given the title definition '''
	''' Creates text file with TRex output from test'''

	# Get current time and create timestamp
	ts = time()
	stamp = timestmp(ts).strftime("%d%b%Y_%Hh%Mm%Ss")

	# Create file to store output of test "title"
	out = OUT + title +'/'+ title +'_'+ stamp
	system("touch " + out)

	# Execute test and store in the above created file
        if title in T:
		system(T[title] + " > " + out)

	print("Created file: in " + str(round(time() - ts,1)) + " seconds")
	print(out)

def get_multiplier_data_pts(title):
	''' Create directories in dir_name to create multiple files '''
	
	dir_name = "simult_pS_throughput_" + title
	out = OUT + dir_name
	system("mkdir " + out)

        max_multi = int(7e5)
	start_multi = int(2e5)
	num_test = 2
	num_files_per_test = 1

	step_multi = int((max_multi - start_multi) / num_test)

	ts = time()# start of multi_test

	for m in range(start_multi, max_multi, step_multi):
		sub_dir = out +'/'+ 'm' + str(m)
		
		print('\nTried to create ' + sub_dir)
		system("mkdir " + sub_dir)

		for file in range(0, num_files_per_test):
                        test_start = time()
			stamp = '_' + timestmp(test_start).strftime("%d%b%Y_%Hh%Mm%Ss")
			filename = sub_dir +'/'+ title + stamp
			system("touch " + filename)			
			
			print("\nCreated file: " + title + stamp)
			

			# remove any number after -m, replace with multiplier for this test
			_test = T[title].split("-m")
			_test = _test[0] + "-m " + str(m) + ' -d' + _test[1].split('-d')[1]

			system(_test + " > " + filename)

			print("Stored multi test " + str(file) + " of " + str(num_test))
			if file == 0:

				t_elapsed = time() - test_start
				print("duration of last test " + str(t_elapsed/60) + " min")

				t_remain = t_elapsed * num_test
				t_remain *= ((max_multi - m - start_multi) / step_multi)
				t_remain = round(t_remain/60, 1)
				t_remain = str(t_remain) +" minutes"
				print("Estimated time remain "+ t_remain)

		print("\tCompleted m = "+ str(m) +", in time "+ str((time() - test_start)/60) +" min\n")
	print("All multi tests complete in " + str((time() - ts)/60) +" minutes")

def time_remaining(time_elapsed, num_test, range, timestep):
	start, end, step = range
	time_elapsed = float(time_elapsed.split('elapsed')[1][:-4])
	t_remain = time_elapsed * num_test
	# simplify since step_multi == ((end - start) / num_test)
	t_remain *= ((end - timestep - start) / timestep)
	t_remain = round(t_remain/60, 1)

	return str(t_remain) + " minutes"

def time_elapsed(start):
	t = str( round((time() - start)/60, 1) )
	return "time elapsed " + t + "min"

def initialize_file(save_directory):
	test_start = time()
	file_stamp = timestmp(test_start).strftime("%Hh%Mm%Ss")
	filename = save_directory +'/'+ file_stamp
	system("touch " + filename)

	print("Created file " + filename)
	return filename


def create_directory(name, top_level=False):
	if top_level:
	        dir_full_path = OUT + name + '/'
	else:
		dir_full_path = name
        system("mkdir " + dir_full_path)
	return dir_full_path

def exec_trex_test(flow, save_dir, duration, multiplier='1', dual_port=False):
	save_dir = initialize_file(save_dir)
	command = _exe + '-f ' + flow + ' -m ' + multiplier 
	command += ' -c 6 -l 1000 -d ' + duration

	if dual_port:
		command += '-p'

	print("Starting " + command)
	command += ' > ' + save_dir

	system(command)
	
	
def get_all_flow_data(fast=True):
	yaml_files = []

	flow_dirs = ['cap2/cur_flow_single_tw_8.yaml', 'cap2/cur_flow_single.yaml', 'cap2/cur_flow.yaml', 'cap2/dns_no_delay.yaml', 'cap2/dns_one_server.yaml', 'cap2/dns_single_server.yaml', 'cap2/dns_tw.yaml', 'cap2/dns_wlen1.yaml', 'cap2/dns_wlen2.yaml', 'cap2/dns_wlength.yaml', 'cap2/dns_wlen.yaml', 'cap2/dns.yaml', 'cap2/dyn_pyld1.yaml', 'cap2/http_plugin.yaml', 'cap2/http_simple_ipv6.yaml', 'cap2/http_simple.yaml', 'cap2/imix_1518.yaml', 'cap2/imix_64_100k.yaml', 'cap2/imix_64_fast.yaml', 'cap2/imix_64.yaml', 'cap2/imix_9k.yaml', 'cap2/ipv4_load_balance.yaml', 'cap2/jumbo.yaml', 'cap2/lb_ex1.yaml', 'cap2/limit_multi_pkt.yaml', 'cap2/limit_single_pkt.yaml', 'cap2/many_client_example.yaml', 'cap2/per_template_gen1.yaml', 'cap2/per_template_gen2.yaml', 'cap2/per_template_gen3.yaml', 'cap2/per_template_gen4.yaml', 'cap2/rtsp.yaml', 'cap2/short_tcp.yaml', 'cap2/test_pcap_mode1.yaml', 'cap2/test_pcap_mode2.yaml', 'cap2/wrong_ip.yaml']

	if not fast:
		for filename in listdir('cap2'):
			if '.yaml' in filename:
				yaml_files.append(dir +"/"+ filename)
	else:
		yaml_files = flow_dirs

	#print(yaml_files); quit()
	return yaml_files
			

def exec_all_flows():
	start_time = time()# start of all flows test
	
	dir_stamp = "_" + timestmp(start_time).strftime("%d%b%Y")

	output_dir = create_directory("All_Flows" + dir_stamp, top_level=True)

        max_multi = 100
        start_multi = 10
        num_test = 2
	trex_dur = str(1) # seconds
                                                               
        step_multi = int((max_multi - start_multi) / num_test)
	multi_range = (start_multi, max_multi, step_multi)

	flow_yaml_names = get_all_flow_data()

	for flow in flow_yaml_names:
		if 'sfr' in flow:
			continue

		flow_dir = create_directory(output_dir + flow.replace('/', '_').replace('.', '_'))
		print('\nTesting Flow: ' + flow_dir.split('/')[-1])

		flow_start = time()

		for m in range(start_multi, max_multi, step_multi):
			file_dir = create_directory(flow_dir + '/m' + str(m))

			for file in range(0, num_test):
                	        test_start = time()
				exec_trex_test(flow, file_dir, trex_dur, str(m), False)

				if file == 0:
					t_elapsed = time_elapsed(test_start)
					t_remain = time_remaining(t_elapsed, num_test, multi_range, m)

					print("Estimated time remain " + t_remain)
			print("Completed m = "+ str(m) +", in time "+ time_elapsed(test_start))
		print("\tThis flow's multi tests completed in " + time_elapsed(flow_start) + '\n')
	print('Recorded data for all flow in ' + time_elapsed(start_time))

if __name__ == "__main__":
	#link("http_simple")
	#get_multiplier_data_pts('http_6cores')
	exec_all_flows()

