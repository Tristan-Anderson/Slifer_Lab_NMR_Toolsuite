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
def announcement(mystr):
    print('\n')
    print("#"*3, mystr, '#'*3)
    print('\n')

def header(mystr):
    s = 7
    lstr = len(mystr) +2
    width = lstr+s*2+2
    print("@"*width)
    print(str("{0:1}{2:^"+str(s)+"}{1:^"+str(lstr)+"}{2:^"+str(s)+"}{0:1}").format("@",mystr, ' '*s))
    print("@"*width)


def getdir(cwd):
    # Get the items in a directory
    for subdir, dirs, files in os.walk(cwd):
        break
    #print("Current directory:", cwd)
    cleanfiles = []
    for f in files:
        if any(ext in f for ext in variablenames.agui_allowable_file_extensions):
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
        if index > 99:
            bbreak = True
            break
    print('#'*crossbar_width)
    if bbreak:
        print("Printing exceeded 100 lines.")
    return fixeddirs, fixedfiles


def selectit():
    cwd = os.getcwd()
    status = True
    while status:
        fixeddirs, fixedfiles = getdir(cwd)
        print("Enter choice in the format of: \'LineNum(f/d)\n ex: 1f")
        status, path = choice(fixeddirs, fixedfiles)
        announcement(cwd)
        cwd = path
    return path


def choice(fixeddirs, fixedfiles):
    c = input("Enter Choice: ")
    if 'd' in c.lower():
        newpath = fixeddirs[int(c.split('d')[0])]
        os.chdir(newpath)
        return True, os.getcwd()
    elif 'f' in c.lower():
        newpath = fixedfiles[int(c.split('f')[0])]
        return False, os.getcwd()+'/'+newpath
    elif '..' == c:
        os.chdir(c)
        return True, os.getcwd()
    elif 'ok' in c:
        print('okay. Saving current directory choice.')
        return False, os.getcwd()
    else:
        print("You selected", c, 'which is not a valid option.')
        return True, os.getcwd()


def NMRAnalyzer():
    """
    Get the baseline and rawsignal from the user.
    """
    header("NMR Analyser")
    print('\n'*3,'Please select baseline file')
    print("#"*30)
    instance = nmrAnalyser(hardinit=True)



class nmrAnalyser():
    def __init__(self, hardinit=False):
        self.rootdir = os.getcwd()
        if hardinit:
           self.getBaseline()
           print('/'.join(self.baselinepath.split('/')))
           print('Thats it')
           os.chdir(self.baselinepath)
           os.chdir('..')
           self.getRawsig()

    def getBaseline(self):
        self.baselinepath = selectit()
        os.chdir(self.rootdir)
        announcement("Baseline path achieved")

    def getRawsig(self):
        self.rawsigpath = selectit()
        os.chdir(self.rootdir)


    def updateDataframe(self):
        pass

    def updateIndecies(self):
        pass

    def updateGraph(self):
        pass

    def updateXYSelector(self):
        pass

    def addEntry(self):
        pass

    def addFit(self):
        pass

    def initOne(self):
        pass

    def saveFig(self):
        pass

    def gotoBeginning(self):
        pass

    def updateRawSig(self):
        pass

    def trimData(self):
        pass

    def automator(self):
        pass

    def repeatAdNauseum(self):
        pass

def DAQExtractor():
    pass

class daqExtractor():
    def __init__(self):
        pass

    def __getPath__(self):
        pass

    def getFile(self):
        self.path = self.__getPath__()
        pass

    def execute(self):
        pass

    def setstate(self):
        # Sets the state between directory and individual file mode.
        pass


def DirSorter():
    pass

def SweepAverager():
    pass

def GlobalInterpreter():
    pass


def main():
    def options():
        print('\n'*3)
        header("OPTIONS")
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
        try:
            return int(c)
        except TypeError:
            print("Invalid Input")
            return options()

    functions = [NMRAnalyzer, DAQExtractor, DirSorter, SweepAverager, GlobalInterpreter]
    optdict = dict(zip([i for i in range(len(functions))],functions))
    while True:
        c= options()
        try:
            f = optdict[c]
            f()
        except KeyError:
            print("Invalid Option")
    #print("NMR Toolsuite ASCII-GUI")
    #rootdir=os.getcwd()
    #cwd=rootdir

    #fixeddirs, fixedfiles = lsdir(cwd)
main()
