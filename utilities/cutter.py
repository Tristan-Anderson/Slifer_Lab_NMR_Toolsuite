import datetime,pandas,os,numpy,gc,time,multiprocessing,matplotlib,argparse
import numpy as np
from scipy.interpolate import CubicSpline as spline
from matplotlib import pyplot as plt


"""
Tristan Anderson
takc1nqa@gmail.com
tanderson@vt.edu
"""

"""
Scope: We've got some nasty data, and this program should use cubic spline interpolation 
	to draw a line throuhgh, or near, the data that we're interested in. Then, taking the
	dataset's x-axis, the spline will be compared point-wise to the dataset. If the Datapoint from 
	the dataset falls within a user-defined criteria, the x-component of the datapoint will be stored
	and then be used to subset an seperate datatset.
"""

x = 'time'
y = 'Scaled Polarization (%)'

class AsciiGUI():
	"""
	The master template
	for the different frames of an
	ascii-gui page.

	Each option will need to have access to a:
		- File/Dir selector
		- Output formatting
		- And an Options selection method,
	"""
	def __init__(self, args, **passed):
		self.delimeter = '\t'
		self.hardinit = passed.pop('hardinit',False)
		if passed.pop('getrootdir',False):
			self.rootdir = os.getcwd()
		self.processes = 1
		self.servermode = False
		if self.hardinit:
			self.servermode = args.servermode

	def fileDirectorySelector(self):
		cwd = os.getcwd()
		status = True
		while status:
			fixeddirs, fixedfiles, cleanfiles, dirs = self.getdir(cwd)
			print("Current working Directory:", cwd)
			print("Enter choice in the format of: \'LineNum(f/d)\n ex: 1f")
			status, path = self.choice(fixeddirs, fixedfiles, cleanfiles, dirs)
			
			cwd = path
		return path

	def getdir(self, cwd):
		# Get the items in a directory
		for subdir, dirs, files in os.walk(cwd):
			break
		#print("Current directory:", cwd)
		cleanfiles = []
		for f in files:
			if any(ext in f for ext in ['.csv']):
				# If theres a match in the allowable extensions, then save it
				# Otherwise, dont.
				cleanfiles.append(f)
		# String-lengths of the allowable file extensions
		filewidth = [len(i) for i in cleanfiles]
		try:
			# Width for output formatting.
			filewidth = max(filewidth)+2
		except ValueError:
			# If theres no allowable extenstions, cleanfiles is of length 0
			# And therefor has no max value in zero-len list.
			filewidth = 0

		if filewidth < 7:
			# Is the minimum width of the file column in ascii format
			filewidth = 7

		dwidth = [len(i) for i in dirs]
		try:
			dwidth = max(dwidth)+2
		except ValueError:
			dwidth= 2
		if dwidth < 13:
			# is the minimum width of the directory column in the ascii output formatted table
			dwidth = 13

		crossbar_width = filewidth+dwidth+3+9
		dirlongfile = len(dirs) > len(cleanfiles)
		fixeddirs = []
		fixedfiles = []
		###########################
		"""
		If the file list and directory list are not of the same length,
		make whichever list is shorter, as long as the longest width, filling
		the missing values with sentinals (i.e. '') so that output formatting
		can print the options.
		"""
		if dirlongfile: 
			for index,value in enumerate(dirs):
				fixeddirs.append(value)
				if index < len(cleanfiles):
					fixedfiles.append(cleanfiles[index])
				else:
					fixedfiles.append(' '*filewidth)

		else:
			for index,value in enumerate(cleanfiles):
				fixedfiles.append(value)
				if index < len(dirs):
					fixeddirs.append(dirs[index])
				else:
					fixeddirs.append(' '*dwidth)
		##########################

		######## BEGIN OUTPUT FORMATTING ###########
		print('#'*crossbar_width)
		print(str("{0:^1}{3:^8}{0:^1}{1:^"+str(filewidth)+"}{0:^1}{2:^"+str(dwidth)+"}{0:^1}").format("#","Files","Directories","LinNUM"))
		print('#'*crossbar_width)
		bbreak = False
		for index, value in enumerate(fixedfiles):
			print(str("{0:^1}{3:^8}{0:^1}{1:^"+str(filewidth)+"}{0:^1}{2:^"+str(dwidth)+"}{0:^1}").format('#', value, fixeddirs[index], index))
			if index > 25:
				bbreak = True
				break
		print('#'*crossbar_width)
		if bbreak:
			print("Printing exceeded 100 lines.")
		return fixeddirs, fixedfiles, cleanfiles, dirs

	def choice(self, fixeddirs, fixedfiles, cleanfiles, dirs):
		c = input("Enter Choice: ")
		if 'd' in c.lower():
			item = int(c.split('d')[0])
			if item in range(len(dirs)):
				newpath = fixeddirs[item]
				os.chdir(newpath)
				return True, os.getcwd()
		elif 'f' in c.lower():
			item = int(c.split('f')[0])
			if item in range(len(cleanfiles)):
				newpath = fixedfiles[int(c.split('f')[0])]
				return False, os.getcwd()+'/'+newpath
		elif '..' == c:
			os.chdir(c)
			return True, os.getcwd()
		elif 'ok' in c:
			print('okay. Saving current directory choice.')
			return False, os.getcwd()
		self.announcement("You selected " +c+ ' which is not a valid option.')
		return True, os.getcwd()

	def dict_selector(self, dic):
		"""
		expects a key:tupple unorganized dictionary where
			tuple = [String, Function]
		such that the string describes the properties of the function.

		the "key"
		has the function of not only being the ouput choice of this selector
		function, but it also is the key to the tuple.
		"""
		def tableformatter(keys, strs):
			len_keys = [len(key) for key in keys]
			maxlen_keys = max(len_keys)+2

			keydescribers = strs
			len_keydescribers = [len(k) for k in keydescribers]
			maxlen_key_descrbers = max(len_keydescribers)+2
			maxlen_key_descrbers = 10 if maxlen_key_descrbers < 10 else maxlen_key_descrbers
			xbar = maxlen_keys + maxlen_key_descrbers +4+8+1

			print('#'*xbar)
			print(str('{0:1}{1:^9}{0:1}{2:^'+str(maxlen_keys)+'}{0:1}{3:^'+str(maxlen_key_descrbers)+'}{0:1}').format('#','option#','name','describers'))
			print('#'*xbar)
			for index,value in enumerate(keys):
				print(str('{0:1}{1:^9}{0:1}{2:^'+str(maxlen_keys)+'}{0:1}{3:^'+str(maxlen_key_descrbers)+'}{0:1}').format('#',index,value,keydescribers[index]))
			print('#'*xbar)
			return True

		keys = dic.keys()
		options = [i for i in range(len(keys))]
		reconsile = dict(zip(options, keys))
		keydescribers = []
		for k in keys:
			value = dic[k]
			if type(value) == list:
				keydescribers.append(dic[k][0])
			else:
				keydescribers.append(dic[k])
		tableformatter(keys,keydescribers)

		choices = 'hey'
		while True:
			try:
				choices = int(input("Enter option number: "))
				print("Your choice was", reconsile[choices], 'returning...')
				break
			except KeyboardInterrupt:
				print('keyboard inturrupt recived. Breaking.')
				raise KeyboardInterrupt
			except ValueError as e:
				print("Invalid input. Try again.", '\n'*2)
				continue
			except KeyError:
				print("Incorrect Key. Make sure option number matches that which is in the table of options.")
				continue
		return reconsile[choices]

	def announcement(self, mystr):
		print('\n')
		print("#"*3, mystr, '#'*3)

	def header(self, mystr):
		s = 7
		lstr = len(mystr) +2
		width = lstr+s*2+2
		print("@"*width)
		print(str("{0:1}{2:^"+str(s)+"}{1:^"+str(lstr)+"}{2:^"+str(s)+"}{0:1}").format("@",mystr, ' '*s))
		print("@"*width)

	def getNumInRange(self, a,b):
		choice = None
		maxn = max([a,b])
		minn = min([a,b])
		inputstring = 'Please enter a number between '+str(a) + ' ' + str(b) + ' or press enter to skip: '
		while True:
			r = input(inputstring)
			if r == '':
				print('Sentinal recieved - ignoring and returning.')
				choice = 0
				return choice
			try:
				choice = float(r)
				if choice <= maxn and choice >= minn:
					return choice
			except ValueError:
				print("ValueError, improper-input. Numbers only please, within the appropriate range.")

	def getMDY(self, end=False):
		x = ''
		date = None
		while type(date) != datetime.datetime:
			try:
				if end:
					print("Press ENTER if the start and end DATE are the same.")
				k = input("Your Date: ")
				if end and k == '':
					return None
				date = datetime.datetime.strptime(k, "%m/%d/%Y")
				return date
			except KeyboardInterrupt:
				print("Inturrupt Recieved")
				raise KeyboardInterrupt
			except:
				print("Invalid Format. Enter date in MM/DD/YYYY format.")
	def getcsv(self, path):
		with open(path, 'r') as f:
			df = pandas.read_csv(f)
		return df

