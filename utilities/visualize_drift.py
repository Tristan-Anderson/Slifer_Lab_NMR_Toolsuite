"""
Tristan Anderson
takc1nqa@gmail.com
tanderson@vt.edu
"""

"""
This is used to generate images containing data from a Slifer Lab NMR cooldown.
The NMR analysis toolsuite produces a file called "global_analysis.csv" which this program needs
in tandem with the raw DAQ .csv to form an image sequence that captures the cooldown datastream.

"""

import pandas, os, numpy, multiprocessing, numpy, time, matplotlib, sys
from matplotlib import pyplot as plt
sys.path.insert(1, '..')
import variablenames
# Sept 14 2020 data
"""
rootdir = "../datasets/sep_2020/data_record_9-14-2020/video/"
flist = ['data_record_9-14-2020_abridged.csv', 'data_record_9-15-2020_abridged.csv']
daqdatafile = ["../datasets/sep_2020/rawdata/"+i for i in flist]
csvdirectory = rootdir+"graph_data/"
globalcsv = rootdir+"global_analysis.csv"
globalcsv2 = rootdir+"global_analysis_2.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+"saveme_9_14.csv"
spline_df_location = rootdir+"spline_df_saved_9_14.csv"
rawsig_ym, rawsig_YM = -4, 4
fitsub_xm, fitsub_XM = 32.4,33.4 
fitsub_ym, fitsub_YM= -.2, 1.5
poor_fit_ym, poor_fit_YM = -1.6,-.8
"""

# Dec 3 2020 Data

rootdir = "../datasets/dec_2020/data_record_12-3-2020/"
daqdatafile = '../datasets/dec_2020/rawdata/data_record_12-3-2020_abriged.csv'
csvdirectory = rootdir+"graph_data/"
globalcsv2 = rootdir+"global_analysis_2.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_12_3_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 32.55,33.45
fitsub_ym, fitsub_YM = -.4, .2
rawsig_ym, rawsig_YM = -2, 2
poor_fit_ym, poor_fit_YM = -1,1

# Dec 4 2020 Data
"""
rootdir = "../datasets/dec_2020/data_record_12-4-2020/analysis/polarization/"
csvdirectory = rootdir+"graph_data/"
globalcsv2 = rootdir+"global_analysis_2.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_12_4_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 32.55,33.45
fitsub_ym, fitsub_YM = -.075, .075
rawsig_ym, rawsig_YM = -2, 2
poor_fit_ym, poor_fit_YM = -1,1
"""



# Dec 7 2020
"""
rootdir = "../datasets/dec_2020/data_record_12-7-2020/analysis/Enhanced/"
csvdirectory = rootdir+"graph_data/"
globalcsv2 = rootdir+"global_analysis_2.csv"
yfitsub = 'Fit 1 Subtraction'
karlmethod = rootdir+'saveme_12_7_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 31.85,32.55
fitsub_ym, fitsub_YM = -.3, .2
rawsig_ym, rawsig_YM = -2, 2
poor_fit_ym, poor_fit_YM = -.6,-.1
"""
# Dec 8 2020
"""rootdir = "../datasets/dec_2020/data_record_12-8-2020/analysis/enhanced/"
csvdirectory = rootdir+"graph_data/"
globalcsv2 = rootdir+"global_analysis_2.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_12_8_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 212.45,212.94
fitsub_ym, fitsub_YM = -.01, .02
rawsig_ym, rawsig_YM = -.3, .3
poor_fit_ym, poor_fit_YM = -.018,-.01
"""
# Dec 9 2020
"""
rootdir = "../datasets/dec_2020/data_record_12-9-2020/video/"
csvdirectory = rootdir+"graph_data/"
globalcsv2 = rootdir+"global_analysis_2.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_12_9_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 212.45,212.94
fitsub_ym, fitsub_YM = -.01, .02
rawsig_ym, rawsig_YM = -.3, .3
poor_fit_ym, poor_fit_YM = -.018,-.01
poor_fit_ym, poor_fit_YM = -.005,-.03
"""
# Dec 10 2020 data
"""
csvdirectory = "../datasets/dec_2020/data_record_12-10-2020/video_analysis/graph_data/"
globalcsv2 = "../datasets/dec_2020/data_record_12-10-2020/video_analysis/global_analysis_2.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = 'datasets/2020_12_10/saveme_12_10_20.csv'
spline_df_location = 'datasets/2020_12_10/spline_df.csv'
fitsub_xm, fitsub_XM = 32.6,33.5
fitsub_ym, fitsub_YM = -.2, .25
rawsig_ym, rawsig_YM = -4, 3.5
poor_fit_ym, poor_fit_YM = -.5,0
"""

