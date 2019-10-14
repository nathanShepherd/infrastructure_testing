from os import system
from time import time
import datetime

'''
initial_testing   sfr_delay_10_1g
http_simple       sfr_delay_10_1g_no_bundeling
imix_64_100k     pS_thruput
'''
timestp = datetime.datetime.fromtimestamp

ts = time()
stamp = timestp(ts).strftime("%d%b%Y_%Hh%Mm%Ss")

out = "/root/initial_testing/" + stamp
system("touch " + out)

_exe = "./t-rex-64 "
system(_exe + "-f cap2/http_simple.yaml -c 4 -m 100 -d 1 -l 1000 > " + out)

print("Created file: " + out + " in " + str(round(time() - ts)) + " seconds")
