"""
Tristan Anderson
tja1015@wildcats.unh.edu
"""

import pandas, os, numpy, multiprocessing, numpy, time
from matplotlib import pyplot as plt

csvdirectory = "graph_data/"
globalcsv = "global_analysis_2.csv"

def forkitindexer(filelist):
    """
        Return a list of tuples of indecies that divide the passed
        list into almost equal slices
    """
    p = int(8*multiprocessing.cpu_count()/10)
    lenset = len(filelist)
    modulus = int(lenset%p)
    floordiv = int(lenset/p)
    slicer = [[floordiv*i, floordiv*(i+1)-1] for i in range(p-1)]
    slicer.append([floordiv*(p-1), p*floordiv+int(modulus)-1])
    return slicer

def plotter(files, indexes, times, ga_csv, id_num):
	dump = "dump3/"
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

	for i, val in enumerate(todo):

		t1 = time.time()

		fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(16, 8), constrained_layout=True)


		#fig.suptitle(str(times[s+i]))

		

		with open(csvdirectory+val, 'r') as f:
			df = pandas.read_csv(f)

		ax[0,0].scatter(df[x], df["Third order Polynomial 0 Subtraction"], label='Fit Subtracted Signal', color='red')
		ax[0,0].legend(loc='best')
		ax[0,0].set_title("Fit Subtracted Signal")
		ax[0,0].set_ylabel('Volts (V)')
		ax[0,0].set_xlabel('Frequency (MHz)')
		ax[0,0].set_xlim(32.6,33.5)
		ax[0,0].set_ylim(-.175, .25)



		ax[0,1].set_title('Temperature')
		ax[0,1].scatter(ga_csv['time'], ga_csv['CCX.T3 (K)'], color='red', label='CCX.T3 (K)')
		#ax[0,2].scatter(ga_csv['time'], ga_csv['CCX.T1 (K)'], color='orange', label='CCX.T1 (K)')
		ax[0,1].scatter(ga_csv['time'], ga_csv['CCS.F10 (K)'], color='brown', label='CCS.F10 (K)')
		ax[0,1].scatter(ga_csv['time'], ga_csv['CCS.F11 (K)'], color='green', label='CCS.F11 (K)')
		ax[0,1].scatter(ga_csv['time'], ga_csv['CCCS.T2 (K)'], color='blue', label='CCCS.T2 (K)')
		ax[0,1].set_ylim(-.5, 7)
		ax[0,1].set_ylabel('Kelvin (K)')
		ax[0,1].set_xlabel('Time')


		ax[1,0].set_title("Raw Sweeps")
		ax[1,0].scatter(df[x], df[bl], label='Baseline', color='blue')
		ax[1,0].scatter(df[x], df[raw], label =''.join(list(val)[:-4]), color = 'red')
		ax[1,0].set_xlim(32.6,33.5)
		ax[1,0].set_ylim(-1, 1.3)
		ax[1,0].set_ylabel('Volt')
		ax[1,0].set_xlabel('Frequency (MHz)')


		ax[1,1].scatter(ga_csv['time'], ga_csv['data_area'], color='green', label='Enhanced Data Area')
		ax[1,1].set_title("Data Area")
		ax[1,1].legend(loc='best')
		ax[1,1].scatter(timesteps[s+i], ga_fixed.loc[times[s+i], 'data_area'], color='magenta', label='Current sweep')
		ax[1,1].set_ylabel('Volt-Area')
		ax[1,1].set_xlabel('Time')



		ax[0,2].scatter(ga_csv['time'], ga_fixed['Diode Tune (V)'], label="Diode Tune (V)")
		ax[0,2].scatter(ga_csv['time'], ga_fixed['Phase Tune (V)'], label="Phase Tune (V)")
		ax[0,2].scatter(ga_csv['time'], ga_fixed['UCA Voltage (V)'], label="UCA Voltage (V)")
		ax[0,2].scatter(timesteps[s+i], ga_fixed.loc[times[s+i],'UCA Voltage (V)'], color='magenta', label="Current Sweep")
		ax[0,2].scatter(timesteps[s+i], ga_fixed.loc[times[s+i],'Phase Tune (V)'], color='magenta',)
		ax[0,2].scatter(timesteps[s+i], ga_fixed.loc[times[s+i],'Diode Tune (V)'], color='magenta')
		ax[0,2].grid(True)
		ax[0,2].legend(loc='best')
		ax[0,2].set_title("VME & Microwave Stuff")
		ax[0,2].set_ylabel('Volts (V)')
		ax[0,2].set_xlabel('Time')

		ax[1,2].scatter(ga_csv['time'], ga_fixed['SIG (V)'], label="SIG (V)")
		ax[1,2].scatter(timesteps[s+i], ga_fixed.loc[times[s+i],'SIG (V)'], color='magenta', label="Current Sweep")
		ax[1,2].grid(True)
		ax[1,2].legend(loc='best')
		ax[1,2].set_title("SIG")
		ax[1,2].set_ylabel('Volts (V)')
		ax[1,2].set_xlabel('Time')


		ax[0,1].scatter(timesteps[s+i], ga_fixed.loc[times[s+i], 'CCX.T3 (K)'], color='magenta', label="Current Sweep")
		#ax[0,2].scatter(timesteps[s+i], ga_fixed.loc[times[s+i], 'CCX.T1 (K)'], color='blue')
		ax[0,1].scatter(timesteps[s+i], ga_fixed.loc[times[s+i], 'CCS.F10 (K)'], color='magenta')
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


csvs = []
for root, dirs, files in os.walk(csvdirectory):
	for f in files:
		if f.endswith('.csv'):
			csvs.append(''.join(list(f)[:-4]))

with open(globalcsv, 'r') as f:
	df = pandas.read_csv(f)


name = 'name'

dffixed = df.set_index(name)

timesteps = []
keys = []

for index in csvs:
	timesteps.append(dffixed.loc[index, 'time'])
	keys.append(index+'.csv')

corrected_DF = pandas.DataFrame(dict(zip(['keys', 'time'],[keys, timesteps])))

sorted_df = corrected_DF.sort_values(by='time')
timesteps = sorted_df['time'].to_list()
files = sorted_df['keys'].to_list()

indexes = forkitindexer(files)

matplotlib.use('Agg')

#for index,value in enumerate(indexes):
#	plotter(files, value, timesteps, dffixed, 0)

with multiprocessing.Pool(processes=int(8*multiprocessing.cpu_count()/10)) as pool:
    result_objects = [pool.apply_async(plotter, args =(files, value, timesteps, dffixed, index)) for index,value in enumerate(indexes)]
    pool.close()
    pool.join()