# Dec 11 2020 data
"""
rootdir = "../datasets/dec_2020/data_record_12-11-2020/video/"
daqdatafile = "../datasets/dec_2020/rawdata/data_record_12-11-2020_abridged.csv"
csvdirectory = rootdir+"graph_data/"
globalcsv = rootdir+"global_analysis.csv"
globalcsv2 = rootdir+"global_analysis_2.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_12_9_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 32.6,33.5
fitsub_ym, fitsub_YM = -.2, .25
rawsig_ym, rawsig_YM = -4, 3.5
poor_fit_ym, poor_fit_YM = -.5,0
"""
# Sept 12 2020 data
"""
rootdir = "../datasets/sep_2020/data_record_9-12-2020/video/"
daqdatafile = "../datasets/sep_2020/rawdata/data_record_9-12-2020_abridged.csv"
csvdirectory = rootdir+"graph_data/"
globalcsv = rootdir+"global_analysis.csv"
globalcsv2 = rootdir+"global_analysis_2.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_9_12_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 32.6,33.5
fitsub_ym, fitsub_YM = -.2, .25
rawsig_ym, rawsig_YM = -4, 3.5
poor_fit_ym, poor_fit_YM = -.5,.4
"""
# Sept 11 2020 data
"""
rootdir = "../datasets/sep_2020/data_record_9-11-2020/video/"
daqdatafile = ["../datasets/sep_2020/rawdata/data_record_9-11-2020_abridged.csv", "../datasets/sep_2020/rawdata/data_record_9-10-2020_abridged.csv"]
csvdirectory = rootdir+"graph_data/"
globalcsv = rootdir+"global_analysis.csv"
globalcsv2 = rootdir+"global_analysis_2_redo.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_9_12_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 32.6,33.5
fitsub_ym, fitsub_YM = -.2, .25
rawsig_ym, rawsig_YM = -4, 3.5
poor_fit_ym, poor_fit_YM = -.5,.4
"""
# Sept 12 2020 data #FOR TE FIXING
"""
rootdir = "../datasets/sep_2020/data_record_9-12-2020_old_analysis/TE/"
daqdatafile = "../datasets/sep_2020/rawdata/data_record_9-12-2020_abridged.csv"
csvdirectory = rootdir+"graph_data/"
globalcsv = "../datasets/sep_2020/data_record_9-12-2020_old_analysis/TE/912_536pTE/global_analysis.csv"
globalcsv2 = "../datasets/sep_2020/data_record_9-12-2020_old_analysis/TE/912_536pTE/global_analysis_with_extra_stuff.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_9_12_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 32.6,33.5
fitsub_ym, fitsub_YM = -.2, .25
rawsig_ym, rawsig_YM = -4, 3.5
poor_fit_ym, poor_fit_YM = -.5,.4
"""
# Sept 11 2020 data
"""
rootdir = "../datasets/sep_2020/data_record_9-11-2020/video/"
daqdatafile = "../datasets/sep_2020/rawdata/data_record_9-11-2020_abridged.csv"
csvdirectory = rootdir+"graph_data/"
globalcsv = rootdir+"global_analysis.csv"
globalcsv2 = rootdir+"global_analysis_2.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_9_11_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 31.95,32.85
fitsub_ym, fitsub_YM = -.2, .25
rawsig_ym, rawsig_YM = -4, 3.5
poor_fit_ym, poor_fit_YM = -.5,.4
"""
# Sept 13 2020 Dat
"""
rootdir = "../datasets/sep_2020/data_record_9-13-2020/video/"
daqdatafile = "../datasets/sep_2020/rawdata/data_record_9-13-2020_abridged.csv"
csvdirectory = rootdir+"graph_data/"
globalcsv = rootdir+"global_analysis.csv"
globalcsv2 = rootdir+"global_analysis_2.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_9_13_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 31.95,32.85
fitsub_ym, fitsub_YM = -.05, .5
rawsig_ym, rawsig_YM = -4, 3.5
poor_fit_ym, poor_fit_YM = -.5,.4
"""
# Sept 15 2020 Data #enhanced
"""
rootdir = "../datasets/sep_2020/data_record_9-13-2020/video/"
daqdatafile = ["../datasets/sep_2020/rawdata/data_record_9-15-2020_abridged.csv", "../datasets/sep_2020/rawdata/data_record_9-14-2020_abridged.csv"]
csvdirectory = rootdir+"graph_data/"
globalcsv = "../datasets/sep_2020/data_record_9-15-2020/video/global_analysis.csv"
globalcsv2 = "../datasets/sep_2020/data_record_9-15-2020/video/global_analysis_long_fixed.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_9_13_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 31.95,32.85
fitsub_ym, fitsub_YM = -.05, .5
rawsig_ym, rawsig_YM = -4, 3.5
poor_fit_ym, poor_fit_YM = -.5,.4
"""
# Sept 15 2020 Data #te
"""
rootdir = "../datasets/sep_2020/data_record_9-13-2020/video/"
daqdatafile = ["../datasets/sep_2020/rawdata/data_record_9-15-2020_abridged.csv", "../datasets/sep_2020/rawdata/data_record_9-14-2020_abridged.csv"]
csvdirectory = rootdir+"graph_data/"
globalcsv = "../datasets/sep_2020/data_record_9-14-2020_old_analysis/700pte/7p_lab/global_analysis.csv"
globalcsv2 = "../datasets/sep_2020/data_record_9-14-2020_old_analysis/700pte/7p_lab/global_analysis_long_fixed.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_9_13_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 31.95,32.85
fitsub_ym, fitsub_YM = -.05, .5
rawsig_ym, rawsig_YM = -4, 3.5
poor_fit_ym, poor_fit_YM = -.5,.4"""


