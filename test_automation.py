from os import system
from time import time
import datetime

timestmp = datetime.datetime.fromtimestamp
no_bundle = "sfr_delay_10_1g_no_bundeling"
_exe = "./t-rex-64 "
OUT = "/opt/trex/v2.57/test_dir/"

# TODO:	Define dictionary T in separate yaml file

# Dictionary T (test) defines each test including the associated executable
# Usage: T[ testname ] returns TRex command for test type "testname"
T = {"pS_thruput":"",
     "initial_testing":_exe +"-f cap2/http_simple.yaml -c 4 -m 10 -d 1 -l 1000",

     "imix_64_100k": _exe +"-f cap2/imix_64_100k.yaml -c 4 -m 2 -d 60 -l 1000",

     no_bundle:_exe +"-f avl/"+ no_bundle +".yaml -c 4 -m 20 -d 60 -l 1000 --ipv6",

     "sfr_delay_10_1g":_exe+"-f avl/sfr_delay_10_1g.yaml -c 4 -m 35 -d 100 -l 1000 -p",

     "http_simple": _exe +"-f cap2/http_simple.yaml -c 4 -m 100 -d 1 -l 1000"}

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
	
	dir_name = "multi_" + title
	out = OUT + dir_name
	system("mkdir " + out)

        max_multi = 200
	step_multi = 10
	num_test = 3
	ts = time()

	for m in range(1, max_multi, step_multi):
		sub_dir = out +'/'+ 'm' + str(m)
		
		system("mkdir " + sub_dir)

		for file in range(0, num_test):
                        test_start = time()
			stamp = '_' + timestmp(test_start).strftime("%d%b%Y_%Hh%Mm%Ss")
			filename = sub_dir +'/'+ title + stamp
			system("touch " + filename)
			
			print(filename)

			# remove any number after -m, replace with multiplier for this test
			_test = T[title].split("-m")
			_test = _test[0] + "-m " + str(m) + ' -d' + _test[1].split('-d')[1]

			system(_test + " > " + filename)

			print("Stored multi test " + str(file) + " of " + str(num_test))
			if file == 0:
				t_elapsed = time() - ts
				print("duration of test " + str(t_elapsed))
				t_remain = t_elapsed * num_test * ((max_multi - 1) / step_multi)
				t_remain = round(t_remain/60, 1)
				t_remain = str(t_remain) +" minutes"
				print("Estimated time remain "+ t_remain)
		print("Completed m = " + str(m) + ", in time " + str((time() - ts)/60) + "min")
	print("All multi tests complete in " + str((time() - ts)/60) )
		
	

if __name__ == "__main__":
	#link("http_simple")
	get_multiplier_data_pts("http_simple")

