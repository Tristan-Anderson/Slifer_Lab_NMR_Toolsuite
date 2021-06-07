"""
Tristan Anderson
takc1nqa@gmail.com
tanderson@vt.edu
"""



# Fortune
"""
I love ROCK 'N ROLL!  I memorized all the WORDS to "WIPE-OUT" in
1965!!
"""


import matplotlib, pandas, scipy, os, gc, time, multiprocessing, sys, matplotlib, argparse, numpy, math, traceback, datetime, warnings
sys.path.insert(1, '..')
import variablenames,daq_muncher, directory_sorter, sweep_averager, global_interpreter, spin_extractor, NMR_Analyzer

sampledumpdir = 'diagnostic_dir/'
samplefile = 'data_record_9-14-2020.csv'

home = os.getcwd()
root = os.getcwd() + '/'+sampledumpdir
tedir = root +'/TE/'
baselinedir = root+'/Baseline/'
blfile = baselinedir+'baseline_average.ta1'
polarizationdir = root+'/Polarization/'
daqfile = root + samplefile
daq_muncher.single_file(daqfile, root)
directory_sorter.shelf(tedir,seconds=30)
sweep_averager.avg_nested_dirs(tedir)
sweep_averager.avg_single_dir(baselinedir)