# Dec 10 2020 Data null
"""
rootdir = "../datasets/dec_2020/data_record_12-10-2020/Complete_analysis/null_pure/"
daqdatafile = "../datasets/dec_2020/rawdata/data_record_12-10-2020_abridged.csv"
csvdirectory = rootdir+"graph_data/"
globalcsv = rootdir+"global_analysis.csv"
globalcsv2 = rootdir+"global_analysis_2.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_12_10_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 32.6,33.5
fitsub_ym, fitsub_YM = -.2, .25
rawsig_ym, rawsig_YM = -4, 3.5
poor_fit_ym, poor_fit_YM = -.5,0
"""
# Dec 10 2020 Data
"""
rootdir = "../datasets/dec_2020/data_record_12-10-2020/Complete_analysis/enhanced_pure/"
daqdatafile = "../datasets/dec_2020/rawdata/data_record_12-10-2020_abridged.csv"
csvdirectory = rootdir+"graph_data/"
globalcsv = rootdir+"global_analysis.csv"
globalcsv2 = rootdir+"global_analysis_2.csv"
yfitsub = 'Third order Polynomial 0 Subtraction'
karlmethod = rootdir+'saveme_12_10_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 32.6,33.5
fitsub_ym, fitsub_YM = -.2, .25
rawsig_ym, rawsig_YM = -4, 3.5
poor_fit_ym, poor_fit_YM = -.5,0
"""
# Dec 11 2020 Data
"""
rootdir = "../datasets/dec_2020/data_record_12-11-2020/video/"
daqdatafile = "../datasets/dec_2020/rawdata/data_record_12-11-2020_abridged.csv"
csvdirectory = rootdir+"graph_data/"
globalcsv = rootdir+"global_analysis.csv"
globalcsv2 = rootdir+"global_analysis_2.csv"
yfitsub = 'Fit 1 Subtraction'
karlmethod = rootdir+'saveme_12_11_20.csv'
spline_df_location = rootdir+'spline_df.csv'
fitsub_xm, fitsub_XM = 32.6,33.5
fitsub_ym, fitsub_YM = -.2, .25
rawsig_ym, rawsig_YM = -4, 3.5
poor_fit_ym, poor_fit_YM = -.5,0
"""
dump = "../dump3/"

