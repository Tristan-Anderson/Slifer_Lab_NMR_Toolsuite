"""
Tristan Anderson
takc1nqa@gmail.com
tanderson@vt.edu
"""
import numpy, pandas, os, variablenames
from datetime import datetime

# Fortune:
"""
Computers will not be perfected until they can compute
how much more than the estimate the job will cost.
"""

# Explanation:
"""
When placed within a directory that contains tab-delimited .csv's
this program expects a DAQ-like file format, with nmr data after a final "NMR Data"
column label, and then it creates a .s1p-like file with useful temperatures, and magnetic fields
(T_vp, T_t3, B, etc) all contianed in the single row of the DAQ-like file.

This creates .ta1 files which are a spin-off of the .s1p files.

This program catagorizes the output files by "NMR Status", so when you set a
directory that contains the .csv's, and a directory for the .ta1's
"""

file_delimeter = '\t'

def to_kelvin(c):
    return c+273.15

def file_muncher(df_path, data, fdump, dulya=False):
    daq_dict = {}
    
    # Go into the data directory
    os.chdir(data)
    # Open the DAQ file which was requested
    problem_children = []
    with open(df_path,'r') as f:
        # Enumerate the file
        for lf, l in enumerate(f):
            pass
    ten_percent = round((lf+1)/10)
    with open(df_path, 'r') as f:
        for index, line in enumerate(f):
            if index % ten_percent == 0:
                print(int(index*10/(ten_percent)), "precent complete reading.")
            # If its the first line: we know its the header
            if index == 0:
                topline = line
                header = line.split(file_delimeter)
                #print(header) # You can print this but it's just a list.
                for index, val in enumerate(header):
                    # Get the primary thermsitor
                    if val == variablenames.dmsa_primary_thermometer_colname:
                        cccst3i = index
                    # Get the time it was taken at
                    if val == variablenames.dmsa_time_colname:
                        timei=index
                    # Get a secondary thermistor
                    if val == variablenames.dmsa_secondary_thermometer_colname:
                        vpti=index
                    # Get the magnet current
                    if val == variablenames.dmsa_magnet_psu_amperage_colname:
                        mci = index
                    # Get the NMR data, and sometimes theres the '\n' at the end
                    #   Which can be problamatic.
                    try:
                        nmri
                    except NameError:
                        try:
                            if val == variablenames.dmsa_terminal_colname:
                                nmri = index 
                            nmri
                        except NameError:
                            if val == variablenames.dmsa_terminal_colname+'\n':
                                nmri = index
                    # Terminal daq header, but specifies where NMR data starts 
                    if val == variablenames.dmsa_terminal_colname:
                        nmri = index 
                    # Where is the sweep centered at?
                    if val == variablenames.dmsa_sweep_centroid_colname:
                        cfi = index
                    # How wide is the fequency sweep?
                    if val == variablenames.dmsa_sweep_width_colname:
                        fqsi = index
                    # What is the DAQ doing right now?
                    #   "TE", "Baseline", "Enhanced", "---": no_nmr_status
                    if val == variablenames.dmsa_system_status_colname:
                        nmrsi = index
                header = line.split(file_delimeter)[:-1]
                continue
            l = line.split(file_delimeter)
            try:
                if '\n' in l[timei]:
                    # If the Time column for some reason has a newline
                    # That means there's no data recorded after that entry which
                    # since it's always first means that theres no subsequent entries
                    continue
            except Exception as e:
                print("Error occured in file:", df_path)
                print("During Header-Parsing.")
                print("Exception:", e)
                print("File Header:", header)
                print("Listed header (Look closely for POSIX CNTRL and delimeter characters: \\t, \\n, \',\' ... etc)")
                print(topline)
                return True
            try:
                if "NaN" in l[nmri:]:
                    # If we have a NaN in our DAQ NMR sweep, something VERY wrong happened.
                    #print("DAQ NMR Sweep Extractor: *** ERROR: NMR sweep had a NaN in line", index, "in file", df_path)
                    print(df_path.split('/')[-1],"had error on line", index)
                    continue
            except Exception as e:
                print("Error occured in file:", df_path)
                print("During Header-Parsing.")
                print("Exception:", e)
                print("File Header:", header)
                print("Listed header (Look closely for POSIX CNTRL and delimeter characters: \\t, \\n \',\'... etc)")
                print(topline)
                return True

            try:
                NMR_DATA = numpy.array(l[nmri:], dtype=numpy.float64)
                dt = datetime.strptime(l[timei],"%m/%d/%Y %I:%M:%S %p")
            except ValueError as e:
                # If we can't create the array of NMR data. Don't waste time making a file about it.
                print(df_path.split('/')[-1],"had error on line", index, 'error:', e)
                continue
            
            # Saves each sweep as an entry in a dictonary structure
            daq_dict[index] = {
                variablenames.dmsa_time_colname:dt,
                variablenames.dmsa_secondary_thermometer_colname:l[vpti],               #### <- As should this.
                variablenames.dmsa_magnet_psu_amperage_colname:l[mci],
                variablenames.dmsa_terminal_colname:NMR_DATA,
                variablenames.dmsa_primary_thermometer_colname:l[cccst3i],                                #### <- this should be user selected
                variablenames.dmsa_sweep_centroid_colname:l[cfi],            
                variablenames.dmsa_sweep_width_colname:l[fqsi],                              
                variablenames.dmsa_system_status_colname:l[nmrsi]
                            }
        
    # Backs out one level from the data directory        
    os.chdir('..')

    # Jumps into the Directory assigned to dump the data
    os.chdir(fdump)
    #from pprint import pprint
    #pprint(daq_dict)
    #exit()
    len_daq_dict =  len(daq_dict)
    ten_percent = round(len_daq_dict/10)
    # Opens the dictonary above
    i = 0
    for key in daq_dict:# [key]
        i += 1
        if i % ten_percent == 0:
            print(int(i*10/(ten_percent)), "precent completed writing.")
        # Finds the centroid
        xc = float(daq_dict[key][variablenames.dmsa_sweep_centroid_colname])
        # Finds the span of the sweep
        dx = float(daq_dict[key][variablenames.dmsa_sweep_width_colname])
        # creates x-min
        xm = xc-dx/2
        # creates x-max
        xM = xc+dx/2
        try:
            # Creates x by sweep width divided by entries in the nmr data array
            x = numpy.arange(xm, xM, step=dx/len(daq_dict[key][variablenames.dmsa_terminal_colname]))
        except ZeroDivisionError:
            # If for some reason the NMR data array failed to be assigned NMR sweep values,
            # Then a zero division error happens.
            # If that happens, then bail on creating the file for this DAQ entry.
            continue
        # If the status is something important
        if daq_dict[key][variablenames.dmsa_system_status_colname] not in variablenames.dmsa_system_status_nulls:
            if dulya == True:
                try:
                    os.chdir("dulya")
                except:
                    os.mkdir("dulya")
                    os.chdir('dulya')
                with open("VME_"+datetime.strftime(daq_dict[key][variablenames.dmsa_time_colname],"%Y_%m_%d_%H_%M_%S")+".cd1", 'w') as f:
                    filewriter(f, daq_dict, key, x, dulya=True)
                os.chdir('..')
                continue
            # Save the files in a directory called /fdump/ + whatever was important (TE/baseline/Polarization)
            try:
                os.chdir(daq_dict[key][variablenames.dmsa_system_status_colname])
            except FileNotFoundError:
                # If the directory doesn't exist, then make it
                os.mkdir(daq_dict[key][variablenames.dmsa_system_status_colname])
                os.chdir(daq_dict[key][variablenames.dmsa_system_status_colname])

            with open("VME_"+datetime.strftime(daq_dict[key][variablenames.dmsa_time_colname],"%Y_%m_%d_%H_%M_%S")+".ta1", 'w') as f:
                filewriter(f, daq_dict, key, x)
            # Hop back into the file dump directory
            os.chdir('..') 
        else:
            try:
                os.chdir(variablenames.dmsa_system_null_status_directory)
            except FileNotFoundError:
                os.mkdir(variablenames.dmsa_system_null_status_directory)
                os.chdir(variablenames.dmsa_system_null_status_directory)
            
            with open("VME_"+datetime.strftime(daq_dict[key][variablenames.dmsa_time_colname],"%Y_%m_%d_%H_%M_%S")+".ta1", 'w') as f:
                filewriter(f, daq_dict, key, x)
            
            os.chdir('..')
            
