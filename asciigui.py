"""
Tristan Anderson
tja1015@wildats.unh.edu

Proceed Formally.
"""

# This is an attempt at an ascii gui.


import variablenames
import gc, time # garbage
from tkinter import filedialog
import NMR_Analyzer as v
import daq_muncher, directory_sorter,sweep_averager,global_interpreter
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime, pandas, os, numpy

def getdir(cwd):
    for subdir, dirs, files in os.walk(cwd):
        break
    print("Current directory:", cwd)
    cleanfiles = []
    for f in files:
        if any(ext in f for ext in variablenames.agui_allowable_file_extensions):
            # If theres a match in the allowable extensions, then save it
            # Otherwise, dont.
            cleanfiles.append(f)

    filewidth = [len(i) for i in cleanfiles]
    try:
        filewidth = max(filewidth)+2
    except ValueError:
        filewidth = 0

    if filewidth < 7:
        filewidth = 7

    dwidth = [len(i) for i in dirs]
    try:
        dwidth = max(dwidth)+2
    except ValueError:
        dwidth= 2
    if dwidth < 13:
        dwidth = 13

    crossbar_width = filewidth+dwidth+3+9
    dirlongfile = len(dirs) > len(cleanfiles)
    fixeddirs = []
    fixedfiles = []
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

    print('#'*crossbar_width)
    print(str("{0:^1}{3:^8}{0:^1}{1:^"+str(filewidth)+"}{0:^1}{2:^"+str(dwidth)+"}{0:^1}").format("#","Files","Directories","LinNUM"))
    print('#'*crossbar_width)
    bbreak = False
    for index, value in enumerate(fixedfiles):
        print(str("{0:^1}{3:^8}{0:^1}{1:^"+str(filewidth)+"}{0:^1}{2:^"+str(dwidth)+"}{0:^1}").format('#', value, fixeddirs[index], index))
        if index > 99:
            bbreak = True
            print
    print('#'*crossbar_width)
    if bbreak:
        print("Printing exceeded 100 lines.")
    return fixeddirs, fixedfiles

def cdir(cwd):

    fixeddirs, fixedfiles = getdir(cwd)
    print("Enter choice in the format of: \'LineNum(f/d)\n ex: 1f")
    return choice(fixeddirs, fixedfiles)

def choice(fixeddirs, fixedfiles):
    c = input("Enter Choice: ")
    if 'd' in c.lower():
        newpath = fixeddirs[int(c.split('d')[0])]
        os.chdir(newpath)
        return os.getcwd()
    elif 'f' in c.lower():
        os.chdir(fixedfiles[int(c.split('f')[0])])
        return os.getcwd()
    elif '..' == c:
        os.chdir(c)
        return os.getcwd()
def NMRAnalyzer():
    pass
def DAQExtractor():
    pass
def DirSorter():
    pass
def SweepAverager():
    pass
def GlobalInterpreter():
    pass


def main():
    def options():
        optionstr = "@"+" "*10+"OPTIONS"+" "*10+"@"
        print("@"*len(optionstr))
        print(optionstr)
        print(len(optionstr))
        print("@"*len(optionstr))
        functions = [NMRAnalyzer, DAQExtractor, DirSorter, SweepAverager, GlobalInterpreter]
        functionalities = ["NMRAnalyzer","DAQExtractor","DirSorter","SweepAverage","GlobalInterpreter"]

        print('#'*(12+max([len(i) for i in functionalities])))
        print(str("{0:1}{2:^7}{0:1}{1:^"+str(2+max([len(i) for i in functionalities]))+"}{0:1}").format('#','Functionality',"Mode"))
        print('#'*(12+max([len(i) for i in functionalities])))
        for index,value in enumerate(functionalities):
            print(str("{0:^1}{2:^7}{0:^1}{1:^"+str(2+max([len(i) for i in functionalities]))+"}{0:1}").format('#',value,index))
        
        print('#'*(12+max([len(i) for i in functionalities])))
        print("What mode do you want the GUI in?")
        c = input("Enter number in table above: ")
    
    functions = [NMRAnalyzer, DAQExtractor, DirSorter, SweepAverager, GlobalInterpreter]
    optdict = dict(zip([i for i in range(len(functions))],functions))
    while True:
        c= options()
        try:
            f = int(optdict[c])
        except KeyError:
            print("Invalid Option")
    #print("NMR Toolsuite ASCII-GUI")
    #rootdir=os.getcwd()
    #cwd=rootdir

    #fixeddirs, fixedfiles = lsdir(cwd)
main()