def forkitindexer(filelist):
    """
        Return a list of tuples of indecies that divide the passed
        list into almost equal slices
    """
    p = int(8*multiprocessing.cpu_count()/10)
    lenset = len(filelist)
    modulus = int(lenset%p)
    floordiv = int(lenset/p)
    slicer = [[floordiv*i, floordiv*(i+1)] for i in range(p-1)]
    slicer.append([floordiv*(p-1), p*floordiv+int(modulus)-1])
    return slicer

def plotter(files, indexes, times, ga_fixed, id_num, deltas, timesteps, deltastime, tkbackend):
	deltasx = 'time'
	deltasy = 'sum'
	x = "MHz"
	bl = "BL Potential (V)"
	raw = "Raw Potential (V)"

	if tkbackend == 'on':
		pass
	elif tkbackend == 'off':
		matplotlib.use('Agg')
	
	s,f = indexes
	todo = files[s:f]
	timedeltas = []

	for i, val in enumerate(todo):

		t1 = time.time()

		fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(16, 8), constrained_layout=True)

		fig.suptitle(str(times[s+i]))

		with open(csvdirectory+val, 'r') as f:
			df = pandas.read_csv(f)

		ss = ga_fixed.loc[times[s+i], 'sigstart']
		sf = ga_fixed.loc[times[s+i], 'sigfinish']
		signal_removed_df = df[(df[x]>ss) & (df[x]<sf)]

		ax[0,0].scatter(df[x], df[yfitsub], label='Fit Subtracted Signal', color='blue')
		ax[0,0].scatter(signal_removed_df[x], signal_removed_df[yfitsub], label='User Selected Region', color='red')
		ax[0,0].legend(loc='best')
		ax[0,0].set_title("Fit Subtracted Signal")
		ax[0,0].set_ylabel('Volts (V)')
		ax[0,0].set_xlabel('Frequency (MHz)')
		ax[0,0].set_ylim(fitsub_ym, fitsub_YM)
		
		ax[0,1].set_title('Temperature')
		ax[0,1].scatter(ga_fixed.index.tolist(), ga_fixed['CCX.T3 (K)'], color='red', label='CCX.T3 (K)')
		ax[0,1].scatter(ga_fixed.index.tolist(), ga_fixed['CCX.T1 (K)'], color='orange', label='CCX.T1 (K)')
		ax[0,1].scatter(ga_fixed.index.tolist(), ga_fixed['CCS.F11 (K)'], color='green', label='CCS.F11 (K)')
		ax[0,1].scatter(ga_fixed.index.tolist(), ga_fixed['CCCS.T2 (K)'], color='blue', label='CCCS.T2 (K)')
		ax[0,1].set_ylim(-.5, 7)
		ax[0,1].set_ylabel('Kelvin (K)')
		ax[0,1].set_xlabel('Time')

		ax[1,0].set_title("Raw Sweeps")
		ax[1,0].scatter(df[x], df[bl], label='Baseline', color='blue')
		ax[1,0].scatter(df[x], df[raw], label =''.join(list(val)[:-4]), color = 'red')
		ax[1,0].set_ylim(rawsig_ym, rawsig_YM)

		ax[1,0].set_ylabel('Volt')
		ax[1,0].set_xlabel('Frequency (MHz)')

		ax[1,1].scatter(ga_fixed.index.tolist(), ga_fixed['data_area'], color='green', label='Enhanced Data Area')
		ax[1,1].set_title("Data Area")
		#ax[1,1].set_ylim(-.025,.05)
		ax[1,1].scatter(timesteps[s+i], ga_fixed.loc[times[s+i], 'data_area'], color='magenta', label='Current sweep')
		ax[1,1].set_ylabel('Volt-Area')
		ax[1,1].set_xlabel('Time')

		ax[0,2].scatter(ga_fixed.index.tolist(), ga_fixed['IFOFF (V)'], label="IFOFF (V)")
		ax[0,2].scatter(timesteps[s+i], ga_fixed.loc[times[s+i],'IFOFF (V)'], color='magenta', label="Current Sweep")
		ax[0,2].grid(True)
		ax[0,2].legend(loc='best')
		ax[0,2].set_title("VME & Microwave Stuff")
		ax[0,2].set_ylabel('Volts (V)')
		ax[0,2].set_xlabel('Time')

		#ax[1,2].set_ylim(poor_fit_ym, poor_fit_YM)
		ax[1,2].scatter(deltastime, deltas[deltasy], label="Signal-Wing avg value")
		if timesteps[s+i] in deltastime:
			ax[1,2].scatter(timesteps[s+i], deltas.loc[times[s+i], deltasy], color='magenta', label="Current Sweep")
		ax[1,2].grid(True)
		ax[1,2].legend(loc='best')
		ax[1,2].set_title("Poor-fit indicator prototype")
		ax[1,2].set_xlabel('Time')

		ax[0,1].scatter(timesteps[s+i], ga_fixed.loc[times[s+i], 'CCX.T3 (K)'], color='magenta', label="Current Sweep")
		ax[0,1].scatter(timesteps[s+i], ga_fixed.loc[times[s+i], 'CCX.T1 (K)'], color='blue')
		ax[0,1].scatter(timesteps[s+i], ga_fixed.loc[times[s+i], 'CCS.F11 (K)'], color='magenta')
		ax[0,1].scatter(timesteps[s+i], ga_fixed.loc[times[s+i], 'CCCS.T2 (K)'], color='magenta')
		
		ax[0,0].grid(True)
		ax[1,0].grid(True)
		ax[1,1].grid(True)
		ax[0,1].grid(True)

		ax[0,1].legend(loc='best')
		ax[0,0].legend(loc='best')
		ax[1,0].legend(loc='best')
		ax[1,1].legend(loc='best')

		plt.savefig(dump+str("{0:05d}".format(s+i)))
		plt.clf()
		plt.close('all')

		t2 = time.time()

		timedeltas.append(t2-t1)
		print('ID:', id_num, ":", (i+1), "of", len(todo), '['+str(round((i+1)*100/len(todo),4))+'%]', "ETA: ", round((len(todo)-(i+1))*numpy.mean(timedeltas),1), 's')

