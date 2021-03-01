import pandas, numpy, datetime
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit as fit
from matplotlib import rc
#rc('text', usetex=True)
#font = {'size'   : 30}
#rc('font', **font)

def spin_down(t, pmax, t0, tau, d):
	# = args[0], args[1], args[2]
	return pmax*(1-numpy.exp(-(t-t0)/tau))+d

def spin_up(t, p0, t0, tau, d):
	# = args[0], args[1], args[2]
	return p0*numpy.exp(-(t-t0)/tau)+d

def file_fetcher(filename, t):

	with open(filename, 'r') as f:
		df = pandas.read_csv(f)

	df[t] = pandas.to_datetime(df[t], format="%Y-%m-%d %H:%M:%S")
	df = df.sort_values(t)

	return df

def df_trimmer(df, Sd, Sm, Sy, sh, sm,  fh,fm, t, ss=0, fs=0, Fd=None,Fm=None,Fy=None):
	if Fd is None:
		Fd = Sd
	if Fm is None:
		Fm = Sm
	if Fy is None:
		Fy = Sy
	startdate = datetime.datetime(year=Sy, month=Sm, day=Sd, hour=sh, minute=sm, second=ss)
	enddate = datetime.datetime(year=Fy, month=Fm, day=Fd, hour=fh, minute=fm, second=fs)

	df = df[(df[t]>startdate)&(df[t]<enddate)].sort_values(t)

	return df

def get_x_for_fit(trimmed, Sd, Sm, Sy, t):
	"""
	Get the x data (of type datetime) into a format that scipy can interpret (seconds from the start of the day)
	
	"""

	end_time = (max(trimmed[t].tolist())-datetime.datetime(year=Sy, month=Sm, day=Sd)).total_seconds()
	
	start_time = (min(trimmed[t].tolist())-datetime.datetime(year=Sy, month=Sm, day=Sd)).total_seconds()

	timestamp_list = trimmed[t].tolist()
	timesteps = []

	for index, val in enumerate(timestamp_list):
		if index == len(timestamp_list)-1:
			break
		timesteps.append((timestamp_list[index+1]-val).total_seconds())
		
	avg_timestep = numpy.mean(timesteps)

	xdata_for_fit = numpy.arange(start_time, end_time, avg_timestep).tolist()
	xdata_for_fit.append(xdata_for_fit[-1]+avg_timestep)

	return xdata_for_fit

def previewdata_gui(*args, **kwargs):
	filename, title, Sd, Sm, Sy, sh, sm,  fh,fm, p,t = args
	ss=kwargs.pop('ss', 0)
	fs=kwargs.pop('fs',0)
	Fd=kwargs.pop('Fd',None)
	Fm=kwargs.pop('Fm',None)
	Fy=kwargs.pop('Fy',None)
	preview=kwargs.pop('preview',True)
	bounds=kwargs.pop('bounds',[])
	up=kwargs.pop('up',True)
	df = file_fetcher(filename, t)

	trimmed = df_trimmer(df, Sd, Sm, Sy, sh, sm,  fh,fm, t, ss=ss, fs=fs, Fd=Fd,Fm=Fm,Fy=Fy)

	fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(8.5, 11), constrained_layout=True)
	ax[0].set_title(title)
	ax[1].set_xlabel("Datetime")
	ax[0].set_xlabel("Datetime")
	ax[0].scatter(df[t], df[p], c='b', label=title)
	ax[0].scatter(trimmed[t], trimmed[p], c='red')
	ax[1].scatter(trimmed[t], trimmed[p], c='red')
	ax[0].grid(True)
	ax[1].grid(True)

	return fig

def getupdown(*args, **kwargs):
	filename, title, Sd, Sm, Sy, sh, sm,  fh,fm, p,t = args
	ss=kwargs.pop('ss', 0)
	fs=kwargs.pop('fs',0)
	Fd=kwargs.pop('Fd',None)
	Fm=kwargs.pop('Fm',None)
	Fy=kwargs.pop('Fy',None)
	preview=kwargs.pop('preview',False)
	bounds=kwargs.pop('bounds',[])
	up=kwargs.pop('up',True)
	df = file_fetcher(filename, t)

	trimmed = df_trimmer(df, Sd, Sm, Sy, sh, sm,  fh,fm, t, ss=ss, fs=fs, Fd=Fd,Fm=Fm,Fy=Fy)

	xforfit = get_x_for_fit(trimmed, Sd, Sm, Sy, t)
	yforfit = trimmed[p].to_list()
	xforplot = trimmed[t]

	fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(8.5, 11), constrained_layout=True)

	ax[0].set_title(title)
	
	ax[0].set_xlabel("Datetime")
	ax[0].scatter(df[t], df[p], c='b', label=title)
	ax[0].scatter(trimmed[t], trimmed[p], c='red')
	ax[0].grid(True)

	ax[1].set_xlabel("Datetime")
	ax[1].scatter(trimmed[t], trimmed[p], c='red')
	ax[1].grid(True)

	if up:
		print(xforfit, yforfit)
		fitvars, _ = fit(spin_up, xforfit, yforfit, p0=bounds)#, bounds=[(0, 83500, 0),(numpy.inf, 100000, numpy.inf)])
		print("\n\nSpin up:", "pmax*(1-numpy.exp(-(t-t0)/tau))+shift\n")
		print(title)
		print("pmax", "t0", "tau", 'shift')
		for i, val in enumerate(["pmax:", "t0:", "tau:", "shift:"]):
			print(fitvars[i],end='\t')
		print('')
		fy = spin_up(xforfit, fitvars[0], fitvars[1], fitvars[2], fitvars[3])
		ax[1].plot(xforplot, fy, c='green', label="Spin Up")
	else:

		fitvars, _ = fit(spin_down, xforfit, yforfit, p0=bounds)#, bounds=[(0, 83500, 0),(numpy.inf, 100000, numpy.inf)])
		print("\n\nSpin down:", "p0*numpy.exp(-(t-t0)/tau)+shift\n")
		print(title)
		print(["p0", "t0", "tau", "shift"])
		for i, val in enumerate(["p0:", "t0:", "tau:","shift:"]):
			print(fitvars[i],end='\t')

		fy = spin_up(xforfit, fitvars[0], fitvars[1], fitvars[2], fitvars[3])
		ax[1].plot(xforplot, fy, c='green', label="Spin Down")

	ax[1].legend(loc='best')

	return fig

#ax = previewdata_gui("/home/kb/research/wdirs/NMR_Toolsuite/global_analysis.csv",
#	"2020-12-10 Down", 10, 12, 2020, 20, 32, 22,32, 'data_area', 'time', ss=30, preview=True, up=True, bounds=[.02, 69200, 7200, .015])
ax = getupdown("/home/kb/research/wdirs/NMR_Toolsuite/global_analysis.csv",
	"2020-12-10 Up", 10, 12, 2020, 19, 56, 21,8, 'data_area', 'time', ss=30, preview=True, up=True, bounds=[.02, 69200, 7200, .015])

ax.show()
input('Press ENTER to continue')
