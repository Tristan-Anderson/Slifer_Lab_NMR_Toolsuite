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


import matplotlib, pandas, scipy, os, gc, time, shutil, multiprocessing, sys, matplotlib, argparse, numpy, math, traceback, datetime, warnings
sys.path.insert(1, '..')
import variablenames, daq_muncher, directory_sorter, sweep_averager, global_interpreter, spin_extractor, NMR_Analyzer
from asciigui_backend import nmrAnalyser



sampledumpdir = 'diagnostic_dir/'
samplefile = 'data_record_9-14-2020.tsv'

home = os.getcwd()
root = home + '/'+sampledumpdir
for root, dirs, files in os.walk(root):
	break
for directory in dirs:
	#print(directory)
	shutil.rmtree(root+directory)


te_global = home+"/global_analysis.csv"
enh_global = home + "/global_analysis_enhanced_data.csv"
try:
	os.remove(te_global)
	os.remove(enh_global)
except FileNotFoundError:
	pass

tedir = root +'TE/'
tefile = tedir + "0914_184951_0914_184959p_diagnostic_dir_average.ta1"
baselinedir = root+'Baseline/'
blfile = baselinedir+'diagnostic_dir_average.ta1'
polarizationdir = root+'Polarization/'
polarizationfile = polarizationdir+"VME_2020_09_14_19_01_23.ta1"
daqfile = root + samplefile
daq_muncher.single_file(daqfile, root)
directory_sorter.shelf(tedir,seconds=30)
sweep_averager.avg_nested_dirs(tedir, returndir=home)
sweep_averager.avg_single_dir(baselinedir, returndir=home)

# Start TE Data:
instance = nmrAnalyser(evademainloop=True, hardinit=True)
instance.fetchArgs(fitnumber="fitnumber", automatefits=[['third_order', 'Third order Polynomial 0']], 
	material_type ="TritylDProp", mutouse='deuteron', 
	binning=2, integrate=True, vnavme='vme', signalstart=32.65,
	signalend=33.225, fitlorentzian=False, xname='MHz', xaxlabel='MHz',
	yname='Third order Polynomial 0', yaxlabel='Subtraction Potential (V)',
	xmin='', xmax='', startcolumn=['Potential (V)'], instancename='TritylDPropTE',
	title='TritylDProp', baselinepath=blfile, rawsigpath=tefile, diagnostic=True)
instance.collectFiles()
instance.diagnosticFitting()
instance.overrideYname('Third order Polynomial 0 Subtraction')
#instance.updateGraph()
instance.mainloop(diagnostic=True)

del instance
# start enhanced data:
instance = nmrAnalyser(evademainloop=True, hardinit=True)
instance.fetchArgs(fitnumber="fitnumber", automatefits=[['third_order', 'Third order Polynomial 0']], 
	material_type ="TritylDProp", mutouse='deuteron', 
	binning=2, integrate=True, vnavme='vme', signalstart=32.65,
	signalend=33.225, fitlorentzian=False, xname='MHz', xaxlabel='MHz',
	yname='Third order Polynomial 0', yaxlabel='Subtraction Potential (V)',
	xmin='', xmax='', startcolumn=['Potential (V)'], instancename='TritylDPropENH',
	title='TritylDProp', baselinepath=blfile, rawsigpath=polarizationfile, diagnostic=True)
instance.collectFiles()
instance.diagnosticFitting()
instance.overrideYname('Third order Polynomial 0 Subtraction')
print("Enhanced analysis commencing:")
try:
	instance.automate(addition="_enhanced_data")
except KeyboardInterrupt:
	pass
print("Beginning global analysis.")


constants, teinfo = global_interpreter.collator(te_global,te=True, home='.', title="TE d-Prop", deuteron=True)

global_interpreter.collator(enh_global, home='.', constant=constants, to_save=teinfo, title="ENHANCED d-Prop", deuteron=True)