def get_csv_files():
	csvs = []
	for root, dirs, files in os.walk(csvdirectory):
		for f in files:
			if f.endswith('.csv'):
				csvs.append(''.join(list(f)[:-4])) # removes suffixes

	return csvs

def get_global_analysis():
	with open(globalcsv2, 'r') as f:
		df = pandas.read_csv(f)

	name = 'name'
	# Set the indexer as the user-defined name of the analyzed instance
	#	which reflects the file names gotten in the function get_csv_files()
	dffixed = df.set_index(name)


	return dffixed
	
def sync_timestamps_with_csv_filenames(dffixed, csvs):
	timesteps = []
	keys = []

	for i, index in enumerate(csvs):
		try:
			timesteps.append(dffixed.loc[index, 'time'])
			keys.append(index+'.csv')
		except KeyError as e:
			print("Key error", e, "file exists, but no entry in global analysis.")
			continue



	corrected_DF = pandas.DataFrame(dict(zip(['keys', 'time'],[keys, timesteps])))
	sorted_df = corrected_DF.sort_values(by='time')

	return sorted_df

def cutter(ga_csv, sorted_df, tolerance):
	import cutter as cutter2

	minn = -.3
	maxx=-.23
	deltasx = 'time'
	deltasy = 'sum'
	deltasmin = 'spline min'
	deltasmax = 'spline max'
	x = "MHz"
	bl = "BL Potential (V)"
	raw = "Raw Potential (V)"
	edited = input("do you need to subsect (CUT) the data? [Y/N]: ")
	edited = True if edited.upper() == 'Y' else False	
	if edited:
		try:
			with open(spline_df_location, 'r') as f:
				deltas = pandas.read_csv(f)
		except:
			deltas = cutter2.main(tolerance=tolerance, neededpath=karlmethod, global_analysis=globalcsv2)
			with open(spline_df_location, 'w') as f:
				deltas.to_csv(f)
	else:
		with open(karlmethod, 'r') as f:
			deltas = pandas.read_csv(f)

	deltas = deltas.sort_values(by=deltasx)	
	deltas[deltasx] = pandas.to_datetime(deltas[deltasx],format="%Y-%m-%d %H:%M:%S")
	

	ga_csv['time'] = pandas.to_datetime(ga_csv['time'], format="%Y-%m-%d %H:%M:%S")
	asd = ['CCS.F10 (K)','IFOFF (V)', 'Phase Tune (V)', "Diode Tune (V)", "CCX.T3 (K)", 
			"CCX.T1 (K)", "SIG (V)", "UCA Voltage (V)", "Mmwaves Frequency (GHz)", 
			"CCCS.T2 (K)", "CCS.F11 (K)"]
	for i in asd:
		ga_csv[i] = pandas.to_numeric(ga_csv[i], errors='coerce')
	ga_csv.replace(to_replace='Off\n', value=dict(zip(asd,[numpy.nan for a in asd])), inplace=True)
	ga_csv.replace(to_replace='Off', value=dict(zip(asd,[numpy.nan for a in asd])), inplace=True)
	ga_csv = ga_csv.fillna(0)
	ga_csv = ga_csv.sort_values(by='time')	
	
	# Sycronize indecies
	deltas = deltas.set_index(deltasx)
	ga_fixed = ga_csv.set_index('time')
	sorted_df['time'] = pandas.to_datetime(sorted_df['time'],format="%Y-%m-%d %H:%M:%S")
	sorted_df = sorted_df.set_index('time')

	# Merge the dataframes
	ga_fixed = ga_fixed.merge(deltas,left_index=True, right_index=True, how = 'right')
	#ga_fixed = ga_fixed.merge(sorted_df,left_index=True, right_index=False, how = 'right')
	ga_fixed = ga_fixed.join(sorted_df)
	
	# Take "Cuts" (in python/R/SQL language: take a subset based on VALUE critera)

	if edited:
		deltas =deltas[(deltas[deltasy]>deltas[deltasmin])&(deltas[deltasy]<deltas[deltasmax])]
		ga_fixed =ga_fixed[(ga_fixed[deltasy]>ga_fixed[deltasmin])&(ga_fixed[deltasy]<ga_fixed[deltasmax])]

		deltastime = deltas.index.tolist()
		timesteps = ga_fixed.index.tolist()

		sorted_df = pandas.DataFrame({'time':timesteps, 'keys':ga_fixed['keys'].to_list()})

		trashlist = []
		for index,value in enumerate(ga_fixed['keys']):
			try:
				trashlist.append(''.join(list(value)[:-4]))
			except:
				trashlist.append('')
		with open(rootdir+"global_analysis_cleaned.csv", 'w') as f:
			ga_fixed.to_csv(f, columns=[])

	else:
		deltastime = deltas.index.tolist()
		timesteps = ga_fixed.index.tolist()


	return ga_fixed, deltas, timesteps, deltastime, sorted_df