def filewriter(f, daq_dict, key, x, dulya=False):
    if dulya:
        for index, val in enumerate(daq_dict[key]["NMR Data"]):
            f.write(str(val)+"\n")
        return True

    # Write the header
    f.write(variablenames.dmsa_time_colname+"\t"+str(daq_dict[key][variablenames.dmsa_time_colname])+'\t')
    f.write(variablenames.dmsa_secondary_thermometer_colname+"\t"+str(daq_dict[key][variablenames.dmsa_secondary_thermometer_colname])+'\n')
    f.write(variablenames.dmsa_magnet_psu_amperage_colname+"\t"+str(daq_dict[key][variablenames.dmsa_magnet_psu_amperage_colname])+'\t')
    f.write(variablenames.dmsa_primary_thermometer_colname+"\t"+str(daq_dict[key][variablenames.dmsa_primary_thermometer_colname])+'\n')
    f.write(variablenames.dmsa_sweep_centroid_colname+"\t"+str(daq_dict[key][variablenames.dmsa_sweep_centroid_colname])+'\t')
    f.write(variablenames.dmsa_sweep_width_colname+"\t"+str(daq_dict[key][variablenames.dmsa_sweep_width_colname])+'\n')
    f.write(variablenames.dmsa_system_status_colname+"\t"+str(daq_dict[key][variablenames.dmsa_system_status_colname])+'\n')
    f.write("#\tMHz\t"+variablenames.dmsa_terminal_colname+"\n")
    # Write the rest of the file
    for index, val in enumerate(daq_dict[key][variablenames.dmsa_terminal_colname]):
        f.write(str(x[index])+"\t"+ str(val)+"\n")