class ripItUp(AsciiGUI):
	# By Orange Juice
	def __init__(self, args,**passed):
		super().__init__(args, getrootdir=True)

		self.path_data_to_cut = passed.pop("path_data_to_cut", '')
		self.path_data_to_subset = passed.pop("path_data_to_subset", '')


		self.cwd = os.getcwd()
		if self.path_data_to_cut == '':
			self.header("Select larger dataset to take a subset of (i.e. global analysis)")
			self.path_data_to_cut = self.fileDirectorySelector()
		self.data_to_cut = self.getcsv(self.path_data_to_cut)

		if self.path_data_to_subset == '':
			self.header('Now select simple dataset to use as a criteria for the larger datatset')
			self.path_data_to_subset = self.fileDirectorySelector()
		self.data_to_subset = self.getcsv(self.path_data_to_subset)

	def select_n_points(self, tolerance):
		
		n = 25

		self.data_to_subset[x] = pandas.to_datetime(self.data_to_subset[x], format="%Y-%m-%d %H:%M:%S")
		self.data_to_subset = self.data_to_subset.sort_values(by=x)
		
		min_xdata = min(self.data_to_subset[x])
		xdata_for_fit = get_x_for_fit(self.data_to_subset, min_xdata.day, min_xdata.month, min_xdata.year, x)
		by_index = int(len(xdata_for_fit)/8)
		#print(xdata_for_fit)
		#print(self.data_to_subset[x])

		self.data_to_subset['Fittting x'] = xdata_for_fit


		graphed_xticks = [xdata_for_fit[by_index*i] for i in range(8)]
		xtick_conversion = [self.data_to_subset.loc[by_index*i,x].strftime("%Y-%m-%d %H:%M") for i in range(8)]
		total_spline_approved = False	
		while total_spline_approved != True:
			plt.close()
			fig, ax = plt.subplots(figsize=(11,8.5))
			
			ax.scatter(xdata_for_fit, self.data_to_subset[y], color='blue', label=y)
			#plt.xticks(ticks=graphed_xticks, labels=[])
			ax.set_title("Data to fit")
			ax.set_xlabel("Seconds since "+str(min_xdata.month)+'/'+str(min_xdata.day)+ '/'+ str(min_xdata.year))
			ax.set_ylabel("Subset Metric")
			#ax.set_ylim(-1.6, -.6) # 9_14
			#ax.set_ylim(-.5, -.1)   # 12_10_20
			try:

				ax.scatter(xdata,ydata, color='red', label='Last Spline Selection')
			except:
				pass
			ax.grid(True)
			ax.legend(loc='best')

			#plt.show()
			self.header("Choose 25 datapoints on the graph by clicking it.")
			try:
				tuples = plt.ginput(n, timeout=0)
			except Exception as e:
				print(e)

			#print(tuples)
			#sorted_tuples = tuples.sort(key=lambda x: x[0])
			#print(sorted_tuples)

			xdata,ydata = map(list,zip(*tuples))
			try:
				ppoly_instance = spline(xdata,ydata)
			except ValueError as e:
				print(e, "Retry selection.")
				continue

			self.data_to_subset['spline'] = ppoly_instance(xdata_for_fit)

			contourline = self.data_to_subset['spline'].values
			
			useraccepted = False
			while useraccepted != True:
				cmin = contourline-tolerance
				cmax = contourline+tolerance
				self.data_to_subset['spline min'] =cmin
				self.data_to_subset['spline max'] =cmax

				plt.close()
				fig, ax = plt.subplots(figsize=(11,8.5))

				ax.fill_between(xdata_for_fit, cmin, cmax, color='aqua', alpha=0.5, label='Acceptance region')

				ax.scatter(xdata_for_fit, self.data_to_subset[y], color='blue', label=y)
				ax.plot(xdata_for_fit, self.data_to_subset['spline'], color='magenta', label='Cubic Spline')
				#plt.xticks(ticks=graphed_xticks, labels=[])
				ax.set_title("Data to fit")
				ax.set_xlabel("Seconds since "+str(min_xdata.month)+'/'+str(min_xdata.day)+ '/'+ str(min_xdata.year))
				ax.set_ylabel("Subset Metric")
				#ax.set_ylim(-1.6, -.6) # 9_14
				#ax.set_ylim(-.5, -.1) # 12_10_20

				ax.legend(loc='best')
				ax.grid(True)
				plt.show()
				useraccepted = input("Do you need to update the width of the acceptance region? [Y/N]: ")
				useraccepted = False if useraccepted.upper() == 'Y' else True
				if not useraccepted:
					print("Current tolerance region is:", tolerance, 'wide.')
					try:
						tolerance = float(input("Enter new tolerance: "))
					except ValueError:
						print("Improper value.")

			total_spline_approved = input("Do you accept the current spline? [Y/N]: ")
			total_spline_approved = True if total_spline_approved.upper() == 'Y' else False
			if total_spline_approved == False:
				nnew = input("Do you need to increase number of spline points? [Y/N]: ")
				nnew = True if nnew.upper() == 'Y' else False
				if nnew:
					print("Current number of user-selected points is:", n)
					n = int(input("Input the number of desired points: "))

		print("Selected data is in a dataframe, and now returning.")
		with open('spline_df_for_ellie.csv', 'w') as f:
			self.data_to_subset.to_csv(f)
		os.chdir(self.cwd)
		return self.data_to_subset
		#exit()