def fetch_df(path, delimiter=','):
	try:
		with open(path, 'r') as f:
			df = pandas.read_csv(f, delimiter=delimiter)
		return df
	except FileNotFoundError:
		print("Can not find path")

def merger(primary_path:str, secondary_path:str, desired_columns:list, shared_column="time"):
	"""

	--> Primary path is the global analysis file produced by analyzing NMR spectra
	--> Secondary path is the raw-data file recorded by the DAQ.
	--> Desired columns is a list of columns that you want to MIGRATE from the 
			raw-data file INTO the global analysis file.

	--> Shared column needs to be some form of timestamp.

	"""
	primary_df = fetch_df(primary_path)
	print(primary_df)
	primary_df[shared_column] = pandas.to_datetime(primary_df[variablenames.vd_GA_timecol], format="%Y-%m-%d %H:%M:%S")
	primary_df = primary_df.sort_values(by=shared_column)

	indexes_to_grab = primary_df.loc[:, shared_column]
	"""
		if you get an index error, double check the delimeter of 
		the secondary path (the DAQ csv). If you see things like:
		9830  12/7/2020 11:59:58 PM\t3690248398.062093\tOff\...
		in the print statement, then make sure the delimeter is correct

	"""
	# Implemented the multiple-file method of merging daq files.
	if type(secondary_path) == list:
		things_to_append = []
		secondary_df = pandas.DataFrame()
		for element in daqdatafile:
			things_to_append.append(fetch_df(element))
		for index, element in enumerate(things_to_append):
			if index == 0:
				secondary_df = element
			else:
				secondary_df = secondary_df.append(element)

	else:
		############ begin problem child ####################
		secondary_df = fetch_df(secondary_path)#, delimiter='\t')
		#secondary_df = secondary_df.loc[:, ~secondary_df.columns.str.contains('^Unnamed')]
		############ End problem child ####################

	print(secondary_df)


	#### Subject of frequenct problems right here child right here:
	"""
		1) is the delimeter correct for primary/secondary dataframes correct?
			- If yes, but still get ValueError: time data doesn't match format
			----> Ensure format
			- if we STILL fail:
		2) Duplicate the secondary file on your hard-disk removing extrenuous columns
			using software like excel, or libre office.
		3) If that doesn't work: give up.

 	"""
	secondary_df[shared_column] = pandas.to_datetime(secondary_df[variablenames.vd_DAQDATA_timecol], format="%m/%d/%Y %I:%M:%S %p")
	#if "Time" in secondary_df.columns.tolist():
	#	secondary_df.drop('Time', inplace=True;)
	#####
	secondary_df = secondary_df.sort_values(by=shared_column)

	print(primary_df)
	primary_df = primary_df.set_index(shared_column)
	secondary_df = secondary_df.set_index(shared_column)

	print(primary_df)
	for i in desired_columns:
		"""
			Using the intersection (subsection) of common timestamps
			in both the global analysis and raw-data dataframes
			Assign for each column in the global analysis dataframe,
			data we want to fetch from the raw-data dataframe.

			*Brain implodes* 
		"""
		primary_df.loc[primary_df.index.intersection(indexes_to_grab), i] = secondary_df.loc[secondary_df.index.intersection(indexes_to_grab), i]
	print(primary_df)
	return primary_df