def directory(datapath, filedump, cwd):
    from multiprocessing import Pool, cpu_count
    processes = int(8*cpu_count()/10)
    print(processes, "Processing threads available, we're putting it to 80 %")
    raw_data = datapath # Expects a clean file structure with a few DAQ csv's in it
    fdump = filedump         # Expects a clean file directory where it can create folders called
                                # The DAQ csv's name, and dump the appropriate data.
    home = cwd              # For returning to home, but probably not useful. (it's very useful)

    # home
    raws = []
    for file in os.listdir(raw_data):   # Get all of the files
        if file.endswith('.csv') and 'abridged' not in file:       # That end in csv
            raws.append(file)           # Append daq csv to a list
    # file dump
    os.chdir(fdump)                     # chdir into file dump
    dumps = []
    for st in raws:                     # Get name of daq csv
        f = st.split('.')[0]            # Split the daq into its file name and extension, and just take its file name
        dumps.append(f)                 # Save the filename to a list
        try:
            os.mkdir(f)                 # Turn the filename into a directory
        except:
            # FileExistsError (Im pretty sure)
            pass
    print("Parsing", len(raws), ".csv files.")
    with Pool(processes=processes) as pool:
        result_objects = [pool.apply_async(file_muncher, args=(file, raw_data, fdump+dumps[index])) for index, file in enumerate(raws)]
        pool.close()
        pool.join()
    results = [r.get() for r in result_objects if r.get() != False]
    print("Complete.")

def single_file(datafile, filedump):
    datadir = '/'.join((datafile.split('/')[:-2]))+'/'
    #print(datadir)
    file_muncher(datafile,datadir,filedump)
    print("Complete.")
