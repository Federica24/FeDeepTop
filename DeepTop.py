import os
from ttree_to_h5 import process_signal, process_bkg
import time

t_begin = time.time()

listfiles = os.environ["FILE_NAMES"].split(" ")
print len(listfiles)

for filename in listfiles:
    
    # match with 'qcd' (bkg) or 'ZPrime' (signal) in the filename and call functions
    if 'ZPrime' in filename:
        process_signal(filename)
    elif 'QCD' in filename:
        process_bkg(filename)
    else:
        print 'ERROR: no matching signal/bkg with the filename'

t_end = time.time()
print("Time Elapsed for the search: %6.4f" % ((t_end-t_begin)/60))

