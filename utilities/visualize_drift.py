"""
Tristan Anderson
tja1015@wildcats.unh.edu
"""

"""
This is used to generate images containing data from a Slifer Lab NMR cooldown.
The NMR analysis toolsuite produces a file called "global_analysis.csv" which this program needs
in tandem with the raw DAQ .csv to form an image sequence that captures the cooldown datastream.

"""

import pandas, os, numpy, multiprocessing, numpy, time, matplotlib
from matplotlib import pyplot as plt
# Sept 14 2020 data
#csvdirectory = "../datasets/sep_2020/data_record_9-14-2020/914_701a_to_915_405p_enhanced/graph_data/"
#globalcsv = "../datasets/sep_2020/data_record_9-14-2020/914_701a_to_915_405p_enhanced/global_analysis_2.csv"
#yfitsub = 'Fit 1 Subtraction' #2020_9_12
#karlmethod = 'saveme9_14.csv'
#fitsub_xm, fitsub_XM = 32.4,33.4 
#fitsub_ym, fitsub_YM= -.2, 1.3
#poor_fit_ym, poor_fit_YM = -1.6,-.8

# Dec 10 2020 data
csvdirectory = "../datasets/dec_2020/data_record_12-10-2020/video_analysis/graph_data"
globalcsv = "../datasets/dec_2020/data_record_12-10-2020/video_analysis/global_analysis_2.csv"
yfitsub = 'Third order Polynomial 0 Subtraction' #2020_12_10
karlmethod = 'datasets/2020_12_10/saveme_12_10_20.csv'
spline_df_location = 'datasets/2020_12_10/spline_df.csv'
fitsub_xm, fitsub_XM = 32.6,33.5
fitsub_ym, fitsub_YM = -.3, .35
rawsig_ym, rawsig_YM = -4, 3.5
poor_fit_ym, poor_fit_YM = -.5,0


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

def plotter(files, indexes, times, ga_fixed, id_num, deltas, timesteps, deltastime):
	deltasx = 'time'
	deltasy = 'sum'
	x = "MHz"
	bl = "BL Potential (V)"
	raw = "Raw Potential (V)"
	

	s,f = indexes
	todo = files[s:f]


	timedeltas = []

	for i, val in enumerate(todo):

		t1 = time.time()

		fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(16, 8), constrained_layout=True)


		fig.suptitle(str(times[s+i]))

		

		with open(csvdirectory+'/'+val, 'r') as f:
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
		ax[0,0].set_xlim(fitsub_xm, fitsub_XM) 
		ax[0,0].set_ylim(fitsub_ym, fitsub_YM)
		



		ax[0,1].set_title('Temperature')
		ax[0,1].scatter(ga_fixed.index.tolist(), ga_fixed['CCX.T3 (K)'], color='red', label='CCX.T3 (K)')
		ax[0,1].scatter(ga_fixed.index.tolist(), ga_fixed['CCX.T1 (K)'], color='orange', label='CCX.T1 (K)')
		#ax[0,1].scatter(ga_fixed.index.tolist(), ga_csv['CCS.F10 (K)'], color='brown', label='CCS.F10 (K)')
		ax[0,1].scatter(ga_fixed.index.tolist(), ga_fixed['CCS.F11 (K)'], color='green', label='CCS.F11 (K)')
		ax[0,1].scatter(ga_fixed.index.tolist(), ga_fixed['CCCS.T2 (K)'], color='blue', label='CCCS.T2 (K)')
		ax[0,1].set_ylim(-.5, 7)
		ax[0,1].set_ylabel('Kelvin (K)')
		ax[0,1].set_xlabel('Time')


		ax[1,0].set_title("Raw Sweeps")
		ax[1,0].scatter(df[x], df[bl], label='Baseline', color='blue')
		ax[1,0].scatter(df[x], df[raw], label =''.join(list(val)[:-4]), color = 'red')
		#ax[1,0].set_xlim(32.4,33.4)#2020_9_12
		ax[1,0].set_xlim(fitsub_xm, fitsub_XM) #2020_12_10
		ax[1,0].set_ylim(rawsig_ym, rawsig_YM)

		#ax[1,0].set_ylim(-1, 1.3)
		ax[1,0].set_ylabel('Volt')
		ax[1,0].set_xlabel('Frequency (MHz)')


		ax[1,1].scatter(ga_fixed.index.tolist(), ga_fixed['data_area'], color='green', label='Enhanced Data Area')
		ax[1,1].set_title("Data Area")
		ax[1,1].legend(loc='best')
		ax[1,1].scatter(timesteps[s+i], ga_fixed.loc[times[s+i], 'data_area'], color='magenta', label='Current sweep')
		ax[1,1].set_ylabel('Volt-Area')
		ax[1,1].set_xlabel('Time')




		ax[0,2].scatter(ga_fixed.index.tolist(), ga_fixed['Diode Tune (V)'], label="Diode Tune (V)")
		ax[0,2].scatter(ga_fixed.index.tolist(), ga_fixed['Phase Tune (V)'], label="Phase Tune (V)")
		ax[0,2].scatter(ga_fixed.index.tolist(), ga_fixed['UCA Voltage (V)'], label="UCA Voltage (V)")
		ax[0,2].scatter(ga_fixed.index.tolist(), ga_fixed['IFOFF (V)'], label="IFOFF (V)")
		ax[0,2].scatter(timesteps[s+i], ga_fixed.loc[times[s+i],'UCA Voltage (V)'], color='magenta', label="Current Sweep")
		ax[0,2].scatter(timesteps[s+i], ga_fixed.loc[times[s+i],'Phase Tune (V)'], color='magenta',)
		ax[0,2].scatter(timesteps[s+i], ga_fixed.loc[times[s+i],'Diode Tune (V)'], color='magenta')
		ax[0,2].scatter(timesteps[s+i], ga_fixed.loc[times[s+i],'IFOFF (V)'], color='magenta')
		ax[0,2].grid(True)
		ax[0,2].legend(loc='best')
		ax[0,2].set_title("VME & Microwave Stuff")
		ax[0,2].set_ylabel('Volts (V)')
		ax[0,2].set_xlabel('Time')

		ax[1,2].set_ylim(poor_fit_ym, poor_fit_YM)
		ax[1,2].scatter(deltastime, deltas[deltasy], label="Karl's Metric")
		if timesteps[s+i] in deltastime:
			ax[1,2].scatter(timesteps[s+i], deltas.loc[times[s+i], deltasy], color='magenta', label="Current Sweep")
		ax[1,2].grid(True)
		ax[1,2].legend(loc='best')
		ax[1,2].set_title("Poor-fit indicator prototype")
		ax[1,2].set_xlabel('Time')


		ax[0,1].scatter(timesteps[s+i], ga_fixed.loc[times[s+i], 'CCX.T3 (K)'], color='magenta', label="Current Sweep")
		ax[0,2].scatter(timesteps[s+i], ga_fixed.loc[times[s+i], 'CCX.T1 (K)'], color='blue')
		#ax[0,1].scatter(timesteps[s+i], ga_fixed.loc[times[s+i], 'CCS.F10 (K)'], color='magenta')
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
		


		plt.savefig(dump+str("{0:04d}".format(s+i)))
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
	with open(globalcsv, 'r') as f:
		df = pandas.read_csv(f)

	name = 'name'
	# Set the indexer as the user-defined name of the analyzed instance
	#	which reflects the file names gotten in the function get_csv_files()
	dffixed = df.set_index(name)

	return dffixed
	
