from os import system
from time import time
import datetime

timestmp = datetime.datetime.fromtimestamp
no_bundle = "sfr_delay_10_1g_no_bundeling"
_exe = "./t-rex-64 "

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
	out = "/opt/trex/v2.59/test_dir/"
	out = out + title +'/'+ title +'_'+ stamp
	system("touch " + out)

	# Execute test and store in the above created file
        if title in T:
		system(T[title] + " > " + out)

	print("Created file: in " + str(round(time() - ts,1)) + " seconds")
	print(out)

if __name__ == "__main__":
	link("http_simple")
