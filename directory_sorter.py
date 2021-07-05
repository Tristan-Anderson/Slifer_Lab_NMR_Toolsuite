"""
Tristan Anderson
takc1nqa@gmail.com
tanderson@vt.edu

Sometimes, python lets you be just lazy enough to do something like this
"""

#############################
##DO NOT USE IN A DIRECTORY##
##WITH SYMLINKS. I DONT KNOW#
#####WHAT COULD HAPPEN.######
#############################


# This program will look at the .ta1 data generated from DAQ csv's, 
# 	and organize it in user-specified datetime timedelta increments.
# This is most useful for averaging TE sweeps for weak signal NMR;
#	where a peak would rise from the noise floor after 1000+ sweeps.

# This program takes a 1d file directory and turns it into a 2d file directory.


import os, datetime,shutil, glob




def shelf(location, **ts):
	"""
	Takes all of the .ta1 files and "shelves" them
	into tiny directories, the timespan of which
	is regulated by the user
	"""
	location += '/' # needs to be marked as a directory


	hours = ts.pop("hours",0)
	minutes = ts.pop("minutes",0)
	seconds = ts.pop("seconds",0)
	if hours==minutes==seconds==0:
		print("Invalid selection of time width.")
		print("Escaping.")
		return False
	timestep = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
	for (dirpath, dirnames, filenames) in os.walk(location):
		fnames = filenames
		break
	print(location)

	broken = []
	alldates = []
	for file in fnames:
		# Extract all of the dates out of the filenames in the directory.
		alldates.append(datetime.datetime.strptime(''.join(file.split('.')[0].split('_')[1:]),'%Y%m%d%H%M%S'))
	
	minalldates = min(alldates)
	start_of_daterange = minalldates
	end_of_daterange = minalldates+timestep
	while start_of_daterange < max(alldates):
		#print('stepping into loop: 58: ', location, '\nStart of date range:', start_of_daterange, 'end of daterange:', end_of_daterange)
		os.chdir(location)

		#Form the naming for the directory
		ampm = datetime.datetime.strftime(end_of_daterange, "%p")
		ap = "p" if ampm == "PM" else "a"
		#directoryname = datetime.datetime.strftime(start_of_daterange,"%m%d_%H%M%S_")+datetime.datetime.strftime(end_of_daterange,"%H%M%S")+ap+'/'

		

		# Select the right files to move
		files_to_move = []
		subsection = []
		for index, date in enumerate(alldates):
			# If the specific date is within the correct range
			if date >= start_of_daterange and date <= end_of_daterange:
				# collect a subsection
				subsection.append(date)
				# add the subsection to the list of files to move.
				files_to_move.append(datetime.datetime.strftime(date, "%Y_%m_%d_%H_%M_%S"))

		#print('79: files to move:', files_to_move)
		if len(files_to_move) > 0:
			directoryname = datetime.datetime.strftime(min(subsection),"%m%d_%H%M%S_")+datetime.datetime.strftime(max(subsection),"%m%d_%H%M%S")+ap+'/'

			#print(len(files_to_move), "creating", directoryname)
			# Make the directory
			try:
				os.chdir(directoryname)
				os.chdir(location)
			except FileNotFoundError:
				os.mkdir(directoryname)
			# one by one move the files.
			for f in files_to_move:
				#print("Hello")
				#print(glob.glob(location+'*'+f+'*'), f)
				try:
					actual_file = glob.glob(location+'*'+f+'*')[0]
				except IndexError as e:
					# If she ain't were she's supposed to be, she's been moved....
					print(e, f)
					#print(f, "has already been moved.")
					continue
				actual_file_name = actual_file.split('/')[-1]
				shutil.move(actual_file, location+directoryname+actual_file_name)
		start_of_daterange = end_of_daterange
		end_of_daterange += timestep
	print("Shelving complete.")

def unshelf(location):
	"""
	From a shelved 2-D file structure, go into the
	children of the "location" directory, and move
	them to the parent/root/"location" directory.
	"""
	location += '/' # needs to be marked as a directory

	home = os.getcwd()
	os.chdir(location)
	for (dirpath, dirnames, filenames) in os.walk(location):
		dirnames = dirnames
		break
	for child in dirnames:
		d = location+child+'/'
		print(d)
		os.chdir(d)
		for (dirpath, dirnames, filenames) in os.walk(d):
			for file in filenames:
				shutil.move(d+file, location+file)
			break
		os.chdir(location)
		os.rmdir(d)
	os.chdir(home)
	print("Unshelving Complete.")

"""
USEAGE:

shelf(PATH, hours=h, minutes=m, seconds=s)
unshelf(PATH)

"""