def metric_getter(files, indexes, times, ga_csv, id_num):
	
	s,f = indexes
	todo = files[s:f]

	ga_csv['time'] = pandas.to_datetime(ga_csv['time'], format="%Y-%m-%d %H:%M:%S")
	asd = ['CCS.F10 (K)','IFOFF (V)', 'Phase Tune (V)', "Diode Tune (V)", "CCX.T3 (K)", 
			"CCX.T1 (K)", "SIG (V)", "UCA Voltage (V)", "Mmwaves Frequency (GHz)", 
			"CCCS.T2 (K)", "CCS.F11 (K)"]
	for i in asd:
		ga_csv[i] = pandas.to_numeric(ga_csv[i], errors='coerce')
	ga_csv.replace(to_replace='Off\n', value=dict(zip(asd,[numpy.nan for a in asd])), inplace=True)
	ga_csv.replace(to_replace='Off', value=dict(zip(asd,[numpy.nan for a in asd])), inplace=True)
	ga_csv = ga_csv.fillna(0)

	
	gasorted = ga_csv.sort_values(by='time')
	timesteps = gasorted['time'].to_list()
	
	ga_fixed = ga_csv.set_index('time')

	x = "MHz"
	bl = "BL Potential (V)"
	raw = "Raw Potential (V)"
	timedeltas = []
	values = []
	xs = []
	lmost = []
	rmost = []
	meanie = []

	for i, val in enumerate(todo):
		with open(csvdirectory+val, 'r') as f:
			df = pandas.read_csv(f)

		ss = ga_fixed.loc[times[s+i], 'sigstart']
		sf = ga_fixed.loc[times[s+i], 'sigfinish']
		signal_removed_df = df[(df[x]<ss) & (df[x]>sf)]

		lm = df.loc[0,raw]
		rm = df.loc[(len(df[raw])-1), raw]
		values.append(df[raw].mean())
		lmost.append(lm)
		rmost.append(rm)
		meanie.append((lm+rm)/2)
		xs.append(str(times[s+i]))
	
	v=pandas.DataFrame({'time':xs,'sum':values, 'leftmost':lmost, 'rightmost':rmost, 'mean':meanie})
	with open(karlmethod, 'w') as f:
		v.to_csv(f)