def main(tolerance=.3, neededpath='', global_analysis=''):
	a = ripItUp([], path_data_to_cut=global_analysis, path_data_to_subset=neededpath)
	df = a.select_n_points(tolerance)
	return df

def nearest(test_val, iterable): 
        # In an interable data-structure, find the nearest to the 
        # value presented.
        return min(iterable, key=lambda x: abs(x - test_val))

def get_x_for_fit(trimmed, Sd, Sm, Sy, t):
	"""
	Get the x data (of type datetime) into a format that scipy can interpret (seconds from the start of the day)
	
	"""


	end_time = (max(trimmed[t].tolist())-datetime.datetime(year=Sy, month=Sm, day=Sd)).total_seconds()
	
	start_time = (min(trimmed[t].tolist())-datetime.datetime(year=Sy, month=Sm, day=Sd)).total_seconds()

	timestamp_list = trimmed[t].tolist()
	timesteps = []

	"""
	# I found a brilliant way to overcomplicate things,
	#	And I leave this here for future reference.
	for index, val in enumerate(timestamp_list):
		if index == len(timestamp_list)-2:
			break
		timesteps.append((timestamp_list[index+1]-val).total_seconds())
		
	avg_timestep = numpy.mean(timesteps)"""

	xdata_for_fit = numpy.arange(start_time, end_time, (end_time-start_time)/len(timestamp_list)).tolist()
	if len(xdata_for_fit) != len(timestamp_list):
		if len(xdata_for_fit) > len(timestamp_list):
			xdata_for_fit = xdata_for_fit[:len(timestamp_list)]
		else:

			print("#"*50,"\n xdata for fit len:", len(xdata_for_fit), '\n',xdata_for_fit)
			print("#"*50,"\n timestamp list len:", len(timestamp_list), '\n', timestamp_list)

			print("#"*50,"\n timestamp list len:", len(timestamp_list))
			print("#"*50,"\n xdata for fit len:", len(xdata_for_fit))
			raise ValueError("Can not get xdata for fit.")

	return xdata_for_fit
if __name__ == "__main__":
    df = main()

    if True:
        accepted = df[(df['spline min'] < df[y]) & (df['spline max'] > df[y])]
        rejected = df[(df['spline min'] > df[y]) & (df['spline max'] < df[y])]
        with open('accepted_data.csv', 'w') as f:
            accepted.to_csv(f)
        with open('rejected_data.csv', 'w') as f:
            rejected.to_csv(f)

