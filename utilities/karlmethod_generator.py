import pandas, os, numpy, multiprocessing, numpy, time, matplotlib
from matplotlib import pyplot as plt

# Sept 14 2020 data
#csvdirectory = "../datasets/sep_2020/data_record_9-14-2020/914_701a_to_915_405p_enhanced/graph_data/"
#globalcsv = "../datasets/sep_2020/data_record_9-14-2020/914_701a_to_915_405p_enhanced/global_analysis_2.csv"
#dump = "../dump3/"
#savefile = 'saveme_9_14.csv'

# Dec 10 2020 data
csvdirectory = "../datasets/dec_2020/data_record_12-10-2020/video_analysis/graph_data/"
globalcsv = "../datasets/dec_2020/data_record_12-10-2020/video_analysis/global_analysis_2.csv"
dump = "../dump3/"
savefile = 'saveme_12_10_20.csv'
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

def plotter(files, indexes, times, ga_csv, id_num):
	
	s,f = indexes
	#sprint(files)
	todo = files[s:f]
	#print('\n'*10)
	#print(todo)
	#print(s,f)
	#it = [i for i in range(s,f+1)]

	ga_csv['time'] = pandas.to_datetime(ga_csv['time'], format="%Y-%m-%d %H:%M:%S")
	#asd = ['CCS.F10 (K)','IFOFF (V)', 'Phase Tune (V)', "Diode Tune (V)", "CCX.T3 (K)", 
	#		"CCX.T1 (K)", "SIG (V)", "UCA Voltage (V)", "Mmwaves Frequency (GHz)", 
	#		"CCCS.T2 (K)", "CCS.F11 (K)"]
	#for i in asd:
	#	ga_csv[i] = pandas.to_numeric(ga_csv[i], errors='coerce')
	#ga_csv.replace(to_replace='Off\n', value=dict(zip(asd,[numpy.nan for a in asd])), inplace=True)
	#ga_csv.replace(to_replace='Off', value=dict(zip(asd,[numpy.nan for a in asd])), inplace=True)
	#ga_csv = ga_csv.fillna(0)

	
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

	for i, val in enumerate(todo):
		with open(csvdirectory+val, 'r') as f:
			df = pandas.read_csv(f)

		ss = ga_fixed.loc[times[s+i], 'sigstart']
		sf = ga_fixed.loc[times[s+i], 'sigfinish']
		signal_removed_df = df[(df[x]<ss) & (df[x]>sf)]
		values.append(df[raw].mean())
		lmost.append(df.loc[0,raw])
		rmost.append(df.loc[(len(df[raw])-1), raw])
		xs.append(str(times[s+i]))
	
	v=pandas.DataFrame({'time':xs,'sum':values, 'leftmost':lmost, 'rightmost':rmost})
	with open(savefile, 'w') as f:
		v.to_csv(f)
	
	#plt.scatter(x,values, label='data')
	#plt.legend(loc='best')
	#plt.savefig('nice')
	#plt.show()
	#input("Please hold")
	#exit()



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

#for two in indexes:
#	print([i for i in range(two[0], two[1]+1)])

#print(indexes)

#exit()
#""
#print(indexes)
#exit()

#for index,value in enumerate(indexes):
#	plotter(files, value, timesteps, dffixed, 0)

plotter(files, [0,len(files)-1], timesteps, dffixed, 0)

#matplotlib.use('Agg')



#with multiprocessing.Pool(processes=int(9*multiprocessing.cpu_count()/10)) as pool:
#    result_objects = [pool.apply_async(plotter, args =(files, value, timesteps, dffixed, index)) for index,value in enumerate(indexes)]
#    pool.close()
#    pool.join()