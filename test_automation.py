from os import system
from time import time
import datetime

timestmp = datetime.datetime.fromtimestamp
no_bundle = "sfr_delay_10_1g_no_bundeling"
_exe = "./t-rex-64 "


T = {"pS_thruput":"",
     "initial_testing":_exe +"-f cap2/http_simple.yaml -c 4 -m 10 -d 1 -l 1000",

     "imix_64_100k": _exe +"-f cap2/imix_64_100k.yaml -c 4 -m 2 -d 60 -l 1000",

     no_bundle:_exe +"-f avl/"+ no_bundle +".yaml -c 4 -m 20 -d 60 -l 1000 --ipv6",

     "sfr_delay_10_1g": _exe +"-f avl/sfr_delay_10_1g.yaml -c 4 -m 35 -d 100 -p",

     "http_simple": _exe +"-f cap2/http_simple.yaml -c 4 -m 100 -d 30 -l 1000"}

def link(title):
        ''' Execute one test given the title definition '''

        ts = time()
        stamp = timestmp(ts).strftime("%d%b%Y_%Hh%Mm%Ss")

        out = "/root/" + title +'/'+ title +'_'+ stamp
        system("touch " + out)

        if title in T:
                system(T[title] + " > " + out)

        print("Created file: " + out + " in " + str(round(time() - ts,1)) + " seconds")

if __name__ == "__main__":
        link("initial_testing")

