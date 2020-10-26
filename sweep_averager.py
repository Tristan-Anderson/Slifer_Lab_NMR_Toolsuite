import sys, pandas, numpy, os, datetime
from statistics import mode
#sys.path.insert(0,'/home/kb/Programming/utils')
#from andertools import ta1parser

"""
# Authoring, or whatever.

Tristan Anderson
tja1015@wildcats.unh.edu

Do you want to spend the rest of your life 
selling sugared water or do you want a chance 
to change the world?


Proceed Formally.
"""


# Program Explanation:
"""
Takes the .ta1 files of the first child directories,
and creates an average of them, writing it in a parent directory.
"""

global time_colname, primary_thermometer_colname,secondary_thermometer_colname,\
        magnet_psu_amperage_colname,sweep_centroid_colname,sweep_width_colname,\
        system_status_colname,system_status_nulls,system_null_status_directory,\
        terminal_colname
time_colname = "Time"
primary_thermometer_colname = "CCX.T3 (K)"
secondary_thermometer_colname = "Vapor Pressure Temperature (K)"
magnet_psu_amperage_colname = "Magnet Current (A)"
sweep_centroid_colname  = "Central Freq (MHz)"
sweep_width_colname = "Freq Span (MHz)"
system_status_colname = "NMR Status"
system_status_nulls = ['---']
system_null_status_directory = 'null_status'
terminal_colname = 'NMR Data' # This is the column below, and after which sweep data
                                #   data accumulates.

def ta1parser(path,columns=[], delimeter='\t'):
    #import datetime
    #from statistics import mode
    header = []
    h2 = []
    tf_file = []

    with open(path, 'r') as f:
        for index, line in enumerate(f):
            ##########################################
            """
                This if-else block extracts data from
                the data files that are given to the
                gui. It reads and interprets the header
                of the file, and will attempt to use
                the data for later on.
            """
            ######### HEADER EXTRACTION #############
            if index == 0:
                dateish = line.split('\t')[1]
                #2019-12-19 23:59:47
                TE_DATE = datetime.datetime.strptime(dateish, "%Y-%m-%d %H:%M:%S")

                #Time\t2019-12-19 22:01:07\tVapor Pressure Temperature (K)\t1.219363
                vp = line.split('\t')[3] # Vapor pressure

                try:
                    float(vp)
                    vptf = True
                except:
                    vptf = False
            if index == 1:
                #Magnet Current (A)\t48.666000\tCCCS.T3 (K)\t2.860396
                I = line.split('\t')[1]
                # Get the primary thermistor
                t3 = line.split('\t')[3]
                
                try:
                    I = float(I)
                    itf = True
                except ValueError:
                    itf = False

                try:
                    float(t3)
                    t3tf = True
                except ValueError:
                    t3tf = False

                if t3tf and vptf:
                    T = round((float(vp)+float(t3))/2,4)
                elif t3tf and not vptf:
                    T = round((float(t3)),4)
                elif vptf and not t3tf:
                    T = round((float(vp)),4)
                elif not t3tf and not vptf:
                    T = ""
            if index == 2:
                # Central Freq (MHz)\t212.990000\tFreq Span (MHz)\t0.400000
                try:
                    cfq = float(line.split('\t')[1])
                    fqs = float(line.split('\t')[3])

                except ValueError:
                    cfq = line.split('\t')[1]
                    fqs = line.split('\t')[3]
            ##########################################

            header.append(len(line.split(delimeter)))
            h2.append(line.split(delimeter))

        data_width = mode(header)
        
        for element in header:
            if element == data_width:
                tf_file.append(False)
            else:
                tf_file.append(True)
        
        lines_to_skip = 0
        while any(tf_file[lines_to_skip:]):  # While any values are true, iterate through it, deleting the first element of the list.
            lines_to_skip += 1
            
    ta1f =[]
    for index, element in enumerate(h2[lines_to_skip:]):
        ta1f.append([])
        for i in range(len(element)):
            ta1f[index].append(float(element[i]))
    
    return {"data":ta1f, "lines_to_skip":lines_to_skip, "Temperature":T, "Mag Current":I, "Central Freq (MHz)":cfq, "Freq Span (MHz)":fqs, "Time":dateish}

def ta1filewriter(f, y, x, T, I,cfq,fqspan, date="None", nmr_status="Baseline"):
    f.write(time_colname+"\t"+date+'\t')
    f.write(secondary_thermometer_colname+"\t"+str(T)+'\n')
    f.write(magnet_psu_amperage_colname+"\t"+str(I)+'\t')
    f.write(primary_thermometer_colname+"\t"+str(T)+'\n')
    f.write(sweep_centroid_colname+"\t"+str(cfq)+'\t')
    f.write(sweep_width_colname+"\t"+str(fqspan)+'\n')
    f.write(system_status_colname+"\t"+str(nmr_status)+'\n')
    f.write("#\tMHz\t"+terminal_colname+"\n")
    for index, val in enumerate(y):
        f.write(str(x[index])+"\t"+ str(val)+"\n")