def sync_timestamps_with_csv_filenames(dffixed, csvs):
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

	return sorted_df

def cutter(ga_csv, sorted_df):
	edited =True
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
	
	try:
		if True:
			with open(spline_df_location, 'r') as f:
				deltas = pandas.read_csv(f)
	except:
		deltas = cutter2.main()

	print(deltas)

	deltas = deltas.sort_values(by=deltasx)	
	deltas[deltasx] = pandas.to_datetime(deltas[deltasx],format="%Y-%m-%d %H:%M:%S")
	
	#print(ga_csv)

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
	#print(ga_csv)
	
	# Sycronize indecies
	deltas = deltas.set_index(deltasx)
	ga_fixed = ga_csv.set_index('time')
	sorted_df['time'] = pandas.to_datetime(sorted_df['time'],format="%Y-%m-%d %H:%M:%S")
	sorted_df = sorted_df.set_index('time')

	#print(ga_fixed)
	# Merge the dataframes
	ga_fixed = ga_fixed.merge(deltas,left_index=True, right_index=True, how = 'right')
	#ga_fixed = ga_fixed.merge(sorted_df,left_index=True, right_index=False, how = 'right')
	ga_fixed = ga_fixed.join(sorted_df)
	
	print(ga_fixed)
	# Take "Cuts" (in python/R/SQL language: take a subset based on VALUE critera)
	if edited:
		deltas =deltas[(deltas[deltasy]>deltas[deltasmin])&(deltas[deltasy]<deltas[deltasmax])]
		ga_fixed =ga_fixed[(ga_fixed[deltasy]>ga_fixed[deltasmin])&(ga_fixed[deltasy]<ga_fixed[deltasmax])]

		deltastime = deltas.index.tolist()
		timesteps = ga_fixed.index.tolist()

		sorted_df = pandas.DataFrame({'time':timesteps, 'keys':ga_fixed['keys'].to_list()})
	else:
		deltastime = deltas.index.tolist()
		timesteps = ga_fixed.index.tolist()

	print(ga_fixed)

	return ga_fixed, deltas, timesteps, deltastime, sorted_df


def main():
	# Get the sweep Data
	csvs = get_csv_files()
	# Get the global analysis file
	dffixed = get_global_analysis()
	# Synchronize timestamps with filenames 
	sorted_df = sync_timestamps_with_csv_filenames(dffixed, csvs)

	ga_fixed, deltas, timesteps, deltastime, sorted_df_draft = cutter(dffixed, sorted_df)


	#timesteps = sorted_df['time'].to_list()
	files = sorted_df_draft['keys'].to_list()
	#print(files)
	#exit()
	print("###"*10)
	print(files)
	#print(sorted_df_draft)
	#print(sorted_time_copy)
	#exit()

	indexes = forkitindexer(files)
	#print(indexes)
	#exit()
	#for index,value in enumerate(indexes):
	#	plotter(files, value, timesteps, ga_fixed, 0, deltas, timesteps, deltastime)
	#matplotlib.use('Agg')



	with multiprocessing.Pool(processes=int(9*multiprocessing.cpu_count()/10)) as pool:
	    result_objects = [pool.apply_async(plotter, args =(files, value, timesteps, ga_fixed, index, deltas, timesteps, deltastime)) for index,value in enumerate(indexes)]
	    pool.close()
	    pool.join()

main()