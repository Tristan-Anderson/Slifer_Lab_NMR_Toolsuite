# Tristan Anderson
# tja1015@wildcats.unh.edu

"""
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
	hours = ts.pop("hours",0)
	minutes = ts.pop("minutes",0)
	seconds = ts.pop("seconds",0)
	timestep = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
	for (dirpath, dirnames, filenames) in os.walk(location):
		fnames = filenames
		break

	broken = []
	alldates = []
	for file in fnames:
		# Extract all of the dates out of the filenames in the directory.
		alldates.append(datetime.datetime.strptime(''.join(file.split('.')[0].split('_')[1:]),'%Y%m%d%H%M%S'))

	minalldates = min(alldates)
	prevstepalldates = minalldates
	stepalldates = minalldates+timestep
	print(minalldates, stepalldates)
	while prevstepalldates < max(alldates):
		os.chdir(location)

		#Form the naming for the directory
		ampm = datetime.datetime.strftime(stepalldates, "%p")
		ap = "p" if ampm == "PM" else "a"
		directoryname = datetime.datetime.strftime(prevstepalldates,"%m%d_%H%M%S_")+datetime.datetime.strftime(stepalldates,"%H%M%S")+ap+'/'

		

		# Select the right files to move
		files_to_move = []
		for index, date in enumerate(alldates):
			# If the specific date is within the correct range
			if date >= prevstepalldates and date <= stepalldates:
				# add it to the list of files to move.
				files_to_move.append(datetime.datetime.strftime(date, "%Y_%m_%d_%H_%M_%S"))
		if len(files_to_move) > 0:
			#print(len(files_to_move), "creating", directoryname)
			# Make the directory
			try:
				os.chdir(directoryname)
				os.chdir(location)
			except FileNotFoundError:
				os.mkdir(directoryname)
			# one by one move the files.
			#print(files_to_move)
			for f in files_to_move:
				#print("Hello")
				#print(glob.glob(location+'*'+f+'*'), f)
				try:
					actual_file = glob.glob(location+'*'+f+'*')[0]
				except IndexError:
					# If she ain't were she's supposed to be, she's been moved....
					#print(f, "has already been moved.")
					continue
				actual_file_name = actual_file.split('/')[-1]
				shutil.move(actual_file, location+directoryname+actual_file_name)
		prevstepalldates = stepalldates
		stepalldates += timestep

def unshelf(location):
	"""
	From a shelved 2-D file structure, go into the
	children of the "location" directory, and move
	them to the parent/root/"location" directory.
	"""
	home = location
	
	for (dirpath, dirnames, filenames) in os.walk(location)
		dirnames = dirnames
		break
	for child in dirnames:
		os.chdir(child)
		for (dirpath, dirnames, filenames) in os.walk(location)
			filenames = filenames
			break
		for file in filenames:
			shutil.move