def kc1(filesdir, dn='', dump='.', additive="TE"):
	"""
	Takes the .ta1 files within filesdir, and creates an average of them
	"""
	files_to_combine = []
	# Given a file directory, look at the files within said directory
	for file in os.listdir(filesdir):
	    if file.endswith('.ta1'):		# If they're of the .ta1 file type, I've probably created them
	        files_to_combine.append(file)
	if len(files_to_combine) == 0:		# If theres no files in the directory, skip it
		print("No files in", filesdir, "skipping...")
		return False

	whoops = {}							# Take the kernel from the .ta1 file parser, and save it in a dictonary.
	for path in files_to_combine:
		#{"data":ta1f, "lines_to_skip":lines_to_skip, "Temperature":T, "Mag Current":I, "Central Freq (MHz)":cfq, "Freq Span (MHz)":fqs}
		whoops[path.split('.')[0]] = ta1parser(filesdir+path)

	# HERE is where the headers for the .ta1 columns can be changed. You can modify this without having to propogate these changes through
	#		the entire NMR suite.
	header = ["MHz", "NMR Data"]
	x = header[0]
	y = header[1]
	dfdict = {}
	xl = []
	yl = []
	dates = []
	avgt = 0
	ac=0
	icurent = 0
	ic =0
	cfq = 0
	cc = 0 
	freqspan = 0
	fc = 0
	for key in whoops:
		# Make a dataframe for the nmr sweeps
		dfdict[key] = pandas.DataFrame(whoops[key]["data"], columns=header)

		# The Try/Except tree here is a form of averaging across all of these files.
		try:
			# Add the temperature to itself
			avgt += whoops[key]["Temperature"]
			# Count that we've added something
			ac += 1
		except:
			pass
		try:
			# Passthrough current.
			# DANGER.
			icurent = whoops[key]["Mag Current"]
		except:
			pass
		try:
			cfq += whoops[key]["Central Freq (MHz)"]
			# Count that we've added something
			cc += 1
		except:
			pass
		try:
			freqspan += whoops[key]["Freq Span (MHz)"]
			# Count that we've added something
			fc += 1
		except:
			pass
		try:
			dates.append(whoops[key]["Time"])
		except:
			pass
		xl.append(dfdict[key][x].values)
		yl.append(dfdict[key][y].values)
	try:
		avgt, icurrent, cfq, freqspan = avgt/ac, icurent, cfq/cc, freqspan/fc
	except ZeroDivisionError:
		print("ZDE for: ", dn)
	
	da = []
	for dateish in dates:
		# Gets the date
		da.append(datetime.datetime.strptime(dateish, "%Y-%m-%d %H:%M:%S"))

	xavg = numpy.mean(xl, axis=0)
	yavg = numpy.mean(yl, axis=0)
	os.chdir(dump)
	with open(dn+additive+"_average.ta1", 'w') as f:
		ta1filewriter(f, yavg, xavg, avgt, icurent, cfq, freqspan,date=(min(da)+(max(da)-min(da))/2).strftime("%Y-%m-%d %H:%M:%S"))

def avg_nested_dirs(filesdir):
    additive=''.join(filesdir.split('/')[-3]) # Is a string of the element between  /^^/ <- there. Useful in making the user type less.
    for (dirpath, dirnames, filenames) in os.walk(filesdir):
        dirnames = dirnames
        break
    for dirname in dirnames:
        kc1(filesdir+dirname+'/', dn=dirname+'_', dump=filesdir, additive=additive)
    print("Avering nested directories complete.")

def avg_single_dir(filesdir):
    additive=''.join(filesdir.split('/')[-3])
    kc1(filesdir, dump=filesdir, additive=additive)
    print("Avering single directory complete.")
# A place where there are a bunch of child directories containing .ta1 files (organized by te_directory_sorter.py)
# And averages each child directory into a single file which it writes in parent directory
"""bldirs = "sep_2020/data_record_9-12-2020/TE/912_514p/"
additive=''.join(bldirs.split('/')[-3]) # Is a string of the element between  /^^/ <- there. Useful in making the user type less.
kc1("sep_2020/data_record_9-14-2020/TE/914_641_650p_for_karl/", dump="sep_2020/data_record_9-14-2020/TE/914_641_650p_for_karl/", additive='TE_')
exit()
for (dirpath, dirnames, filenames) in os.walk(bldirs):
	dirnames = dirnames
	break
for dirname in dirnames:
	kc1(bldirs+dirname+'/', dn=dirname+'_', dump=bldirs, additive=additive)
"""