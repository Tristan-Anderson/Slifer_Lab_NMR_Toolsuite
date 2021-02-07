# PYTHON 3.9.1
"""
Tristan Anderson
tja1015@wildats.unh.edu

Proceed Formally.
"""
import NMR_Analyzer as v
import daq_muncher, directory_sorter,sweep_averager,global_interpreter
from matplotlib import pyplot as plt
import datetime,pandas,os,numpy,gc,time,multiprocessing,variablenames,matplotlib,argparse

"""
# TODO: Add overview of current settings on each mainloop in table format.
"""
class AsciiGUI():
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
        self.baselinepath = self.fileDirectorySelector()
        os.chdir(self.rootdir)
        self.announcement("Baseline path updated")

    def getRawsig(self):
        self.announcement("Update Raw Signal")
        print("Current working directory:",os.getcwd())
        self.rawsigpath = self.fileDirectorySelector()
        os.chdir(self.rootdir)
        self.announcement("Raw Signal path updated")

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

    def mainloop(self):
        try:
            self.getBaseline()
            them = '/'.join(self.baselinepath.split('/')[:-1])
            os.chdir(them)
            os.chdir('..')
            self.getRawsig()s
            self.fetchArgs()
            while True:
                if not self.servermode:
                    self.figure.show()
                print("#"*70)
                self.currentSettings()
                print("#"*70)
                self.header("Data frame head")
                print("#"*70)
                print(self.df.head(3))
                self.allchoices()
        except KeyboardInterrupt:
            print("Keyboard Inturrupt recieved in mainloop. Exiting.")
            return True

    def allchoices(self):
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
        f()

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
        self.announcement('Current binning is '+str(self.binning)+'.')
        print('Please select new binning')
        choices = 'hey'
        while type(choices) != int:
            try:
                choices = int(input("Enter bin width: "))
            except KeyboardInterrupt:
                print('keyboard inturrupt recived. Breaking.')
                return False
            except ValueError as e:
                print("Invalid input. Try again.", '\n'*2)
        self.binning = choices
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

    def saveFig(self,filename=None):
        filename = self.plottitle if filename is None else filename
        self.updateGraph()
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
        matplotlib.use('Agg') # Thwarts X-server Errors
        # Matplotlib is NOT thread-safe w/ known race conditions.
        # Care has been used to avoid these conditions
        # Let me know if I missed any.
        self.analysisfile = pandas.DataFrame()
        
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

        # To be implemented later
        self.failedfiles = []  # TODO: pass quirky into this namespace, and pop a key "hassucceeded"
                          # if True: do not append to this list
                          # else: append filename to this bad larry
                          # rewrite the loop, and cycle back through
                          # this list. It will involve proper invoking of fetch_kwargs()
                          # Which will be difficult to resolve logistically with self.item adding "S %ITEM"
                          # to the names of things.
        # Used to create unique instance names so pandas doesn't overwrite identical entries. (also human readability)
        self.workpool = {} 
        for index, value in enumerate(oh_indexes):
            (start, end) = value
            self.workpool[index] = nmrAnalyser()
            self.workpool[index].overrideRootDir(self.rootdir)
            self.workpool[index].fetchArgs(fitnumber='fitnumber',
                automatefits= self.automatefits,
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
                plottitle= self.plottitle,
                isautomated= True,
                filelist = ([tefiles[start]] if start==end else tefiles[start:end]),
                rawsigpath = self.rawsigpath,
                baselinepath = self.baselinepath)
            self.workpool[index].updateItemSeed(start)

        with multiprocessing.Pool(processes=self.processes) as pool:
            result_objects = [pool.apply_async(self.workpool[index].automatedPKernel, args =(graphs, graphdata, home, index)) for index,value in enumerate(oh_indexes)]
            pool.close()
            pool.join()
        # Keeper data / global analysis is in the results
        results = [r.get() for r in result_objects]

        # Cleanup behind ourselves.
        del self.workpool 

        # extract then merge individual results into a keeper data
        for i in results:
            self.analysisfile = self.analysisfile.append(i,ignore_index=True)
        print(self.analysisfile)
        input('Press any key to continue')
        self.addEntry(appendme=self.analysisfile)
        exit()

    def automatedPKernel(self, graphs, graphdata, home, id_num):
        return self.repeatAdNauseum(self.filelist,graphs, graphdata, home, id_num=id_num)

    def repeatAdNauseum(self, filelist, graphs, graphdata, home, failed=False, failedno=0, self_itemseed = None, id_num=''):
        # based on VME/VNA file selection what y-axis are we going to apply the user's settings to first on a blind loop
        self.analysisfile = pandas.DataFrame()

        self.item = int(self_itemseed) if self_itemseed is not None else self.item
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

            # As the user fit more than one function to the dataframe
            if not failed:
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
                    self.e_f0= rawsigfit.pop('e_f0', None)
                    self.e_w=rawsigfit.pop("e_w", None)
                    self.e_kmax=rawsigfit.pop('e_kmax', None)
                    self.e_theta=rawsigfit.pop("e_theta", None)
                    # Save this, because if we loop again, we're gonna need to fit subtract fit-subtracted data,
                    #   assuming thats what the user did; I made it so; actually otherwise the user overwrites
                    #   their last fit.
                    npriev = tupp[1]
                # Save the figure
                os.chdir(graphs)

                self.saveFig(filename=originalplottitle+" S"+str(self.item)+'.png') # UNCOMMENT TO SAVE EVERYTHING.

                """#######################################
                # A section dedicated to second-time-arrounders.
                if type(self.tlorentzian_chisquared) == float:
                    if self.tlorentzian_chisquared > 1.5:
                        self.failedfiles.append([file, self.item])
                        print("Poor chisquared fit while fitting: ", file)
                        #self.savefig(automated=True, p_title=originalplottitle+" S"+str(self.item))
                        self.item+=1
                        return False
                    elif self.tlorentzian_chisquared <= 1.5:
                        self.savefig(automated=True, p_title=originalplottitle+" S"+str(self.item))
                else:
                    self.failedfiles.append([file, self.item])
                    self.item+=1
                    return False
                #######################################"""


                os.chdir(home)
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
                c = [originalplottitle + " S"+str(self.item),  self.material_type,
                 self.te_date, self.vnavme, self.baselinepath, self.rawsigpath, self.xmin, self.xmax,
                 self.signalstart,self.signalend, self.blskiplines,
                 self.rawsigskiplines, str(self.B),
                 str(self.T), self.primary_thermistor, self.secondary_thermistor, self.tevalue,
                 self.dataarea, self.ltzian_integration, self.data_cal_constant,
                 self.fit_cal_constant, self.ltzian_a, self.ltzian_w, self.ltzian_x0,
                 self.tlorentzian_chisquared, self.sigma_error, self.sigmaforchisquared,
                 self.klorentzian_chisquared, self.centroid, self.spread, self.e_f0, self.e_w, self.e_kmax, self.e_theta]
                #os.chdir(graphdata)

                self.analysisfile = self.analysisfile.append(pandas.DataFrame(dict(zip(headers,c)), index=[0]))
                
                self.item+=1
                # Free your mind (memory)
                self.figure.clf()
                plt.close(self.figure)
                #self.canvas.destroy()
                gc.collect()

                t2 = time.time()
                timedeltas.append(t2-t1)
                print('ID:', id_num, ":", (i+1), "of", todo, '['+str(round((i+1)*100/todo,4))+'%]', "ETA: ", round((todo-(i+1))*numpy.mean(timedeltas),1), 's')

        return self.analysisfile

    def addEntry(self, k=[], h=None, addition='',dontwrite=False, appendme=None):
       # as the headers list in vna_visualizer.py
        headers = variablenames.na_global_analysis_headers

        if len(k) != 0:
            with open(k[0]+'.csv', 'w') as f:
                self.df.to_csv(f)
            v.add_entry(*k, headers=headers if h is not None else h, addition=addition,dontwrite=dontwrite)
        elif appendme is not None:
            v.add_entry(*headers, headers=headers if h is not None else h, appendme=appendme)
        else:
            with open(self.instancename+'.csv', 'w') as f:
                self.df.to_csv(f)
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
        self.announcement("Pick directory or file to unpack")
        self.selection = self.fileDirectorySelector()
        self.selection += '/' # needed to make the fact this was a directory clear to the file organisers
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
        try: 
            while True:
                self.choices()

        except KeyboardInterrupt:
            print("Keyboard Inturrupt detected. Returning")
            return True

    def choices(self):
        locationmsg = "Select directory for averaging"
        startmsg = "Start the avergaing process"

        choice = {'updatelocation':[locationmsg, self.updateLocation], "execute":[startmsg, self.execute]}

        key = self.dict_selector(choice)

        f = choice[key][1]
        f()

    def updateLocation(self):
        self.selection = self.fileDirectorySelector() + '/'
        self.is_file = os.path.isfile(self.selection)
        print("You selected", self.selection, "which is a", ('File' if self.is_file else 'Directory'))
        if self.is_file:
            print("You selected an individual file. Please ONLY select a directory")
            print("this is done by entering 'ok' once the current working directory reads the desired path")
            self.getSelection()

    def execute(self):
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
        global_interpreter.collator(self.enhancedpath, home=self.dumppath, deuteron=self.deuteron, constant=constants, to_save=teinfo)
        print("Enhanced Global analysis complete.")


def main(args):
    def options():
        print("NMR Toolsuite options:")
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
        except ValueError:
            print("Invalid Input")
            return options()

    functions = [NMRAnalyzer, DAQExtractor, DirSorter, SweepAverager, GlobalInterpreter]
    optdict = dict(zip([i for i in range(len(functions))],functions))
    while True:
        c= options()
        f = optdict[c]
        f(args)
        

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