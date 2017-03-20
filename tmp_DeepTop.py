import os
from ttree_to_h5 import process_signal, process_bkg
import time

t_begin = time.time()

#listfiles = os.environ["FILE_NAMES"].split(" ")
file = open("files.txt","r")
listfiles = file.readlines()
print len(listfiles)

for filename in listfiles:
    
    print filename
    
    # match with 'qcd' (bkg) or 'ZPrime' (signal) in the filename and call functions
    if 'z1000' in filename:
        process_signal(filename.split('\n')[0])
    elif 'QCD' in filename:
        process_bkg(filename.split('\n')[0])
    else:
        print 'ERROR: no matching signal/bkg with the filename'

t_end = time.time()
print("Time Elapsed for the search: %6.4f" % ((t_end-t_begin)/60))

