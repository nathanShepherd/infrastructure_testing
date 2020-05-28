from os import system
from time import time

test = 'sudo docker exec -it b0f40e4d5072 pscheduler task throughput --dest 198.111.224.153'

outdir = 'pS_Sumult_May2020_13h51m/'
duration = 17 # min

def cur_t(start):
	return round((time() - start) / 60)

start = time()

for i in range(duration*2):
	if cur_t(start) < duration:
		print('time: ' + str(cur_t(start)))
		file = outdir +str(i)+ "_" + str(cur_t(start))

		system('touch ' + file)
		print('file ' + file + ' created')

		system(test +' > '+ file)
	else:
		break

