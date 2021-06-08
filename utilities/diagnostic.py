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
import variablenames, daq_muncher, directory_sorter, sweep_averager, global_interpreter, spin_extractor, NMR_Analyzer
from asciigui_backend import nmrAnalyser
sampledumpdir = 'diagnostic_dir/'
samplefile = 'data_record_9-14-2020.tsv'

home = os.getcwd()
root = os.getcwd() + '/'+sampledumpdir
tedir = root +'/TE/'
tefile = tedir + "0914_184951_0914_184959p__average.ta1"
baselinedir = root+'/Baseline/'
blfile = baselinedir+'_average.ta1'
polarizationdir = root+'/Polarization/'
daqfile = root + samplefile
daq_muncher.single_file(daqfile, root)
directory_sorter.shelf(tedir,seconds=30)
sweep_averager.avg_nested_dirs(tedir)
sweep_averager.avg_single_dir(baselinedir)

# Start TE Data:
instance = nmrAnalyser('', evademainloop=True)
instance.fetchArgs(fitnumber="fitnumber", automatefits=[['third_order', 'Third order Polynomial 0']], 
	material_type ="TritylDProp", mutouse='deuteron', 
	binning=2, integrate=True, vnavme='vme', signalstart=32.65,
	signalend=33.225, fitlorentzian=False, xname='MHz', xaxlabel='MHz',
	yname='Third order Polynomial 0', yaxlabel='Subtraction Potential (V)',
	xmin='', xmax='', startcolumn=['Potential (V)'], instancename='TritylDPropTE',
	title='TritylDProp', baselinepath=blfile, rawsigpath=tefile, diagnostic=True)
instance.collectFiles()
instance.diagnosticFitting()
instance.updateGraph()

print(instance.df)
instance.mainloop(diagnostic=True)
exit()
del instance
# start enhanced data:
instance = nmrAnalyser('')
instance.fetchArgs(fitnumber="fitnumber", automatefits=[['third_order', 'Third order Polynomial 0']], 
	material_type ="TritylDProp", mutouse='deuteron', 
	binning=2, integrate=True, vnavme='vme', signalstart=32.65,
	signalend=33.225, fitlorentzian=False, xname='MHz', xaxlabel='MHz',
	yname='Third order Polynomial 0', yaxlabel='Subtraction Potential (V)',
	xmin='', xmax='', startcolumn=['Potential (V)'], instancename='TritylDPropENH',
	title='TritylDProp', baselinepath=blfile, rawsigpath=tefile)

