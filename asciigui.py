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

def dict_selector(dic):
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

        keydescribers = [dic[k][0] for k in keys]
        len_keydescribers = [len(k) for k in keydescribers]
        maxlen_key_descrbers = max(len_keydescribers)+2
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
    keydescribers = [dic[k][0] for k in keys]
    tableformatter(keys,keydescribers)

    choice = 'hey'
    while type(choice) != int:
        try:
            choice = int(input("Enter option number: "))
            print("Your choice was", reconsile[choice], 'returning...')
        except KeyboardInterrupt:
            print('keyboard inturrupt recived. Breaking.')
            return False
        except ValueError as e:
            print("Invalid input. Try again.", '\n'*2)
        except KeyError:
            print("Incorrect Key. Make sure option number matches that which is in the table of options.")
    return reconsile[choice]

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
    instance.fetchArgs()
    #instance.showgraph()
    instance.mainloop()


class nmrAnalyser():
    def __init__(self, hardinit=False):
        self.rootdir = os.getcwd()
        self.delimeter = '\t'
        if hardinit:
           self.getBaseline()
           them = '/'.join(self.baselinepath.split('/')[:-1])
           os.chdir(them)
           os.chdir('..')
           self.getRawsig()

    def getBaseline(self):
        self.baselinepath = selectit()
        os.chdir(self.rootdir)
        announcement("Baseline path achieved")

    def getRawsig(self):
        print("Current working directory:",os.getcwd())
        self.rawsigpath = selectit()
        os.chdir(self.rootdir)

    def fetchArgs(self, **kwargs):
        self.mutouse= 'proton'
        self.binning= 1
        self.integrate= True
        self.vnavme= variablenames.agui_vnavme_default
        self.startindex= 0
        self.signalstart= 0
        self.signalend= 0
        self.endindex= 1
        self.fitlorentzian = False 
        self.xname= variablenames.agui_xname_default
        self.xaxlabel= self.xname
        self.yname= variablenames.agui_yname_default
        self.yaxlabel= self.yname
        self.impression= variablenames.agui_impression
        self.xmin= ''
        self.xmax= ''
        self.plottitle= self.rawsigpath.split('/')[-1]
        self.blSkipLinesGetter()
        self.rawsigSkipLinesGetter()
        self.updateDataFrame()
        self.updateGraph()

    def blSkipLinesGetter(self):
        delimeter = self.delimeter
        choice = self.vnavme
        _, _, _, self.blskiplines = v.gui_bl_file_preview(self.baselinepath, self.delimeter)

    def rawsigSkipLinesGetter(self):
        _, _, self.te_date, self.I, self.T, self.primary_thermistor,\
        self.secondary_thermistor, self.rawsigskiplines, self.centroid,\
        self.spread = v.gui_rawsig_file_preview(self.rawsigpath,self.delimeter,self.vnavme)
        try:
            self.B = round(self.I/9.7332,4)
        except ValueError:
            print("WARNING: No Magnet current exists in", self.rawsigpath.split('/')[-1],
                "TE-Value will NOT be calculated")

    def updateDataFrame(self):
        self.df = v.gui_file_fetcher(
                self.rawsigpath, self.baselinepath,
                self.vnavme,
                blskiplines=self.blskiplines, rawsigskiplines=self.rawsigskiplines,
                binning=self.binning
                )

    def changeSignalStartEnd(self):
        announcement("Changing start / end of signal boundaries. Use current x-coordinates.")
        print("To skip changing value for a particular entry, please hit ENTER")
        startsignal = input("Signal Start X-value: ")
        if startsignal == '':
            pass
        else:
            self.startsignal = float(startsignal)

        endsignal = input("Signal End X-Value: ")
        if endsignal == '':
            pass
        else:
            self.endsignal = float(endsignal)

    def updateIndecies(self):
        try:
            self.start_index = self.df.index[self.df[self.xname] == \
            v.nearest(float(self.signalstart),
            self.df[self.xname])][0]-\
            self.df.index[0]
            self.end_index = self.df.index[self.df[self.xname] == \
            v.nearest(float(self.signalend),
              self.df[self.xname])][0]-\
              self.df.index[0]
        except IndexError:
            print("Some index error was raised at the index finding for" 
                  "the pandas dataframe when you entered the "
                  "signal start and end information")
            print("Could be due to malformed signal range. Please recheck your inputs.")
        except:
            print("Error in index finding. Signal highlighting failed.")

    def updateGraph(self, graph=None, repeat=False, p_title=None, automated=False):
        self.updateIndecies()
        if graph is None:
            plt.clf()
            plt.close('all')
            b = self.B
            T = self.T
            try:
                xmin = float(self.xmin)
                xmax = float(self.xmax)
            except ValueError:
                xmin =self.xmin
                xmax = self.xmax

            try:
                fls, fle = float(self.signalstart), float(self.signalend)
            except ValueError:
                fls, fle =0,0
                pass  # It doesn't even matter if this fails because of fltest.
            # Get that plot title during automation
            plot_title = p_title if p_title is not None else self.plottitle
            fltest = True if self.fitlorentzian == '1' else False
            ub = 9.274009994*10**(-24) # Bohr Magnetron
            up = 1.521*10**(-3)*ub     # Proton Magnetic Moment
            ud = 0.307012207*up        # doi.org/10.1016/j.physleta.2003.09.030

            temuval = up if self.mutouse == "proton" else ud
            #print(self.mutouse)
            quirky = v.ggf(
                                self.df, self.start_index, self.end_index, gui=True,
                                plttitle=plot_title, x=self.xname, y=self.yname,
                                xlabel=self.xaxlabel, ylabel=self.yaxlabel,
                                redsig=True if [self.start_index, self.end_index] != [0, len(self.df)]\
                                else False,
                                binning=int(self.binning),
                                integrate=self.integrate,
                                fitlorentzian=fltest, fitlorentziancenter_bounds=[fls,fle],
                                b=b, T=T,   # Its okay if type isnt right, because below line ensures type
                                thermal_equalibrium_value=True if type(b) == float and type (T) == float\
                                 else False,
                                xmin=xmin if type(xmin) == float else None, xmax=xmax if type(xmax) ==\
                                 float else None,filename=self.rawsigpath,
                                clearfigs=True, automated=automated, temu=temuval
                                )
            self.tlorentzian_chisquared = quirky.pop('tristan lorentzian chisquared',None)
            self.klorentzian_chisquared = quirky.pop('karl chisquared', None)
            self.sigmaforchisquared = quirky.pop("karl sigma", None)
            self.figure = quirky['fig']
            self.data_cal_constant = quirky.pop("data_cal_constant", None)
            self.fit_cal_constant = quirky.pop("fit_cal_constant", None)
            self.tevalue = quirky.pop("TE_Value", None)
            self.dataarea = quirky.pop('data_area', None)
            self.ltzian_integration = quirky.pop('ltzian_integration', None)
            self.df = quirky.pop('df', None)
            self.ltzian_a = quirky.pop('a', None)
            self.ltzian_w = quirky.pop('w', None)
            self.ltzian_x0 = quirky.pop('x0',None)
            self.sigma_error = quirky.pop('noisesigma', None)

    def mainloop(self):
        try:
            while True:
                print(self.df.head(3))
                self.allchoices()
        except KeyboardInterrupt:
            print("Keyboard Inturrupt recieved in mainloop. Exiting.")
            exit(True)

    def allchoices(self):
        self.figure.show()
        mumsg= 'Toggles between two available mu values for the TE equation'
        binningmsg = 'Bin width for the data'
        integratemsg = 'Shade region below signal selection on graph. Useful for conceptualizing signal area'
        signalstartendmsg = 'Update start and end x-axis values to mark signal region'
        xnamemsg = 'Select different x-axis for plot'
        ynamemsg = 'Select different y-axis for plot'
        xaxlabelmsg = 'Set x-axis label'
        yaxlabelmsg = 'Set y-axis label'
        fit_subtractionmsg = 'Fit subtract current-data'
        noisemsg = 'Display noise estimate'
        titlemsg = 'Change the plot title'
        automatemsg = 'Take all previous settings and apply them to the rawsignal directory'
        savefigmsg = 'Save the current figure as is.'
        savedatamsg ='Save the current data as is'
        savefiganddatamsg ='Save the current figure and data as is'
        choices = {"binning":[binningmsg, self.setBinning],
                'togglemu':[mumsg, self.adjustmu],
                'toggleintegrate':[integratemsg, self.toggleIntegrate],
                'signal highlighting':[signalstartendmsg, self.changeSignalStartEnd],
                'x-data':[xnamemsg, self.changexname],
                'y-data':[ynamemsg, self.changeyname],
                'xlabel':[xaxlabelmsg, self.changexlabel],
                'ylabel':[yaxlabelmsg, self.changeylabel],
                'fit subtraction':[fit_subtractionmsg, self.fitsubtract],
                'noise quantification':[noisemsg, self.displaynoise],
                'plottitle':[titlemsg, self.changetitle],
                'automate':[automatemsg, self.automate],
                'savefiganddata':[savefiganddatamsg,self.saveboth]}
        key = dict_selector(choices)
        f = choices[key][1]
        f()

    def setBinning(self):
        announce('Current binning is '+str(self.binning)+'.')
        print('Please select new binning')
        choice = 'hey'
        while type(choice) != int:
            try:
                choice = int(input("Enter bin width: "))
            except KeyboardInterrupt:
                print('keyboard inturrupt recived. Breaking.')
                return False
            except ValueError as e:
                print("Invalid input. Try again.", '\n'*2)
        self.binning = choice

    def adjustmu(self):
        allowable_mus = ['proton', 'deuteron']
        print("Current mu is", self.mutouse)
        protonmsg = 'Proton Mu'
        deuteronmsg = 'Deuteron Mu'
        messages = [protonmsg, deuteronmsg]

        choices = dict(zip(allowable_mus, messages))
        self.mutouse = dict_selector()
        print("Mu is now: ", self.mutouse)

    def toggleIntegrate(self):
        self.integrate = not self.integrate
        print("Shading toggle is now", 'on' if self.integrate else 'off')

    def changexname(self):
        announcement("Current X name "+str(self.xname))
        columns = self.df.cols.tolist()
        columnmsg = "Column in dataframe."
        print("available columns:") 
        nice = [columnmsg for i in range(len(columns))]
        choices = dict(zip(columns, nice))
        self.xname = dict_choice(choices)
    
    def changeyname(self):
        announcement("Current Y name "+str(self.yname))
        columns = self.df.cols.tolist()
        columnmsg = "Column in dataframe."
        print("available columns:") 
        nice = [columnmsg for i in range(len(columns))]
        choices = dict(zip(columns, nice))
        self.yname = dict_choice(choices)

    def changexlabel(self):
        announcement("Current xlabel "+str(self.xlabel))
        self.xlabel = input("Input xlabel: ")

    def changeylabel(self):
        announcement("Current ylabel "+str(self.ylabel))
        self.ylabel = input("Input xlabel: ")

    def fitsubtract(self):
        pass
    def displaynoise(self):
        pass
    def changetitle(self):
        pass
    def automate(self):
        pass
    def saveboth(self):
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
