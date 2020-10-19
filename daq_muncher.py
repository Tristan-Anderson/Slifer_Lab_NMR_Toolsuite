import numpy, pandas, os
from datetime import datetime
"""
Tristan Anderson
tris31299@gmail.com

Proceed Formally.
"""

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
                header = line.split('\t')
                #print(header) # You can print this but it's just a list.
                for index, val in enumerate(header):
                    # Get the primary thermsitor
                    if val == primary_thermometer_colname:
                        cccst3i = index
                    # Get the time it was taken at
                    if val == time_colname:
                        timei=index
                    # Get a secondary thermistor
                    if val == secondary_thermometer_colname:
                        vpti=index
                    # Get the magnet current
                    if val == magnet_psu_amperage_colname:
                        mci = index
                    # Get the NMR data, and sometimes theres the '\n' at the end
                    #   Which can be problamatic.
                    try:
                        nmri
                    except NameError:
                        try:
                            if val == terminal_colname:
                                nmri = index 
                            nmri
                        except NameError:
                            if val == terminal_colname+'\n':
                                nmri = index
                    # Terminal daq header, but specifies where NMR data starts 
                    if val == terminal_colname:
                        nmri = index 
                    # Where is the sweep centered at?
                    if val == sweep_centroid_colname:
                        cfi = index
                    # How wide is the fequency sweep?
                    if val == sweep_width_colname:
                        fqsi = index
                    # What is the DAQ doing right now?
                    #   "TE", "Baseline", "Enhanced", "---": no_nmr_status
                    if val == system_status_colname:
                        nmrsi = index
                header = line.split('\t')[:-1]
                continue
            l = line.split('\t')
            if '\n' in l[timei]:
                # If the Time column for some reason has a newline
                # That means there's no data recorded after that entry which
                # since it's always first means that theres no subsequent entries
                continue
            if "NaN" in l[nmri:]:
                # If we have a NaN in our DAQ NMR sweep, something VERY wrong happened.
                #print("DAQ NMR Sweep Extractor: *** ERROR: NMR sweep had a NaN in line", index, "in file", df_path)
                problem_children.append((index, df_path))
                continue
            
            # Saves each sweep as an entry in a dictonary structure
            daq_dict[index] = {
                time_colname:datetime.strptime(l[timei],"%m/%d/%Y %I:%M:%S %p"),
                secondary_thermometer_colname:l[vpti],               #### <- As should this.
                magnet_psu_amperage_colname:l[mci],
                terminal_colname:numpy.array(l[nmri:], dtype=numpy.float64),
                primary_thermometer_colname:l[cccst3i],                                #### <- this should be user selected
                sweep_centroid_colname:l[cfi],            
                sweep_width_colname:l[fqsi],                              
                system_status_colname:l[nmrsi]
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
        xc = float(daq_dict[key][sweep_centroid_colname])
        # Finds the span of the sweep
        dx = float(daq_dict[key][sweep_width_colname])
        # creates x-min
        xm = xc-dx/2
        # creates x-max
        xM = xc+dx/2
        try:
            # Creates x by sweep width divided by entries in the nmr data array
            x = numpy.arange(xm, xM, step=dx/len(daq_dict[key][terminal_colname]))
        except ZeroDivisionError:
            # If for some reason the NMR data array failed to be assigned NMR sweep values,
            # Then a zero division error happens.
            # If that happens, then bail on creating the file for this DAQ entry.
            continue
        # If the status is something important
        if daq_dict[key][system_status_colname] not in system_status_nulls:
            if dulya == True:
                try:
                    os.chdir("dulya")
                except:
                    os.mkdir("dulya")
                    os.chdir('dulya')
                with open("VME_"+datetime.strftime(daq_dict[key][time_colname],"%Y_%m_%d_%H_%M_%S")+".cd1", 'w') as f:
                    filewriter(f, daq_dict, key, x, dulya=True)
                os.chdir('..')
                continue
            # Save the files in a directory called /fdump/ + whatever was important (TE/baseline/Polarization)
            try:
                os.chdir(daq_dict[key][system_status_colname])
            except FileNotFoundError:
                # If the directory doesn't exist, then make it
                os.mkdir(daq_dict[key][system_status_colname])
                os.chdir(daq_dict[key][system_status_colname])

            with open("VME_"+datetime.strftime(daq_dict[key][time_colname],"%Y_%m_%d_%H_%M_%S")+".ta1", 'w') as f:
                filewriter(f, daq_dict, key, x)
            # Hop back into the file dump directory
            os.chdir('..') 
        else:
            try:
                os.chdir(system_null_status_directory)
            except FileNotFoundError:
                os.mkdir(system_null_status_directory)
                os.chdir(system_null_status_directory)
            
            with open("VME_"+datetime.strftime(daq_dict[key][time_colname],"%Y_%m_%d_%H_%M_%S")+".ta1", 'w') as f:
                filewriter(f, daq_dict, key, x)
            
            os.chdir('..')
            
def filewriter(f, daq_dict, key, x, dulya=False):
    if dulya:
        for index, val in enumerate(daq_dict[key]["NMR Data"]):
            f.write(str(val)+"\n")
        return True

    # Write the header
    f.write(time_colname+"\t"+str(daq_dict[key][time_colname])+'\t')
    f.write(secondary_thermometer_colname+"\t"+str(daq_dict[key][secondary_thermometer_colname])+'\n')
    f.write(magnet_psu_amperage_colname+"\t"+str(daq_dict[key][magnet_psu_amperage_colname])+'\t')
    f.write(primary_thermometer_colname+"\t"+str(daq_dict[key][primary_thermometer_colname])+'\n')
    f.write(sweep_centroid_colname+"\t"+str(daq_dict[key][sweep_centroid_colname])+'\t')
    f.write(sweep_width_colname+"\t"+str(daq_dict[key][sweep_width_colname])+'\n')
    f.write(system_status_colname+"\t"+str(daq_dict[key][system_status_colname])+'\n')
    f.write("#\tMHz\t"+terminal_colname+"\n")
    # Write the rest of the file
    for index, val in enumerate(daq_dict[key][terminal_colname]):
        f.write(str(x[index])+"\t"+ str(val)+"\n")


def directory(datapath, filedump, cwd):
    raw_data = datapath # Expects a clean file structure with a few DAQ csv's in it
    fdump = filedump         # Expects a clean file directory where it can create folders called
                                # The DAQ csv's name, and dump the appropriate data.
    home = cwd              # For returning to home, but probably not useful. (it's very useful)

    # home
    raws = []
    for file in os.listdir(raw_data):   # Get all of the files
        if file.endswith('.csv'):       # That end in csv
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
    for index, file in enumerate(raws):
        filestuff = ' '.join(["#File", file, "In progress.#"])
        print('#'*len(filestuff))
        print(filestuff)
        print('#'*len(filestuff))
        file_muncher(file, raw_data, fdump+dumps[index])

def single_file(datafile, filedump):
    datadir = '/'.join((datafile.split('/')[:-2]))+'/'
    #print(datadir)
    file_muncher(datafile,datadir,filedump)




############ Column Names ############
# Future work is to be done here to have
# a master.ini files with a bunch of global declarations
# to practice good string-variable softcoding, 
# as opposed to the hardcoding that is downstream
# from the execution of this program


""" Psssst.... Hey you! user! Look here:
        ########################
        #     DO NOT MODIFY    #       
        #  WITHOUT CONSULTING  #
        #    DOCUMENTATION.    #
        ########################
               
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
######################################

"""
cwd = os.getcwd()+'/'
raw_data = cwd+"raw_data/" # Expects a clean file structure with a few DAQ csv's in it
fdump = cwd+"vme/"         # Expects a clean file directory where it can create folders called
                            # The DAQ csv's name, and dump the appropriate data.
home = cwd              # For returning to home, but probably not useful. (it's very useful)

# home
raws = []
for file in os.listdir(raw_data):   # Get all of the files
    if file.endswith('.csv'):       # That end in csv
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
for index, file in enumerate(raws):
    filestuff = ' '.join(["#File", file, "In progress.#"])
    print('#'*len(filestuff))
    print(filestuff)
    print('#'*len(filestuff))
    file_muncher(file, raw_data, fdump+dumps[index])
                                # This ^^^^^^^^^^^^ Is possible because the dumps list and raws are parralelly indexable (:
"""