def main_metric_generator():
	csvs = []
	for root, dirs, files in os.walk(csvdirectory):
		for f in files:
			if f.endswith('.csv'):
				csvs.append(''.join(list(f)[:-4]))

	with open(globalcsv2, 'r') as f:
		df = pandas.read_csv(f)


	name = 'name'

	dffixed = df.set_index(name)

	timesteps = []
	keys = []

	for index in csvs:
		try:
			timesteps.append(dffixed.loc[index, 'time'])
			keys.append(index+'.csv')
		except KeyError as e:
			print("Key error", e)
			continue

	corrected_DF = pandas.DataFrame(dict(zip(['keys', 'time'],[keys, timesteps])))
	sorted_df = corrected_DF.sort_values(by='time')
	timesteps = sorted_df['time'].to_list()
	files = sorted_df['keys'].to_list()

	indexes = forkitindexer(files)

	metric_getter(files, [0,len(files)-1], timesteps, dffixed, 0)

def main_df_column_merger():

	"""
			TODO: implement a way to merge more than one
			DAQ data record into a global analysis file.
	"""
	columns_to_keep = ['CCS.F10 (K)','IFOFF (V)', 'Phase Tune (V)', 
				"Diode Tune (V)", "CCX.T3 (K)", "CCX.T1 (K)", 
				"SIG (V)", "UCA Voltage (V)", "Mmwaves Frequency (GHz)",
				"CCCS.T2 (K)", "CCS.F11 (K)"]
	primary_df = merger(\
			# Global analysis file
			globalcsv,
			# Daq data file
			daqdatafile,
			columns_to_keep)

	with open(globalcsv2, 'w') as f:
		primary_df.to_csv(f)

def main_videomaker(tolerance):
	# Get the sweep Data
	csvs = get_csv_files()
	# Get the global analysis file
	dffixed = get_global_analysis()
	# Synchronize timestamps with filenames 
	sorted_df = sync_timestamps_with_csv_filenames(dffixed, csvs)

	ga_fixed, deltas, timesteps, deltastime, sorted_df_draft = cutter(dffixed, sorted_df, tolerance)

	
	#timesteps = sorted_df['time'].to_list()
	files = sorted_df_draft['keys'].to_list()
	#print(files)
	#exit()
	#print("###"*10)
	#print(files)
	#print(sorted_df_draft)
	#print(sorted_time_copy)
	#exit()

	indexes = forkitindexer(files)
	#print(indexes)
	#exit()
	"""
	for index,value in enumerate(indexes):
		plotter(files, value, timesteps, ga_fixed, 0, deltas, timesteps, deltastime, 'on')
	"""
	#matplotlib.use('Agg')



	with multiprocessing.Pool(processes=int(9*multiprocessing.cpu_count()/10)) as pool:
	    result_objects = [pool.apply_async(plotter, args =(files, value, timesteps, ga_fixed, index, deltas, timesteps, deltastime, 'off')) for index,value in enumerate(indexes)]
	    pool.close()
	    pool.join()



print("#"*50)
print("#",15*" ", "Start Merging", 15*" ","#")
print("#"*50)
if not os.path.isfile(globalcsv2):
	main_df_column_merger()

print("#"*50)
print("#",15*" ", "Start Metric", 15*" ","#")
print("#"*50)
if not os.path.isfile(karlmethod):
	main_metric_generator()
print("#"*50)
print("#",15*" ", "Start Video", 15*" ","#")
print("#"*50)
main_videomaker(tolerance=.3)