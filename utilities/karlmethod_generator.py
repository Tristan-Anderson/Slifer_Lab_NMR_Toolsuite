import pandas, os, numpy, multiprocessing, numpy, time, matplotlib
from matplotlib import pyplot as plt

# Sept 14 2020 data
#csvdirectory = "../datasets/sep_2020/data_record_9-14-2020/914_701a_to_915_405p_enhanced/graph_data/"
#globalcsv2 = "../datasets/sep_2020/data_record_9-14-2020/914_701a_to_915_405p_enhanced/global_analysis_2.csv"
#karlmethod = 'saveme_9_14.csv'
# Dec 10 2020 data
#csvdirectory = "../datasets/dec_2020/data_record_12-10-2020/video_analysis/graph_data/"
#globalcsv2 = "../datasets/dec_2020/data_record_12-10-2020/video_analysis/global_analysis_2.csv"
#karlmethod = 'saveme_12_10_20.csv'
# Dec 3 2020
csvdirectory = "../datasets/dec_2020/data_record_12-11-2020/video/graph_data/"
globalcsv2 = "../datasets/dec_2020/data_record_12-11-2020/video/global_analysis_2.csv"
karlmethod = '../datasets/dec_2020/data_record_12-11-2020/video/saveme_12_11_20.csv'



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

def plotter_metric(files, indexes, times, ga_csv, id_num):
	
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

	plotter_metric(files, [0,len(files)-1], timesteps, dffixed, 0)
