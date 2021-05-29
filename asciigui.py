# PYTHON 3.9.1
"""
Tristan Anderson
takc1nqa@gmail.com
tanderson@vt.edu

Proceed Formally.
"""

# Fortune
"""
This universe shipped by weight, not by volume.  Some expansion of the
contents may have occurred during shipment.
"""

import NMR_Analyzer as v
import daq_muncher, directory_sorter,sweep_averager,global_interpreter,spin_extractor
from matplotlib import pyplot as plt
import datetime,pandas,os,numpy,gc,time,multiprocessing,variablenames,matplotlib,argparse

"""
# TODO: Add overview of current settings on each mainloop in table format.
"""
class AsciiGUI():
    """
    The master template
    for the different frames of the
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

    def fileDirectorySelector(self, dironly=False, fileonly=False):
        cwd = os.getcwd()
        status = True
        while status:
            fixeddirs, fixedfiles, cleanfiles, dirs = self.getdir(cwd)
            print("Current working Directory:", cwd)
            print("Enter choice in the format of: \'LineNum(f/d)\n\t ex: 1f\t ex: 1d\n\t ex: ok\t ex: ..\n or type: \'help\', \'?\' for more details.")
            
            status, path = self.choice(fixeddirs, fixedfiles, cleanfiles, dirs, dironly=dironly, fileonly=fileonly)
            
            cwd = path
        return path

    def getdir(self, cwd):
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
            if index > 25:
                bbreak = True
                break
        print('#'*crossbar_width)
        if bbreak:
            print("Printing exceeded 100 lines.")
        return fixeddirs, fixedfiles, cleanfiles, dirs

    def choice(self, fixeddirs, fixedfiles, cleanfiles, dirs, dironly, fileonly):
        c = input("Enter Choice: ")
        if 'help' in c.lower() or '?' in c.lower():
            print("To navigate into a directory, enter choice in the format of: LineNum(d)\n\t ex: 1d")
            print("To navigate out of the current directory, (into the parent of the current directory) enter choice in the format of: \'..\'\n\t ex: ..")
            print("To select a directory, you must navigate into the directory you want to select. Then enter choice in the format of: \'ok\'\n\t ex: ok")
            print("To select a particular file, enter choice in the format of: LineNum(f)\n\t ex: 1f")
            return True, os.getcwd()
        elif 'f' not in c.lower() and '1' not in c.lower():
            self.announcement("Invalid Choice.")
            return True, os.getcwd()

        try:
            if 'd' in c.lower() and not fileonly:
                item = int(c.split('d')[0])
                if item in range(len(dirs)):
                    newpath = fixeddirs[item]
                    os.chdir(newpath)
                    return True, os.getcwd()
            elif 'f' in c.lower() and not dironly:
                item = int(c.split('f')[0])
                if item in range(len(cleanfiles)):
                    newpath = fixedfiles[int(c.split('f')[0])]
                    return False, os.getcwd()+'/'+newpath
            elif '..' == c:
                os.chdir(c)
                return True, os.getcwd()
            elif 'ok' in c and not fileonly: 
                print('okay. Saving current directory choice.')
                return False, os.getcwd()
        except ValueError as e:
                self.announcement("Invalid Choice.")
                print(e)
                return True, os.getcwd()
                
        self.announcement("You selected " +c+ ' which is not a valid option.')
        if dironly:
            self.announcement("File browser is in DIRECTORY-only mode. Select a valid Directory.")
        elif fileonly:
            self.announcement("File browser is in FILE-only mode. Select a valid file.")

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
        print('\n')

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


def NMRAnalyzer(args):
    """
    Get the baseline and rawsignal from the user.
    """
    instance = nmrAnalyser(args, hardinit=True)
    del instance

class nmrAnalyser(AsciiGUI):
    def __init__(self,args=None, hardinit=False):
        self.rootdir = os.getcwd()
        self.delimeter = '\t'
        self.hardinit = hardinit
        self.processes = 1
        self.servermode = False
        self.analysisfile = pandas.DataFrame()
        self.failedfiles = []
        if hardinit:
            self.servermode = args.servermode
            self.processes = int(8*multiprocessing.cpu_count()/10)
            print(self.processes, "Processing threads available")
            self.mainloop()
       
    def overrideRootDir(self, override):
        self.rootdir = override
        pass

    def getBaseline(self):
        self.announcement("Update Baseline")
        print("Current working directory:",os.getcwd())
        self.baselinepath = self.fileDirectorySelector(fileonly=True)
        os.chdir(self.rootdir)
        self.announcement("Baseline path updated")

    def getRawsig(self):
        self.announcement("Update Raw Signal")
        print("Current working directory:",os.getcwd())
        self.rawsigpath = self.fileDirectorySelector(fileonly=True)
        os.chdir(self.rootdir)
        self.announcement("Raw Signal path updated")

    def refreshAnalysis(self):
        self.automatefits = []
        self.fitnumber = 0
        self.xname = variablenames.agui_xname_default
        self.yname = variablenames.agui_yname_default
        self.blSkipLinesGetter()
        self.rawsigSkipLinesGetter()
        self.updateDataFrame()

    def fetchArgs(self, **kwargs):
        self.isautomated = kwargs.pop('isautomated', False)
        if self.isautomated:
            self.baselinepath = kwargs.pop('baselinepath', '')
            self.rawsigpath = kwargs.pop('rawsigpath', '')
        self.material_type = kwargs.pop('material_type', '')
        self.fitnumber = kwargs.pop('fitnumber',0)
        self.automatefits = kwargs.pop('automatefits',[])
        self.mutouse= kwargs.pop('mutouse','proton')
        self.binning= kwargs.pop('binning',1)
        self.integrate= kwargs.pop('integrate', False)
        self.vnavme= kwargs.pop('vnavme', variablenames.agui_vnavme_default)
        self.startindex= kwargs.pop('startindex',0)   #NMR Analyzer used
        self.signalstart= kwargs.pop('signalstart',0) #User selected start
        self.signalend=kwargs.pop('signalend',0)      #User selected end
        self.endindex= kwargs.pop('endindex',1)       #NMR Analyzer used
        self.fitlorentzian = kwargs.pop('fitlorentzian',False)
        self.xname= kwargs.pop('xname',variablenames.agui_xname_default)
        self.xaxlabel= kwargs.pop('xaxlabel',self.xname)
        self.yname= kwargs.pop('yname',variablenames.agui_yname_default)
        self.yaxlabel= kwargs.pop('yaxlabel',self.yname)
        self.impression= kwargs.pop('impression',variablenames.agui_impression)
        self.xmin= kwargs.pop('xmin', '')
        self.xmax= kwargs.pop('xmax', '')
        self.startcolumn = kwargs.pop('startcolumn',[])
        self.instancename = kwargs.pop('instancename', datetime.datetime.now().strftime('%Y%m%d_%H%M%s Instance'))
        self.plottitle= kwargs.pop('title',self.rawsigpath.split('/')[-1])
        self.self_itemseed = kwargs.pop('the_new_list', None)

        
        self.filelist = kwargs.pop('filelist', [])
        
        if not self.hardinit:
            self.processes = kwargs.pop('processes',1)

        
        self.blSkipLinesGetter()
        self.rawsigSkipLinesGetter()
        self.updateDataFrame()
        if self.isautomated:
            return True
        self.updateMaterialType()
        self.updateInstanceName()
        self.updateGraph()

    def blSkipLinesGetter(self):
        delimeter = self.delimeter
        choices = self.vnavme
        _, _, _, self.blskiplines = v.gui_bl_file_preview(self.baselinepath, self.delimeter)

    def updateInstanceName(self):
        self.announcement("Current instance name: "+self.instancename)
        self.instancename = input("Input new instance name: ")

    def rawsigSkipLinesGetter(self):
        _, _, self.te_date, self.I, self.T, self.primary_thermistor,\
        self.secondary_thermistor, self.rawsigskiplines, self.centroid,\
        self.spread = v.gui_rawsig_file_preview(self.rawsigpath,self.delimeter,self.vnavme)
        try:
            self.B = round(int(self.I)/9.7332,4)
        except (ValueError,TypeError):
            print("WARNING: No Magnet current exists in", self.rawsigpath.split('/')[-1],
                "TE-Value will NOT be calculated")
            self.B = self.I

    def updateDataFrame(self):
        self.df = v.gui_file_fetcher(
                self.rawsigpath, self.baselinepath,
                self.vnavme,
                blskiplines=self.blskiplines, rawsigskiplines=self.rawsigskiplines,
                binning=self.binning
                )

    def changeSignalStartEnd(self):
        self.announcement("Changing start / end of signal boundaries. Use current x-coordinates.")
        print("To skip changing value for a particular entry, please hit ENTER")
        startsignal = input("Signal Start X-value: ")
        if startsignal == '':
            pass
        else:
            self.signalstart = float(startsignal)

        endsignal = input("Signal End X-Value: ")
        if endsignal == '':
            pass
        else:
            self.signalend = float(endsignal)
        self.updateGraph()

    def updateMaterialType(self):
        self.announcement("Current material type: "+self.material_type)
        self.material_type = input("Input new material type: ")

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
            fltest = self.fitlorentzian 
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
        else:
            self.figure = graph

    def mainloop(self, failedfit=False):
        try:
            if not failedfit:
                self.getBaseline()
                them = '/'.join(self.baselinepath.split('/')[:-1])
                os.chdir(them)
                os.chdir('..')
                self.getRawsig()
                self.fetchArgs()
            else:
                self.blSkipLinesGetter()
                self.rawsigSkipLinesGetter()
                self.updateDataFrame()
                
                #self.updateMaterialType()
                #self.updateInstanceName()
                self.updateGraph()
            while True:
                if not self.servermode:
                    self.figure.show()
                print("#"*70)
                self.currentSettings()
                print("#"*70)
                self.header("Data frame head")
                print("#"*70)
                print(self.df.head(3))
                _ = self.allchoices(failedfit)
                if _ == "triggerAutomateMethod":
                    break
                elif _ == "giveUpRefitting":
                    break
        except KeyboardInterrupt:
            print("Keyboard Inturrupt recieved in mainloop. Exiting.")
            return True

    def allchoices(self, failedfit):
        nameinstancemsg = "Label this current analysis cycle in the global analysis file."
        mumsg= 'Toggles between two available mu values for the TE equation'
        binningmsg = 'Bin width for the data'
        signalstartendmsg = 'Update start and end x-axis values to mark signal region'
        fit_subtractionmsg = 'Fit subtract current-data'
        integratemsg = 'Shade region below signal selection on graph. Useful for conceptualizing signal area'
        lorentzian_rawfitmsg = 'Fit lorentzian to current data selection.'
        xnamemsg = 'Select different x-axis for plot'
        ynamemsg = 'Select different y-axis for plot'
        xaxlabelmsg = 'Set x-axis label'
        yaxlabelmsg = 'Set y-axis label'
        titlemsg = 'Change the plot title'
        automatemsg = 'Take all previous settings and apply them to the rawsignal directory'
        savefigmsg = 'Save the current figure as is.'
        savedatamsg ='Save the current data as is'
        savefiganddatamsg ='Save the current figure and data as is'
        updatebaselinemsg = "Update baseline file"
        updaterawsigmsg = "Update signal file"
        changematerialmsg = "Update Material Type"
        ignorefilemsg = "Ignore / Skip refitting of this file"
        giveupmsg = "This data is insufferable: I'm done re-fitting"
        if failedfit:
            choices = {
                    "binning":[binningmsg, self.setBinning],
                    'signal highlighting':[signalstartendmsg, self.changeSignalStartEnd],
                    'fit subtraction':[fit_subtractionmsg, self.fitSubtract],
                    'toggleintegrate':[integratemsg, self.toggleIntegrate],
                    'fitlorentziancurve':[lorentzian_rawfitmsg, self.toggleLorentzian],
                    'x-data':[xnamemsg, self.changexname],
                    'y-data':[ynamemsg, self.changeyname],
                    'automate':[automatemsg, self.dudToReturnTrue],
                    'skip':[ignorefilemsg, self.pleaseSkipMe],
                    'giveup':[giveupmsg, self.giveUpRefitting]}
        else:
            choices = {
                    "binning":[binningmsg, self.setBinning],
                    'signal highlighting':[signalstartendmsg, self.changeSignalStartEnd],
                    'fit subtraction':[fit_subtractionmsg, self.fitSubtract],
                    'toggleintegrate':[integratemsg, self.toggleIntegrate],
                    'fitlorentziancurve':[lorentzian_rawfitmsg, self.toggleLorentzian],
                    'x-data':[xnamemsg, self.changexname],
                    'y-data':[ynamemsg, self.changeyname],
                    'xlabel':[xaxlabelmsg, self.changexlabel],
                    'ylabel':[yaxlabelmsg, self.changeylabel],
                    'plottitle':[titlemsg, self.changetitle],
                    'togglemu':[mumsg, self.adjustmu],
                    'savefiganddata':[savefiganddatamsg,self.saveBoth],
                    'automate':[automatemsg, self.automate],
                    "updatebaseline":[updatebaselinemsg, self.getBaseline],
                    "updaterawsignal":[updaterawsigmsg, self.getRawsig],
                    "updatematerial":[changematerialmsg, self.updateMaterialType],
                    "nameinstance":[nameinstancemsg, self.setInstanceName]}
        key = self.dict_selector(choices)
        f = choices[key][1]
        if failedfit:
            _ = f()
            if _ == "triggerAutomateMethod":
                return _
            elif _ == "giveUpRefitting":
                return _
        else:
            f()
        if key in ["updatebaseline", "updaterawsignal"]:
            self.refreshAnalysis()
            self.updateGraph()

    def giveUpRefitting(self):
        return "giveUpRefitting"

    def pleaseSkipMe(self):
        try:
            self.rawsigpath = self.filelist.pop(0)
            self.failed_sindexes.pop(0)
            self.failed_eindexes.pop(0)
            self.failed_itemnos.pop(0)
        except IndexError as e:
            print("Index error (OUT OF FILES!) in re-fitting routine. Returning to normal:", e)
            return "triggerAutomateMethod"

        self.xname= variablenames.agui_xname_default
        self.yname= variablenames.agui_yname_default
        self.blSkipLinesGetter()
        self.rawsigSkipLinesGetter()
        self.updateDataFrame()
        self.updateGraph()


    def dudToReturnTrue(self):
        return 'triggerAutomateMethod'

    def currentSettings(self):
        self.header("Current Settings:")
        x = self.xname

        lineone = "# Data Range: " + str(min(self.df[x]))+ ' to ' + str(max(self.df[x])) + ' ' + str(x) \
                + '\n# Current Signal Highlighting Region ' + str(self.signalstart) + ' to ' + str(self.signalend)+ ' ' + str(x)
        
        linetwo = "# Shading: " + ('Enabled' if self.integrate else 'Disabled') \
                + " \n# Current binning: " + str(self.binning) + " \n# Current mu: " + str(self.mutouse.upper())

        linethree = '# Current Baseline File: ' + str(self.baselinepath) + '\n# Current Raw-Signal File: '+ str(self.rawsigpath)

        lines = [lineone, linetwo]
        print(lineone, linetwo, linethree, sep='\n')

    def setInstanceName(self):
        self.announcement("Current instance name is: "+self.instancename)
        self.instancename = input("Input new instance name: ")
        print("Instance name changed to", self.instancename)

    def toggleLorentzian(self):
        self.fitlorentzian = not self.fitlorentzian
        self.updateGraph()
    
    def setBinning(self):
        self.announcement('Please note that updating the data binning will reset the current session.')
        self.announcement('Current binning is '+str(self.binning)+'.')
        print('Please select new binning')
        choices = 'im a string.'
        while type(choices) != int:
            try:
                choices = int(input("Enter bin width: "))
            except KeyboardInterrupt:
                print('keyboard inturrupt recived. Breaking.')
                return False
            except ValueError as e:
                print("Invalid input. Try again.", '\n'*2)
        self.binning = choices
        self.refreshAnalysis()
        self.updateDataFrame()
        self.updateGraph()

    def adjustmu(self):
        allowable_mus = ['proton', 'deuteron']
        print("Current mu is", self.mutouse)
        protonmsg = 'Proton Mu'
        deuteronmsg = 'Deuteron Mu'
        messages = [protonmsg, deuteronmsg]

        choices = dict(zip(allowable_mus, messages))
        self.mutouse = self.dict_selector(choices)
        print("Mu is now: ", self.mutouse)
        self.updateGraph()

    def toggleIntegrate(self):
        self.integrate = not self.integrate
        print("Shading toggle is now", 'on' if self.integrate else 'off')
        self.updateGraph()

    def changexname(self):
        self.announcement("Current X name "+str(self.xname))
        columns = self.df.columns.tolist()
        columnmsg = "Column in dataframe."
        print("available columns:") 
        nice = [columnmsg for _ in range(len(columns))]
        choices = dict(zip(columns, nice))
        self.xname = self.dict_selector(choices)
        self.xaxlabel = self.xname
        self.updateGraph()

    def changeyname(self):
        self.announcement("Current Y name "+str(self.yname))
        columns = self.df.columns.tolist()
        columnmsg = "Column in dataframe."
        print("available columns:") 
        nice = [columnmsg for i in range(len(columns))]
        choices = dict(zip(columns, nice))
        self.yname = self.dict_selector(choices)
        self.yaxlabel = self.yname
        self.updateGraph()

    def changexlabel(self):
        self.announcement("Current xlabel "+str(self.xaxlabel))
        self.xaxlabel = input("Input xlabel: ")
        self.updateGraph()

    def changeylabel(self):
        self.announcement("Current ylabel "+str(self.yaxlabel))
        self.yaxlabel = input("Input xlabel: ")
        self.updateGraph()

    def __user_fit_selection__(self):
        keys = ['Sin', 'Third order Polynomial', 'Fourth order Polynomial',
                'Fifth Order Polynomial', 'Sixth Order Polynomial', 
                'True Lorentzian',"Lorentzian (absorbtion/dispersion)", "Cancel Fit"]
        values = ['sin', 'third_order', 'fourth_order', 'fifth_order',
                'sixth_order','lorentzian_ellie','absorbtion_dispersion_ellie', "Cancel Fit"]
        choices = dict(zip(keys,values))
        reverse = dict(zip(values,keys))
        self.fitname = self.dict_selector(choices)
        if self.fitname == False:
            print("Fit subtraction cancelled")
            return True
        self.type_of_fit = choices[self.fitname]
        self.fitname = self.fitname +str(' '+str(self.fitnumber))
        #print("Fit name",self.fitname, "Function Name", self.type_of_fit)

    def __ensure_unique_fit__(self):
        test = len(self.automatefits)-1
        if test >= 0:
            if self.automatefits[test][1] == self.fitname:
                print("\nWARNING: Previous fit named:", self.automatefits[test][1],
                        "was overridden.\nChange fit name if you are doing multiple subtraction\n")
                self.automatefits[test] = [self.type_of_fit, self.fitname]
                self.startcolumn[test] = self.yname
            else:
                self.automatefits.append([self.type_of_fit, self.fitname])
                self.startcolumn.append(self.yname)
        else:
            self.automatefits.append([self.type_of_fit, self.fitname])
            self.startcolumn.append(self.yname)

    def __fitbound_coersion__(self):
        try:
            p0 = [float(self.lorentzian_x0), float(self.lorentzian_w),
                    float(self.lorentzian_A), float(self.lorentzian_B)]\
                            if self.fitname == "lorentzian_ellie" else None
            bounds = [[float(self.lorentzian_x0)-.1, -numpy.inf, 
                float(self.lorentzian_A)-.05, -numpy.inf],
                [float(self.lorentzian_x0)+.1, numpy.inf, float(self.lorentzian_A)+\
                        .05, numpy.inf]] if self.fitname == "lorentzian_ellie" else \
                        [[-numpy.inf, -numpy.inf, -numpy.inf, -numpy.inf ],
                                [numpy.inf,numpy.inf,numpy.inf,numpy.inf]]
        except ValueError:
            print("***WARNING: Error in type conversion for RAWSIGNAL fit \
                    coersion. p0 WILL NOT be passed.")
            p0 = None
        return p0, bounds

    def fitSubtract(self,automated=False):
        #                   User selection of fit                                  #
        if self.__user_fit_selection__():
            return True

        # Free some memory
        if not automated:
            plt.clf()
            plt.close('all')
        
        #                   don't duplicate fits                                   #

        self.__ensure_unique_fit__()

        # Update the indecies before we fit the data
        self.updateIndecies()

        #                 Collect p0 / bounds if it exists                         #

        p0, bounds = self.__fitbound_coersion__()

        #                           Fit the function                               #


        self.df, fig, chsq, rawsigfit, self.didfailfit = v.gff(
                self.df, self.start_index, self.end_index, fit_sans_signal=True,
                function=[self.type_of_fit], fitname=self.fitname,
                binning=self.binning, gui=True, redsig=True, x=self.xname,
                y=self.yname, plottitle=self.plottitle, p0=p0, bounds = bounds)

        if self.didfailfit and not automated:
            print('Fit failed, try another.')
            self.disapprovePlot()
            return True
        
        self.e_f0= rawsigfit.pop('e_f0', None)
        self.e_w=rawsigfit.pop("e_w", None)
        self.e_kmax=rawsigfit.pop('e_kmax', None)
        self.e_theta=rawsigfit.pop("e_theta", None)

        print(" "*15, "CHI SQUARED VALUES FOR EACH FIT")
        print("#"*65)

        for key in chsq:
            val = chsq[key]
            print("{0:<1s}{1:^5s}{0:1s}{2:^31s}{0:1s}{3:^25s}{0:1s}"\
                    .format("#","Fit", key, str(val)))
            #print("#Fit #\t", key, " #\t Chisquared:", val, " #")
        print("#" * 65)
        self.updateGraph(graph=fig)

        #                   User approve/deny                                      #

        if not automated:
            if not self.servermode:
                self.figure.show()
            cancelmsg = 'Cancel the fit subtraction, and do not change the graph.'
            approvemsg = 'The fit looks good, let me see the fit subtraction'
            disapprovemsg = 'The fit looks bad, let me redo it.'
            choices = {'approve':[approvemsg, self.approvePlot],
                    'disapprove':[disapprovemsg, self.disapprovePlot],
                    'cancel':[cancelmsg,self.cancelFit]}
            key = self.dict_selector(choices)
            f = choices[key][1]
            f(manual=True)

        elif automated:
            self.approvePlot()

    def approvePlot(self, **kwargs):
        availablecolums = self.df.columns.to_list()
        (fit_data, fitsubtraction) = availablecolums[-2:]
        self.yname = fitsubtraction
        self.updateGraph()
        self.fitnumber += 1

    def disapprovePlot(self, manual=False):
        if not manual:
            self.announcement("Plot rejected. Try alternate fitting strategy, or adjust signal highlighted region")
        self.fitSubtract()

    def cancelFit(self, manual='False'):
        self.updateGraph()
        return False
        
    def changetitle(self):
        c = input("Input new plot title: ")
        self.plottitle = c
        self.updateGraph()

    def saveFig(self,filename=None, automated=False):
        filename = self.plottitle if filename is None else filename
        self.updateGraph(automated=automated)
        plt.savefig(filename)

    def updateItemSeed(self, itemseed):
        # Reseed the item in the class.
        # Used for multithreading
        self.item=itemseed

    def getFileList(self):
        print("Filelist")
        print(self.filelist)

    def automate(self):
        """
            Replicated from the tkinter version of the gui
        """
        singleThread = False
        
        matplotlib.use('Agg') # Thwarts X-server Errors
        # Matplotlib is NOT thread-safe w/ known race conditions.
        # Care has been used to avoid these conditions (unique namespaces (instances of this class) should isolate mpl stacks from eachother.)
        # Let me know if I missed any.
        
        ##################################################
        # Ensure Directories exist where we can put file #
        ##################################################
        os.chdir(self.rootdir)
        home = self.rootdir
        os.chdir(home)
        try:
            os.chdir("graphs") 
        except FileNotFoundError:
            os.mkdir("graphs") 
        os.chdir(home)
        try:
            os.chdir("graph_data") 
        except FileNotFoundError:
            os.mkdir("graph_data") 
        os.chdir(home)
        graphs = home+"/graphs/" 
        graphdata = home+"/graph_data/" 


        tedirectory = "/".join(self.rawsigpath.split('/')[:-1])

        tefiles = []
        #########################################################
        extension = ".ta1" if self.vnavme.upper() == "VME" else ".s1p"

        # Create the TE/Enchanced files list
        for file in os.listdir(tedirectory):
            if file.endswith(extension):
                tefiles.append(tedirectory+'/'+file)
        
        # create a list of tuples that split the files between multiple threads
        oh_indexes = self.__forkitindexer__(tefiles)
        
        # Used to create unique instance names so pandas doesn't overwrite identical entries. (also human readability)
        self.workpool = [] 
        self.plottitle = self.instancename if self.plottitle == self.rawsigpath.split('/')[-1] else self.plottitle
        for index, value in enumerate(oh_indexes):
            (start, end) = value
            self.workpool.append(nmrAnalyser())
            self.workpool[index].overrideRootDir(self.rootdir)
            self.workpool[index].fetchArgs(fitnumber='fitnumber',
                automatefits= self.automatefits,
                material_type = self.material_type,
                mutouse= self.mutouse,
                binning= self.binning,
                integrate= self.integrate,
                vnavme= self.vnavme,
                signalstart= self.signalstart,
                signalend=self.signalend,
                fitlorentzian= self.fitlorentzian,
                xname= self.xname,
                xaxlabel= self.xaxlabel,
                yname= self.yname,
                yaxlabel= self.yaxlabel,
                xmin= self.xmin,
                xmax= self.xmax,
                startcolumn= self.startcolumn,
                instancename= self.instancename,
                title= self.plottitle,
                isautomated= True,
                filelist = ([tefiles[start]] if start==end else tefiles[start:end]),
                rawsigpath = self.rawsigpath,
                baselinepath = self.baselinepath)
            self.workpool[index].updateItemSeed(start)

        if singleThread:
            results = [self.workpool[index].automatedPKernel(graphs, graphdata, home, index) for index,value in enumerate(oh_indexes)]
        else:
            with multiprocessing.Pool(processes=self.processes) as pool:
                result_objects = [pool.apply_async(self.workpool[index].automatedPKernel, args =(graphs, graphdata, home, index)) for index,value in enumerate(oh_indexes)]
                pool.close()
                pool.join()

            results = [r.get() for r in result_objects]
        

        # Cleanup behind ourselves.
        del self.workpool 
        
        # HERE LIES THE FIT FAIL CATCHER / REVIEWER.
        # The user will need to put in some extra elbow grease here to encourage the 
        
        #self.failedfiles = [File that failed, [(program function name, fit-label)...], start index, end index, item number in sweep]
        
        for results_df, failedfiles in results:
            # Keeper data / global analysis is in the results
            self.analysisfile = self.analysisfile.append(results_df,ignore_index=True)
            # Gets any and all failed fits.
            self.failedfiles.append(failedfiles)

        
        while all([len(trash_failed_files) > 0 for trash_failed_files in self.failedfiles]):
            self.automatefits = []
            self.failedFitCatcher(graphs, graphdata, home)
        
        input('Press any key to continue')
        self.addEntry(appendme=self.analysisfile)
        matplotlib.use("TkAgg") # Turn plotting front-end back on.
        raise KeyboardInterrupt # Get out of the mainloop.

    def automatedPKernel(self, graphs, graphdata, home, id_num,self_itemseed=None):
        return self.repeatAdNauseum(self.filelist,graphs, graphdata, home, id_num=id_num, self_itemseed=self.self_itemseed)

    def repeatAdNauseum(self, filelist, graphs, graphdata, home, failed=False, failedno=0, self_itemseed = None, id_num=''):
        # based on VME/VNA file selection what y-axis are we going to apply the user's settings to first on a blind loop
        self.analysisfile = pandas.DataFrame()
        self.dataset = {}
        self.failedfiles = []

        try:
            item_is_list = False
            self.item = int(self_itemseed) if self_itemseed is not None else self.item
        except TypeError:
            if type(self_itemseed) == list:
                item_is_list = True

        originalplottitle = self.plottitle
        npriev = self.startcolumn[0]
        
        if npriev is None:
            print("ID:",id_num,"**WARNING: The Y-axis that was selected after file selection"
                " no longer exists, or is invalid. Defaulting to file-type default "
                "(Potential (V) if .ta1; Z_re if .s1p)")
            npriev = "Potential (V)" if self.vnavme.upper() == "VME" else "Z_re"

        timedeltas = []
        todo = len(filelist)

        for i,file in enumerate(filelist):
            # Set the y-axis to be the first column fit by the user during interactive mode.
            npriev = self.startcolumn[0]

            t1 = time.time()
            # update attribute
            self.rawsigpath = file
            # Run method to update other attributes
            self.rawsigSkipLinesGetter()
            
            # Update the dataframe.
            self.updateDataFrame()

            # Update the indecies
            self.updateIndecies()

            # Do multiple fits:
            
            for index, tupp in enumerate(self.automatefits):
                f = tupp[0] # Function name (sin, third-order, fourth-order ... , exponential)
                            # Litterally eval()'ed, dont tell opsec, or Professor Arvind Narayan that I did this
                n = tupp[1] # The name that the user gave their template fit before clicking the "fit data" button
                            # Used to itteratively map / shift fitting, and naming of fits, subtractions, etc.
                self.df, fig, chsq, rawsigfit, self.didfailfit = v.gff(
                                self.df, self.start_index, self.end_index, fit_sans_signal=True,
                                function=[f], fitname=n, x=self.xname,
                                binning=self.binning, gui=True, redsig=True, 
                                y=npriev, plottitle=self.plottitle
                                )
                #print("Did Fail Fit:", self.didfailfit)
                if self.didfailfit:
                    print(file.split('/')[-1], "failed in fitting", npriev, 'with function name', n)
                    # [File that failed, [(program function name, fit-label)...], start index, end index, item number in sweep]
                    #print(file, self.automatefits, self.start_index, self.end_index, self.item)
                    self.failedfiles.append([file, self.automatefits, self.start_index, self.end_index, self.item])

                    if item_is_list:
                        self.item = self_itemseed[i]
                    else:
                        self.item += 1
                    break
                self.e_f0= rawsigfit.pop('e_f0', None)
                self.e_w=rawsigfit.pop("e_w", None)
                self.e_kmax=rawsigfit.pop('e_kmax', None)
                self.e_theta=rawsigfit.pop("e_theta", None)
                # Save tupp[1], because if we loop again, we're gonna need to fit subtract fit-subtracted data,
                #  otherwise the user overwrites their last fit.
                npriev = tupp[1]
            else:
                """
                    This is the start of a for-else statment.
                    The else statement is reached when the for loop iterates
                    successfully (without breaking)
                """
                # Save the figure
                os.chdir(graphs)
                filename = self.instancename+" S"+str(self.item)

                self.saveFig(filename=filename+'.png', automated=True) # UNCOMMENT TO SAVE EVERYTHING.

                # This is here so that i can recreate this order within the loop
                try:
                    self.B = round(self.I/9.7332, 4)
                    self.tevalue = v.tpol(self.B, self.T)
                except TypeError:
                    print(id_num,"WARNING: TE value Failed, indicating that B, or T was not of proper type.")
                    self.B = self.I
                    self.tevalue = 0

                # Headers for the global analysis file
                headers = variablenames.na_global_analysis_headers

                # Write to the global_analysis file
                c = [self.instancename + " S"+str(self.item),  self.material_type,
                 self.te_date, self.vnavme, self.baselinepath, self.rawsigpath, self.xmin, self.xmax,
                 self.signalstart,self.signalend, self.blskiplines,
                 self.rawsigskiplines, str(self.B),
                 str(self.T), self.primary_thermistor, self.secondary_thermistor, self.tevalue,
                 self.dataarea, self.ltzian_integration, self.data_cal_constant,
                 self.fit_cal_constant, self.ltzian_a, self.ltzian_w, self.ltzian_x0,
                 self.tlorentzian_chisquared, self.sigma_error, self.sigmaforchisquared,
                 self.klorentzian_chisquared, self.centroid, self.spread, self.e_f0, self.e_w, self.e_kmax, self.e_theta]
                
                os.chdir(graphdata)
                with open(filename+'.csv', 'w') as f:
                    self.df.to_csv(f)

                self.analysisfile = self.analysisfile.append(pandas.DataFrame(dict(zip(headers,c)), index=[0]))
                if item_is_list: 
                    self.item = self_itemseed[i]
                else:
                    self.item+=1
                
                # Free your mind (memory)
                self.figure.clf()
                plt.close(self.figure)
                gc.collect()

                t2 = time.time()
                timedeltas.append(t2-t1)
                print('ID:', id_num, ":", (i+1), "of", todo, '['+str(round((i+1)*100/todo,4))+'%]', "ETA: ", round((todo-(i+1))*numpy.mean(timedeltas),1), 's')
                continue

            continue


        else:
            return self.analysisfile, self.failedfiles

    def addEntry(self, k=[], h=None, addition='',dontwrite=False, appendme=None):
       # as the headers list in vna_visualizer.py
        headers = variablenames.na_global_analysis_headers

        if len(k) != 0:
            with open(k[0]+'.csv', 'w') as f:
                self.df.to_csv(f,index=False)
            v.add_entry(*k, headers=headers if h is not None else h, addition=addition,dontwrite=dontwrite)
        elif appendme is not None:
            v.add_entry(*headers, headers=headers if h is not None else h, appendme=appendme)
        else:
            with open(self.instancename+'.csv', 'w') as f:
                self.df.to_csv(f,index=False)
            v.add_entry(*c, headers=headers if h is not None else h, addition=addition,dontwrite=dontwrite)

    def __forkitindexer__(self, filelist):
        """
            Return a list of tuples of indecies that divide the passed
            list into almost equal slices
        """
        p = self.processes
        lenset = len(filelist)
        modulus = int(lenset%p)
        floordiv = int(lenset/p)
        slicer = [[floordiv*i, floordiv*(i+1)-1] for i in range(p-1)]
        slicer.append([floordiv*(p-1), p*floordiv+int(modulus)-1])
        return slicer

    def saveBoth(self):
        pass

    def failedFitCatcher(self, graphs, graphdata, home):
        singleThread = True
        failedfiles, failed_fits, failed_sindexes, failed_eindexes, failed_itemnos = [],[],[],[],[]
        for workpool_list in self.failedfiles:
            for failed_file, failed_automatefits, failed_startindex, failed_endindex, failed_itemno in workpool_list:
                failedfiles.append(failed_file)
                failed_fits.append(failed_automatefits)
                failed_sindexes.append(failed_startindex)
                failed_eindexes.append(failed_endindex)
                failed_itemnos.append(failed_itemno)
        #print(failedfiles, failed_fits, failed_sindexes, failed_eindex, failed_itemnos, sep='\n'+"#"*50+"\n")
        #exit()

        self.failedfiles = [[] for trash in self.failedfiles]
        # Now that we've collected the critical data, we need to
        #       reinitalize this current instance by executing a customized mainloop.

        matplotlib.use("TkAgg")
        self.fitnumber = 0
        self.xname= variablenames.agui_xname_default
        self.yname= variablenames.agui_yname_default
        self.rawsigpath = failedfiles[0]

        # Big gulp. This could have unintended consequences, but is necessary to re-visit failed fits.
        self.filelist= failedfiles
        self.failed_sindexes= failed_sindexes
        self.failed_eindexes= failed_eindexes
        self.failed_itemnos= failed_itemnos
        
        testval = self.mainloop(failedfit=True)

        if testval == "triggerAutomateMethod":
            failed_multi_threaded_indexes = self.__forkitindexer__(self.failed_itemnos)
            self.workpool = {}
            for index, value in enumerate(failed_multi_threaded_indexes):
                (start, end) = value
                self.workpool[index] = nmrAnalyser()
                self.workpool[index].overrideRootDir(self.rootdir)
                self.workpool[index].fetchArgs(fitnumber='fitnumber',
                    automatefits= self.automatefits,
                    material_type = self.material_type,
                    mutouse= self.mutouse,
                    binning= self.binning,
                    integrate= self.integrate,
                    vnavme= self.vnavme,
                    signalstart= self.signalstart,
                    signalend=self.signalend,
                    fitlorentzian= self.fitlorentzian,
                    xname= self.xname,
                    xaxlabel= self.xaxlabel,
                    yname= self.yname,
                    yaxlabel= self.yaxlabel,
                    xmin= self.xmin,
                    xmax= self.xmax,
                    startcolumn= self.startcolumn,
                    instancename= self.instancename,
                    title= self.plottitle,
                    isautomated= True,
                    filelist = failedfiles[start] if start==end else failedfiles[start:end],
                    rawsigpath = failedfiles[start],
                    baselinepath = self.baselinepath,
                    the_new_list=failed_itemnos[start] if start==end else failed_itemnos[start:end])
                self.workpool[index].updateItemSeed(start)

            if singleThread:
                results = [self.workpool[index].automatedPKernel(graphs, graphdata, home, index) for index,value in enumerate(failed_multi_threaded_indexes)]
            else:
                with multiprocessing.Pool(processes=self.processes) as pool:
                    result_objects = [pool.apply_async(self.workpool[index].automatedPKernel, args =(graphs, graphdata, home, index)) for index,value in enumerate(failed_multi_threaded_indexes)]
                    pool.close()
                    pool.join()

                del self.workpool

                results = [r.get() for r in result_objects]

            for results_df, failedfiles in results:
                self.analysisfile = self.analysisfile.append(results_df)
                self.failedfiles.append(failedfiles)
        elif testval == "giveUpRefitting":
            # let the function die, and this'll break the while-loop.
            #   in self.automate
            print("giveUpRefitting")
            pass



class daqExtractor(AsciiGUI):
    def __init__(self, args):
        self.header("DAQ Extractor")
        print("Extracts and organizes DAQ .csvs into .ta1 based on keywords found in variablenames.py and setting entered here, by the user.")
        self.selecton = ''
        self.fdump = ''
        self.rootdir = os.getcwd()
       
        self.mainloop()

    def mainloop(self):

        try:
            self.getSelection()
            self.getDestination()
            while True:
                self.choices()
        except KeyboardInterrupt:
            print("Keyboard Inturrupt recieved in mainloop. Exiting.")
            return True

    def getSelection(self):
        self.announcement("Pick directory or file to unpack")
        self.selection = self.fileDirectorySelector()
        self.is_file = os.path.isfile(self.selection)
        print("You selected", self.selection, "which is a", ('File' if self.is_file else 'Directory'))

    def getDestination(self):
        self.announcement("The current unpacking destination is " +str(self.fdump))
        while not os.path.isdir(self.fdump):
            self.header("Select a DIRECTORY to place files.")
            self.fdump = self.fileDirectorySelector()+'/'
            if os.path.isdir(self.fdump):
                print("Path accepted.")
                break
            else:
                self.announcement("Path REJECTED. Try selecting a directory with 'ok'.")



    def choices(self):
        selectmsg = 'Select file, or directory to unpack'
        destinationmsg = 'Select destination to place unpacked data'
        extractmsg = 'Extract current selection into analyzeable files'


        self.options = {'updateSelection':[selectmsg, self.getSelection],
            'updateDestination':[destinationmsg, self.getDestination],
            'extractData':[extractmsg, self.execute]
            }

        choice = self.dict_selector(self.options)
        f = self.options[choice][1]
        f()


    def execute(self):     
        if self.is_file:
            self.filelocation = self.selection
            daq_muncher.single_file(self.selection, self.fdump)
        else:
            self.filelocation = self.selection+'/'
            daq_muncher.directory(self.selection, self.fdump, self.rootdir)


class dirSorter(AsciiGUI):
    def __init__(self, args):
        self.header("Directory Sorter")
        print("Packs and unpacks directories by a width of time based on timestamps present in the .ta1 files")
        self.selecton = ''
        self.fdump = ''
        self.rootdir = os.getcwd()
        self.getSelection()
        self.mainloop()


    def mainloop(self):
        try:
            while True:
                self.choices()
        except KeyboardInterrupt:
            print("Keyboard Inturrupt recieved in mainloop. Exiting.")
            return True

    def getSelection(self):
        self.announcement("Pick directory to sort")
        self.selection = self.fileDirectorySelector(dironly=True)
        #self.selection += '/' # needed to make the fact this was a directory clear to the file organisers
        self.is_file = os.path.isfile(self.selection)
        print("You selected", self.selection, "which is a", ('File' if self.is_file else 'Directory'))
        if self.is_file:
            print("You selected an individual file. Please ONLY select a directory")
            print("this is done by entering 'ok' once the current working directory reads the desired path")
            self.getSelection()

    def choices(self):
        shelfmsg = "Organize the current directory per the user selected time-stamp"
        unshelfmsg = "Move files/folders in first child directories out to their parent directory"
        configuretimestepmsg = "Set the width of time to organize directories with."
        # Your mother was a:
        hampster = {'shelf':[shelfmsg, self.doShelf],
                    'unshelf':[unshelfmsg, self.unShelf],
                    'settimestep':[configuretimestepmsg, self.setTimestep]}
        # And your father smelt of            
        ELDER_BERRIES = self.dict_selector(hampster)

        you = hampster[ELDER_BERRIES][1]

        you()

    def doShelf(self):
        try:
            self.h, self.m, self.s
        except:
            self.setTimestep()
        directory_sorter.shelf(self.selection, hours=self.h, minutes=self.m, seconds=self.s)

    def unShelf(self):
        directory_sorter.unshelf(self.selection)

    def setTimestep(self):
        print("Enter the number of seconds:")
        self.s = self.getNumInRange(0, 59)
        print("Enter the number of minutes:")
        self.m = self.getNumInRange(0,59)
        print("Enter the number of hours:")
        self.h = self.getNumInRange(0,23)

        
def DAQExtractor(args):  
    instance = daqExtractor(args)
    del instance

def DirSorter(args):
    instance = dirSorter(args)
    del instance

def SweepAverager(args):
    instance = sweepAverager(args)
    del instance

class sweepAverager(AsciiGUI):
    def __init__(self, args):
        super().__init__(args, getrootdir=True)

        self.mainloop()


    def mainloop(self):
        self.updateLocation()
        try: 
            while True:
                self.choices()

        except KeyboardInterrupt:
            print("Keyboard Inturrupt detected. Returning")
            return True

    def choices(self):
        locationmsg = "Select directory for averaging"
        startmsg = "Start the avergaing process"

        choice = {'updatelocation':[locationmsg, self.updateLocation], "execute":[startmsg, self.execute], 
                  }

        key = self.dict_selector(choice)

        f = choice[key][1]
        f()

    def updateLocation(self):
        self.selection = self.fileDirectorySelector(dironly=True)
        print("You selected", self.selection, "which is a", ('File' if self.is_file else 'Directory'))
        if self.is_file:
            print("You selected an individual file. Please ONLY select a directory")
            print("this is done by entering 'ok' once the current working directory reads the desired path")
            self.getSelection()

    def execute(self):
        try:
            self.selection
        except AttributeError:
            self.updateLocation()
        choice = {"nested":['Avarage sweeps in a nested directory, naming avg sweep after parent directory'], 'directory':['average single directory into a single file']}
        key = self.dict_selector(choice)
        if key == "directory":
            sweep_averager.avg_single_dir(self.selection)
        elif key == "nested":
            sweep_averager.avg_nested_dirs(self.selection)


def GlobalInterpreter(args):
    instance = globalInterpreter(args)
    del instance

class globalInterpreter(AsciiGUI):
    def __init__(self, args):
        super().__init__(args, getrootdir=True)
        self.rootdir += '/'
        self.enhancedpath = ''
        self.tepath = ''
        self.deuteron = False

        self.mainloop()

    def mainloop(self):
        try:
            while True:
                self.choices()
        except KeyboardInterrupt:
            print("KeyboardInterrupt recieved. Returning.")
            return True

    def choices(self):
        updatetemsg = "Update TE global analysis path"
        updateenhancedmsg = "Update ENHANCED global analysis path"
        analyzetemsg = "Analyze only the TE global analysis"
        analyzeenhancedmsg = "Analyze the TE and ENHANCED global analysis"
        toggledeuteronmsg = "Toggle Deuteron status"

        choice = {'updatete':[updatetemsg, self.updateTE],
                    'updateenhanced':[updateenhancedmsg, self.updateEnhanced],
                    'toggleDeuteron':[toggledeuteronmsg, self.toggleDeuteron],
                    'onlyTE':[analyzetemsg,self.teonly],
                    'onlyEnhanced':[analyzeenhancedmsg, self.summarize]}

        key = self.dict_selector(choice)
        f = choice[key][1]
        f()


    def toggleDeuteron(self):
        print("\n\n Toggling deuteron from", str(self.deuteron), 'to', str(not self.deuteron))
        self.deuteron = not self.deuteron

    def updateEnhanced(self):
        print("Please update the ENHANCED path. Current selection is: ", self.enhancedpath)
        self.enhancedpath = self.fileDirectorySelector()

    def updateTE(self):
        print("Please update the TE path. Current selection is: ", self.tepath)
        self.tepath = self.fileDirectorySelector()


    def teonly(self):
        constants, teinfo = global_interpreter.collator(self.tepath, te=True, home=self.rootdir, deuteron=self.deuteron)
        print("Done. Have a nice day.")

    def summarize(self):
        constants,teinfo = global_interpreter.collator(self.tepath, te=True, home=self.rootdir, deuteron=self.deuteron)
        print("TE Global Analysis Complete. Applying calibration constant forward")
        global_interpreter.collator(self.enhancedpath, home=self.rootdir, deuteron=self.deuteron, constant=constants, to_save=teinfo)
        print("Enhanced Global analysis complete.")


def SpinCurves(args):
    instance = spinCurves(args)
    del instance
    print("Feature not entirely implemented.")

class spinCurves(AsciiGUI):
    def __init__(self, args):
        super().__init__(args, getrootdir=True)
        self.title = "Spin Curve"
        self.df = pandas.DataFrame()
        self.selection="None"

        self.HasTimes = False
        self.Hasplots = False

        self.sh, self.sm, self.ss, self.fh, self.fm, self.es = None,None,None,None,None,None

        self.time = variablenames.agui_se_time
        self.yax = variablenames.agui_se_yaxdef
        self.spinup= True

        self.mainloop()

    def mainloop(self):
        self.getSelection()
        self.selectDate()
        try:
            while True:
                self.currentSettings()
                if self.Hasplots:
                    self.figure.show()
                self.choices()
                plt.close('all')
                plt.clf()
        except KeyboardInterrupt:
            print("Keyboard Inturrupt recieved. Returning...")

    def currentSettings(self):
        cols = self.df.columns.values.tolist()
        self.announcement("Available DF Columns:")
        for index, i in enumerate(cols):
            print(i, end='\t')
            if index % 4 == 0:
                print('')
        print("")
        self.announcement("Current Settings:")
        print("Current File:", self.selection)
        print("Selected y-axis:", self.yax)
        print("Selected x-axis:", self.time)
        print("Current plot Title:", self.title)
        print("Current time selection:")
        if self.HasTimes:
            print("Start:", self.start.strftime('%m/%d/%Y %H:%M:%S'))
            print("End:", self.end.strftime('%m/%d/%Y %H:%M:%S'))

        self.ensure_yax()
        if self.HasTimes:
            self.preview()

    def choices(self):
        selectionmsg = "Select Parsed DAQ file OR Raw Global interpreter file"
        settitlemsg = "Set title for graph"
        selectdatemsg = "Set new time region"
        selectstarttime = "Set start time"
        setstartdate = "Set start date"
        updateEndTime = "Set end time"
        updateEndDate = "Set end date"
        executemsg = "Fit the plot"
        toggleupdownmsg = "Toggle Spin up / Spin Down mode"

        c = {"SelectCSV":[selectionmsg, self.getSelection],
            "TimeSelection":[selectdatemsg, self.selectDate],
            "SetTitle":[settitlemsg, self.settitle],
            "toggleSpinCurve":[toggleupdownmsg, self.togglespin],
            'updateStartTime':[selectstarttime, self.updateStartTime],
            'updateStartDate':[setstartdate, self.updateStartDate],
            'updateEndTime':[updateEndTime, self.updateEndTime],
            'updateEndDate':[updateEndDate, self.updateEndDate],
            'fitcurve':[executemsg, self.execute]
                }

        key = self.dict_selector(c)
        f = c[key][1]
        f()

    def updateStartTime(self):
        print("START TIME: Enter the number of seconds:")
        self.ss = int(self.getNumInRange(0, 59))
        print("START TIME: Enter the number of minutes:")
        self.sm = int(self.getNumInRange(0,59))
        print("START TIME:  Enter the number of hours:")
        self.sh = int(self.getNumInRange(0,23))

        self.updatestart()

    def updateStartDate(self):
        self.header("START DATE: Enter the START date in MM/DD/YYYY format")

        self.start_date = self.getMDY()
        self.Sd, self.Sm, self.Sy =  int(self.start_date.strftime('%d')), int(self.start_date.strftime('%m')),  int(self.start_date.strftime("%Y"))

        self.updatestart()

    def updateEndTime(self):
        print("END TIME: Enter the number of seconds:")
        self.es = int(self.getNumInRange(0, 59))
        print("END TIME: Enter the number of minutes:")
        self.fm = int(self.getNumInRange(0,59))
        print("END TIME: Enter the number of hours:")
        self.fh = int(self.getNumInRange(0,23))

        self.updateend()

    def updateEndDate(self):
        self.header("END DATE: Enter the END date in MM/DD/YYYY format")

        self.end_date = self.getMDY(end=True)
        if self.end_date == None:
            self.end_date = self.start_date 

        self.Fd, self.Fm, self.Fy = int(self.end_date.strftime('%d')), int(self.end_date.strftime('%m')),  int(self.end_date.strftime("%Y"))

        self.updateend()

    def togglespin(self):
        print("Currently in", "Spin Up" if self.spinup else "Spin Down", "Mode")
        self.spinup = not self.spinup
        print("Switching to", "Spin Up" if self.spinup else "Spin Down", "Mode")

    def settitle(self):
        print("Current plot title is: ", self.title)
        self.title = input("Input title: ")

    def getSelection(self):
        self.selection = self.fileDirectorySelector()
        self.updateDF()
        print("made it")
        self.ensure_yax()

    def updateDF(self):
        with open(self.selection, 'r') as f:
            self.df = pandas.read_csv(f)

    def ensure_yax(self):
        cols = self.df.columns.values.tolist()
        if self.yax not in cols:
            print("WARNING! current y-axis selection is NOT in the selected dataframe.")
            print("PLEASE select y-axis column in dataframe:")
            self.updateyax()

    def updateyax(self):
        print('Current y-axis is', self.yax, 'which is not in the current dataframe. Please select an option that is.')

        cols = self.df.columns.values.tolist()
        msg = "Column in Dataframe"
        the_choices = {}
        for i in cols:
            the_choices[i] = [msg]

        k = self.dict_selector(the_choices)
        print("Column updated to", k)
        self.yax = k

    def preview(self):
        self.Hasplots = True

        self.figure = spin_extractor.previewdata_gui(self.selection, self.title, self.Sd, self.Sm, self.Sy, self.sh,
                             self.sm,  self.fh,self.fm, self.yax, self.time, ss=self.ss, fs=self.es, Fd=self.Fd, Fm=self.Fm, Fy=self.Fy, preview=True)

    def selectDate(self):
        self.HasTimes = True
        self.updateStartDate()

        self.updateStartTime()
        
        self.updateEndDate()

        self.updateEndTime()
        
        
    def updatestart(self):
        self.start = self.start_date + datetime.timedelta(hours=0 if self.sh is None else self.sh, minutes=0 if self.sm is None else self.sm, seconds=0 if self.ss is None else self.ss)

    def updateend(self):
        self.end = self.end_date + datetime.timedelta(hours=0 if self.fh is None else self.fh, minutes=0 if self.fm is None else self.fm, seconds=0 if self.es is None else self.es)


    def execute(self):
        self.Hasplots = True
        self.figure = spin_extractor.getupdown(self.selection, self.title, self.Sd, self.Sm, self.Sy, 
                    self.sh, self.sm,  self.fh,self.fm, self.yax, self.time, up=self.spinup, 
                    ss=self.ss, fs=self.es, Fd=self.Fd, Fm=self.Fm, Fy=self.Fy)


class omniVIEW(AsciiGUI):
    def __init__(self, args):
        pass


    def omniview_gui(self, user_start, user_end, thermistors, xaxis, **kwargs):
        #       
        #       An in-memory way of viewing data from a particular timerange
        #
        comments=kwargs.pop("comments",False)
        save_fig=kwargs.pop("save_fig",False)
        dpi_val=kwargs.pop("dpi_val",150)
        gui=kwargs.pop("gui",False)
        ylabel=kwargs.pop("ylabel", "Ohms")

        plt.close('all')
        plt.clf()
        gc.collect()
        font = {'size': 4}
        plt.rc('font', **font)
        
        y_sarebad = False
        x_sarebad = False

        try:
            self.df
        except AttributeError:
            self.load_experimental_data()

        start_date = min(self.df[self.SliferLabTimeDefaultLabel])
        end_date = max(self.df[self.SliferLabTimeDefaultLabel])
        start_index = self.df[self.df[self.SliferLabTimeDefaultLabel]==start_date].index.to_list()[0]
        end_index = self.df[self.df[self.SliferLabTimeDefaultLabel]==end_date].index.to_list()[0]
        max_datapoints = 3000

        if user_start < user_end:
            fig = plt.figure(figsize=(fig_x_dim,fig_y_dim), dpi=dpi_val)
            if comments:
                print("Comments have been turned on")
                canvas = fig.add_subplot(111)
                graph = fig.add_subplot(211)
                footnotes = fig.add_subplot(212)
                footnotes.axis('off')
                canvas.axis('off')
            else:
                graph = fig.add_subplot(111)
            

            # __nearest(self, test_val, iterable)
            print("Locating nearest raw data-frame start index from user provided time")
            data_start_index = self.df[self.df[self.SliferLabTimeDefaultLabel] == self.__nearest(user_start, self.df[self.SliferLabTimeDefaultLabel])].index.to_list()[0]
            print("Start index located.", data_start_index)
            print("Locating nearest raw data-frame end index from user provided time")
            data_end_index = self.df[self.df[self.SliferLabTimeDefaultLabel] == self.__nearest(user_end, self.df[self.SliferLabTimeDefaultLabel])].index.to_list()[0]
            print("End index located.", data_end_index)
            delta = data_end_index-data_start_index
            index_modulus = (delta*(len(thermistors)-1))/max_datapoints

            
            if index_modulus <= 1:
                df_yslice = self.df.iloc[data_start_index:data_end_index:1]
            else:
                df_yslice = self.df.iloc[data_start_index:data_end_index:round(index_modulus)]
            
            df_yslice = df_yslice.convert_dtypes()
            df_xslice = self.df.loc[df_yslice.index.tolist(),xaxis].to_numpy() # GENERALIZE it.
            df_timeslice = self.df.loc[df_yslice.index.tolist(),self.SliferLabTimeDefaultLabel]


            if self.SliferLabTimeDefaultLabel not in xaxis:
                df_xsclice = self.__fix_dfslice(df_xslice)
                try:
                    df_xslice = df_xslice.astype(float)
                except ValueError as e:
                    x_sarebad = True
                    print("Can not convert", xaxis, "To numeric. X-Axis tick errors may occur.")
            yvals = {}
            for column in thermistors:
                if self.SliferLabTimeDefaultLabel not in column:
                    yvals[column] = self.__fix_dfslice(df_yslice[column])

            k = len(df_xslice)
            
            if comments:
                print("Querrying Logbook start")
                logbook_start = self.__nearest(user_start, self.logbook_df[self.SliferLabTimeDefaultLabel])
                print("Querrying Logbook end")
                logbook_end = self.__nearest(user_end, self.logbook_df[self.SliferLabTimeDefaultLabel])
                logbook_start_index = self.logbook_df[self.logbook_df[self.SliferLabTimeDefaultLabel] == logbook_start].index[0]
                logbook_end_index = self.logbook_df[self.logbook_df[self.SliferLabTimeDefaultLabel] == logbook_end].index[0]
                logbook_slice = self.logbook_df[logbook_start_index:logbook_end_index]
                print("Commenting Graph.")
                canvas, graph = self.__commenter(canvas, graph, logbook_slice, 
                                             df_timeslice, rng_ss=data_start_index, 
                                             rng_ee=data_end_index, avg=90, dpi_val=dpi_val
                                             )


            print("Sliced", k, "datapoints from", delta, "Total datapoints", "between", user_start, "and", user_end)
            graph.title.set_text("Data between "+user_start.strftime("%m/%d/%Y, %H:%M:%S")+" and "+user_end.strftime("%m/%d/%Y, %H:%M:%S"))
            graph.set_xlabel(xaxis)
            graph.set_ylabel(ylabel)
            

            for column in thermistors:
                graph.scatter(df_xslice,yvals[column], label=column, s=3)
            
            if self.SliferLabTimeDefaultLabel in xaxis:
                graph.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y/%m/%d %H:%M'))
                graph.xaxis_date()
                pass

            if y_sarebad:
                yticks = graph.get_yticks()
                cool_yticks = [yticks[i] for i in range(0,len(yticks), int(len(yticks)/10)+1)]
                graph.set_yticks(cool_yticks)
            if x_sarebad:
                xticks = graph.get_xticks()
                cool_xticks = [xticks[i] for i in range(0,len(xticks), int(len(xticks)/10)+1)]
                graph.set_xticks(cool_xticks)


            graph.legend(loc='best')


            if save_fig == True:
                plt.savefig(user_start.strftime("%m_%d_%Y_%H_%M_%S")+"_to_"+user_end.strftime("%m_%d_%Y_%H_%M_%S_"))
            elif gui:
                return fig
            else:
                plt.show()
        else:
            print("Bad Date selection.")  


    def __fix_dfslice(self,dfslice):
        a2 = []
        for index, value in enumerate(dfslice):
            to_fix = list(str(value))
            to_delete = []
            offs = []
            ##### Mark all non-alphanumerica special characters for deletion #####
            for index,character in enumerate(to_fix):
                if re.search(r'[\!\@\#\$\%\^\&\*\(\)\=\{\}\[\]\ \+]', character):
                    to_delete.append(index)
            ######################################################################
            if "off" in value or "Off" in value:
                # Set all offs to zero.
                offs.append(index)
                to_fix = ['0']
            else:
                for i in sorted(to_delete,reverse=True):
                    if i not in offs:
                        del to_fix[i]
            #print(index, "".join(to_fix))
            a2.append("".join(to_fix))
        return numpy.array(a2,dtype=numpy.float64)


    def __commenter(self, canvas, graph, logbook_slice, df_timeslice, rng_ss=0, keywords=[], rng_ee=0, avg=0, dpi_val=300):
        # THERE IS CURRENTLY A BUG WHERE IF COMMENTS ARE SET TO TRUE, IN THE GUI DATE-GRAPHER THIS THING WILL DROP TIMESTAMPS
        # ON THE COMMENTS OF THE FIGURES. I HAVE YET TO FIND OUT WHAT IS CAUSING THAT, BUT FOR NOW THE PROGRAM WORKS. 
        #
        """
        orig_x_dim = 32
        orig_y_dim = 18
        fig_x_basic_info = (0.25/16)*fig_x_dim
        fig_y_basic_info = (8.1/9)*fig_y_dim
        fig_x_end_range_data = (13/16)*fig_x_dim
        fig_x_start_range_data = (1.75/16)*fig_x_dim
        fig_y_range_data = (4.3/9)*fig_y_dim
        fig_x_logbook_comment = (0.25/16)*fig_x_dim
        fig_y_logbook_comment = (4.25/9)*fig_y_dim
        fig_x_timestamp = (0.25/16)*fig_x_dim
        fig_y_anchor_timestamp = (4.1/9)*fig_y_dim
        fig_y_step_timestamp = (.15/18)*fig_y_dim
        fig_x_comment_start = (1.2/16)*fig_x_dim
        """
        maxcolumnlen=30


        fig_x_timestamp = fig_x_dim/640
        fig_y_anchor_timestamp = 55*fig_y_dim/128
        fig_y_step_timestamp = 2*fig_y_dim/135
        fig_x_comment_start = 5*fig_x_dim/64
        fig_x_comment_rowshift = 85*fig_x_dim/256


        avg_comments = []
        poi = True
        v = 0
        n = 0
        was = False
        shift = False
        shift_2 = False
        trip = True
        for index, row in logbook_slice.iterrows():
            modified_comment, y = self.graph_comment_formater(row["Comment"])
            v += y # Current line
            timestamp = row[self.SliferLabTimeDefaultLabel]
            have_i_printed = False
            old_v = v
            old_n = n
            if v > maxcolumnlen:
                if not shift:
                    fig_x_comment_start += fig_x_comment_rowshift
                    fig_x_timestamp += fig_x_comment_rowshift
                    shift = True
                elif not shift_2 and v > 2*maxcolumnlen:
                    fig_x_comment_start += fig_x_comment_rowshift
                    fig_x_timestamp += fig_x_comment_rowshift
                    shift_2 = True
                
                if v > 2*maxcolumnlen:
                    v -= 2*maxcolumnlen
                    n -= 2*maxcolumnlen
                else:
                    v -= (maxcolumnlen+1)
                    n -= (maxcolumnlen+1)
            try:
                if df_timeslice[rng_ss] <= timestamp and timestamp <= df_timeslice[rng_ee-1]:
                    canvas.annotate(
                        timestamp, 
                        xy=(fig_x_timestamp*dpi_val,(fig_y_anchor_timestamp-fig_y_step_timestamp*n)*dpi_val), 
                        xycoords='figure pixels', color="green") 
                    avg_comments.append(n)
                else:
                    canvas.annotate(
                        timestamp, 
                        xy=(fig_x_timestamp*dpi_val,(fig_y_anchor_timestamp-fig_y_step_timestamp*n)*dpi_val), 
                        xycoords='figure pixels')
            except KeyError:
                if trip:
                    print("WARNING: Slicing miss-match. IGNORE if using Date Grapher with comments.")
                    trip = False
            n = old_n
            n += 1
            n += y
            if any(x in str(row["Comment"]) for x in keywords):
                if min(df_timeslice) <= row[self.SliferLabTimeDefaultLabel] and row[self.SliferLabTimeDefaultLabel] <= max(df_timeslice): 
                    canvas.annotate(
                        modified_comment, 
                        xy=(fig_x_comment_start*dpi_val,(fig_y_anchor_timestamp-fig_y_step_timestamp*v)*dpi_val),
                        xycoords='figure pixels', color='goldenrod')
                    x_loc = int(self.logbook_df[self.logbook_df["Comment"] == row["Comment"]].index[0])
                    logbook_hit_date = self.logbook_df.loc[x_loc, self.SliferLabTimeDefaultLabel]
                    graph.plot(
                        logbook_hit_date,
                        avg, 'ro',
                        color="goldenrod", ms=10, label=("Keyword Hit") if poi else None)
                    poi = False
                    have_i_printed = True
            if v in avg_comments:
                for index in avg_comments:
                    if v == index:
                        canvas.annotate(
                            modified_comment, 
                            xy=(fig_x_comment_start*dpi_val,(fig_y_anchor_timestamp-fig_y_step_timestamp*v)*dpi_val),
                            xycoords='figure pixels', color='green')
                    have_i_printed = True
            elif not have_i_printed:
                canvas.annotate(
                    modified_comment, 
                    xy=(fig_x_comment_start*dpi_val,(fig_y_anchor_timestamp-fig_y_step_timestamp*v)*dpi_val),
                    xycoords='figure pixels')
                have_i_printed = True
            v = old_v
            v += 1
            if shift_2 and v > 3*maxcolumnlen:
                print("WARNING: Out of lab-book comment space on figure. Consider selecting a narrower plotting range if labbook comment insight is critical.")
                return canvas,graph

        return canvas, graph


    def convert_df_yslice(self, thermistor, data):
        thermistors_in_file = ["CCS.F1","CCS.F2","CCS.F3","CCS.F4","AB.F5", "AB.F6", "CCS.F7", "CCS.F8","CCS.F9","CCS.F10", "CCS.F11", "CCS.S1", "CCS.S2", "CCS.S3"]
        if thermistor in thermistors_in_file:
            (a,b,c) = (self.coefficents_df.loc['a', thermistor], self.coefficents_df.loc['b', thermistor], self.coefficents_df.loc['c', thermistor])
            data2 = data.apply(convert_to_k, args=(a,b,c))
        else:
            data2 = data.apply(convert_to_k_spect, args=(), thermistor=thermistor)
        return data2


    def graph_comment_formater(self, comment):
        ls = list(str(comment))
        n = 0
        linelength = 69
        to_rm = []
        for element in range(0, len(ls)):
            if re.search(r'[\_\+\*\[\]\$\^\(\)\{\}\|\\]', ls[element]):
                    to_rm.append(element)
            if element % linelength == 0 and element != 0:
                if re.search('[a-zA-Z]', ls[element]):
                    ls.insert(element-1, '-')
                ls.insert(element, '\n')
                n += 1
        #print("".join(ls))
        for i in sorted(to_rm,reverse=True):
            del ls[i]
        #print("".join(ls))
        str_to_return = "".join(ls)
        return str_to_return, n


def main(args):
    def options():
        print("NMR Toolsuite options:")
        functions = [DAQExtractor, DirSorter, SweepAverager, NMRAnalyzer, GlobalInterpreter, SpinCurves]
        functionalities = ["DAQExtractor","DirSorter","SweepAverager","NMRAnalyzer","GlobalInterpreter", "SpinCurves"]

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
        except ValueError:
            print("Invalid Input")
            return options()

    functions = [DAQExtractor, DirSorter, SweepAverager, NMRAnalyzer, GlobalInterpreter,SpinCurves]
    optdict = dict(zip([i for i in range(len(functions))],functions))
    home = os.getcwd()
    while True:
        c= options()
        f = optdict[c]
        f(args)
        # Good idea to "clean up" so to set home directory, and return to it in-between functionalities.
        os.chdir(home)
        

    #while True:
        #c= options()
        #f = optdict[c]
        #f()
        """
        try:
            f = optdict[c]
            f()
        except KeyError as e:
            print("Something went wrong:",e)
            print("Invalid Option")
        """ 
    #print("NMR Toolsuite ASCII-GUI")
    #rootdir=os.getcwd()
    #cwd=rootdir

    #fixeddirs, fixedfiles = lsdir(cwd)
parser = argparse.ArgumentParser(description='Start the toolsuite')
parser.add_argument('--server-mode', dest='servermode', action='store_true', default=False,
                    help='Disable the .show methods on figures, useful for remote execution')

args = parser.parse_args()

main(args)