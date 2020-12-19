"""
Tristan Anderson
tja1015@wildats.unh.edu

Proceed Formally.
"""
import gc, time # garbage
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import filedialog
import NMR_Analyzer as v
import daq_muncher, directory_sorter,sweep_averager,global_interpreter
from statistics import mode
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import datetime, pandas, os, numpy
# Implement the default Matplotlib key bindings.
"""
I have almost no formal training with GUIs.
All this stuff is self taught
and found from the library's documentation.

Each class is its own window-pane.
"""

class NMR_Visualizer(tk.Tk):                # Class
    """
        The main() but for this gui.
    """
    def __init__(self, *args, **kwargs):            # Method
        
        tk.Tk.__init__(self, *args, **kwargs)
        window = tk.Frame(self)

        window.pack(side="top", fill="both", expand=True)

        window.grid_rowconfigure(0, weight=1)
        window.grid_columnconfigure(0,weight=1)

        self.frames = {}                            # Attribute            
        options = [NMR_Splash, File_Selector, Data_Selector, Fitting_Page, 
                   DAQ_Extractor, Global_Interpreter, Directory_Sorter,
                   Sweep_Averager]
        for F in options:
            frame = F(window, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(cont=NMR_Splash)

    def show_frame(self, **kwargs):
        cont = kwargs.pop('cont', False)

        vnavme = kwargs.pop('vnavme',None)
        rawsigdatapath = kwargs.pop('rawsigdatapath',None)
        bldatapath = kwargs.pop('bldatapath', None)
        blskiplines = kwargs.pop('blskiplines', None)
        rawsigskiplines = kwargs.pop('rawsigskiplines', None)

        df=kwargs.pop('df', None)
        start_index=kwargs.pop('start_index', None)
        end_index=kwargs.pop('end_index', None)
        xname = kwargs.pop('xname',None)
        yname = kwargs.pop('yname',None)
        binning=kwargs.pop('binning',None)

        xlabel=kwargs.pop('xlabel',None)
        ylabel=kwargs.pop('ylabel',None)                            
        xmin=kwargs.pop('xmin', tk.StringVar(value="-∞"))
        xmax=kwargs.pop('xmax', tk.StringVar(value="-∞"))
        signalstart=kwargs.pop('signalstart',tk.StringVar(value=""))
        signalend=kwargs.pop('signalend',tk.StringVar(value=""))
        impression = kwargs.pop('impression', True)
        rawsigtime = kwargs.pop('rawsigtime', None)
        mag_current = kwargs.pop("mag_current", None)
        temperature = kwargs.pop("temperature", None)

        startcolumn = kwargs.pop("startcolumn", None)

        vapor_pressure_t = kwargs.pop("vapor_pressure_t",None)
        cccst3_t = kwargs.pop("cccst3_t", None)

        spread=kwargs.pop('spread', None)
        centroid=kwargs.pop('centroid',None)


        frame = self.frames[cont]

        frame.fetch_kwargs(
                                    vnavme=vnavme, rawsigdatapath=rawsigdatapath, bldatapath=bldatapath,
                                    blskiplines=blskiplines, rawsigskiplines=rawsigskiplines, df=df,
                                    start_index=start_index, end_index=end_index, yname=yname,
                                    xname=xname, binning=binning, xlabel=xlabel, ylabel=ylabel,
                                    xmin=xmin, xmax=xmax, signalstart=signalstart, signalend=signalend,
                                    impression=impression, rawsigtime=rawsigtime, mag_current=mag_current,
                                    temperature=temperature, vapor_pressure_t=vapor_pressure_t,
                                    cccst3_t=cccst3_t, spread=spread,centroid=centroid, startcolumn=startcolumn
                                  )
        
        frame.tkraise()

### Future tkinter Windows time permitting ###
class DAQ_Extractor(tk.Frame):
    def __init__(self,parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.guiTitle = tk.LabelFrame(self, text="NMR DAQ Extractor")
        self.guiTitle.grid(column=0,row=0,padx=35, pady=10)

        self.daqframe = tk.LabelFrame(self.guiTitle, text="DAQ File Selection")
        self.daqframe.grid(column=0,row=1, pady=10)

        self.dirFileStrvar = tk.StringVar(value='Directory')
        tk.Radiobutton(self.daqframe, text="Directory", variable=self.dirFileStrvar, value="Directory").grid(column = 1, row = 0)
        tk.Radiobutton(self.daqframe, text="File", variable=self.dirFileStrvar, value="File").grid(column = 1, row = 2)
        #self.vnaVmeType.grid(column=1, row=1)
        self.daqFileSelectorButton = tk.Button(self.daqframe, text = "Select Raw DAQ File/Directory", command = self.daqFileDialog)
        self.daqFileSelectorButton.grid(column = 0, row = 1,padx=35)
        

        self.exportLF = tk.LabelFrame(self.guiTitle, text = "Select Export Directory")
        self.exportLF.grid(column = 0, row = 2,padx=35)

        self.exportButton = tk.Button(self.exportLF, text= "Select Export Destination", command=self.daqExportDialog)
        self.exportButton.grid(column=0,row=0)
        
       
        self.start = tk.Button(self.guiTitle, text = "Start", command=self.execute)
        self.start.grid(column = 3, row = 1,padx=35)

        self.back_2_splash = tk.Button(self.guiTitle, text="Back to Splash", command= lambda:self.controller.show_frame(cont=NMR_Splash))
        self.back_2_splash.grid(column=3, row=2,padx=35)

    def fetch_kwargs(self, **kwargs):
        self.populate_toggleables()

    def populate_toggleables(self):
        # Nothing to pass (as of yet!)
        pass

    def execute(self):
        self.cwd = os.getcwd()+'/'
        self.fdump = self.daqexportname+'/'
        
        status = self.dirFileStrvar.get()
        if status == "Directory":
            self.filelocation = self.daqfilename+'/'
            daq_muncher.directory(self.filelocation, self.fdump, self.cwd)
        if status == "File":
            self.filelocation = self.daqfilename
            daq_muncher.single_file(self.filelocation, self.fdump)

        #daq_muncher.file_muncher(self.)
        #print(self.daqexportname)

    def daqFileDialog(self):
        status = self.dirFileStrvar.get()
        if status == "Directory":
            
            self.daqfilename = filedialog.askdirectory(initialdir =  "$HOME/raw_data", title = "Select A File")
            self.daqFileSelectorButton.configure(text = self.daqfilename)
            
        elif status == "File":
            
            self.daqfilename = filedialog.askopenfilename(initialdir =  "$HOME/raw_data", title = "Select A File")
            self.daqFileSelectorButton.configure(text = self.daqfilename)


    def daqExportDialog(self):
        self.daqexportname = filedialog.askdirectory(initialdir =  "$HOME/raw_data", title = "Select A Directory")
        self.exportButton.configure(text=self.daqexportname)


class Global_Interpreter(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.dumppath = os.getcwd()
        self.tepath, self.enhancedpath, self.dumppath = '', '', ''
        self.controller = controller

        self.guiTitle = tk.LabelFrame(self, text='File Selection')
        self.guiTitle.grid(column=0,row=0)

        self.TEbutton = tk.Button(self.guiTitle, text="TE Global Analysis", command = self.TEfiledialog)
        self.TEbutton.grid(column=0, row=0)

        self.teonlycheckbutton = tk.StringVar(value=0)
        self.TEOnlyButton=tk.Checkbutton(self.guiTitle, text="Cal Only", onvalue='1', offvalue='0',variable=self.teonlycheckbutton)
        self.TEOnlyButton.grid(column=1,row=0)

        self.enhancedbutton = tk.Button(self.guiTitle, text='Enhanced Global Analysis', command =self.ENfiledialog)
        self.enhancedbutton.grid(column=0, row=1)

        self.dumppath_button = tk.Button(self.guiTitle, text="Results Path", command=self.dumpdialog)
        self.dumppath_button.grid(column=0,row=2)

        self.checkbutton = tk.StringVar(value=1)
        self.deuteronCheck = tk.Checkbutton(self.guiTitle, text="Deuteron", onvalue='1', offvalue='0', variable=self.checkbutton)
        self.deuteronCheck.grid(column=1, row=2)
        #self.deuteronlabel = tk.Label(value="Deuteron")
        self.go = tk.Button(self.guiTitle, text="Start", command = self.summarize)
        self.go.grid(column=0, row=3)

        self.back = tk.Button(self.guiTitle, text="Back", command = lambda: self.controller.show_frame(cont=NMR_Splash))
        self.back.grid(column=1,row=3)

    def teonly(self):
        deuteron = False if self.checkbutton.get() == '0' else True
        constants, teinfo = global_interpreter.collator(self.tepath, te=True, home=self.dumppath, deuteron=deuteron)
        print("Done. Have a nice day.")
    def fetch_kwargs(self, **kwargs):
        self.populate_toggleables()

    def summarize(self):
        techeckbutton = False if self.teonlycheckbutton.get() == '0' else True
        if techeckbutton:
            self.teonly()
            return True
        deuteron = False if self.checkbutton.get() == '0' else True
        constants, teinfo = global_interpreter.collator(self.tepath, te=True, home=self.dumppath, deuteron=deuteron)
        print("TE Global Analysis Complete. Applying calibration constant forward")
        global_interpreter.collator(self.enhancedpath, home=self.dumppath, deuteron=deuteron, constant=constants, to_save=teinfo)
        print("Enhanced Global analysis complete.")

    def populate_toggleables(self):
        pass

    def TEfiledialog(self):
        self.tepath = filedialog.askopenfilename(initialdir =  "$HOME/raw_data", title = "Select A File")
        self.TEbutton.configure(text=self.tepath)

    def ENfiledialog(self):
        self.enhancedpath = filedialog.askopenfilename(initialdir =  "$HOME/raw_data", title = "Select A File")
        self.enhancedbutton.configure(text=self.enhancedpath)

    def dumpdialog(self):
        self.dumppath = filedialog.askdirectory(initialdir =  "$HOME/raw_data", title = "Select A File")+'/'
        self.dumppath_button.configure(text=self.dumppath)

class Directory_Sorter(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.guiTitle = tk.LabelFrame(self, text="NMR Sweep Sorter")
        self.guiTitle.grid(column=0,row=0,padx=35, pady=10)

        self.status = tk.StringVar(value='shelf')
        tk.Radiobutton(self.guiTitle, text="Shelf (Organize into Child Dirs)", variable=self.status, value="shelf").grid(column=2,row=0, pady=10)
        tk.Radiobutton(self.guiTitle, text="Un-Shelf (Remove from Child Dirs into Root Dir)", variable=self.status, value="unshelf").grid(column=2,row=2, pady=10)
        self.sortd_LF = tk.LabelFrame(self.guiTitle, text="Directory to Sort")
        self.sortd_LF.grid(column=0,row=1, pady=10)

        self.directory_Button = tk.Button(self.sortd_LF, text='Pick Directory', command=self.pickdir)
        self.directory_Button.grid(column=0, row=1)

        self.timedelta_organize_LF = tk.LabelFrame(self, text="Timedelta")
        self.timedelta_organize_LF.grid(column=1, row=0, padx=35,pady=10)
        
        hours = [str(i) for i in range(0,24)]
        minutes = [str(i) for i in range(0,60)]
        seconds = minutes
        
        self.timedeltalabel = tk.Label(self.timedelta_organize_LF, text="Timedelta Selection:")
        self.timedeltalabel.grid(column=1,row=0)
        
        self.hourslabel = tk.Label(self.timedelta_organize_LF, text="Hours:")
        self.hourslabel.grid(column=0, row=1)
        self.hours = tk.StringVar(self)
        self.hours.set(hours[0])
        self.hoursPulldown = tk.OptionMenu(self.timedelta_organize_LF, self.hours, *hours)
        self.hoursPulldown.grid(column=2, row=1)
        
        self.minuteslabel = tk.Label(self.timedelta_organize_LF, text="Minutes:")
        self.minuteslabel.grid(column=0, row=2)
        self.minutes = tk.StringVar(self)
        self.minutes.set(minutes[0])
        self.minutesPulldown = tk.OptionMenu(self.timedelta_organize_LF, self.minutes, *minutes)
        self.minutesPulldown.grid(column=2, row=2)
        
        self.secondslabel = tk.Label(self.timedelta_organize_LF,text="Seconds:")
        self.secondslabel.grid(column=0,row=3)
        self.seconds = tk.StringVar(self)
        self.seconds.set(seconds[0])
        self.secondsPulldown = tk.OptionMenu(self.timedelta_organize_LF, self.seconds, *seconds)
        self.secondsPulldown.grid(column=2, row=3)

        self.beginButton = tk.Button(self.timedelta_organize_LF, text="Organize", command=self.organize)
        self.beginButton.grid(column=1,row=4, padx=25,pady=10)

        self.backbutton = tk.Button(self, text="Back", command=lambda: self.controller.show_frame(cont=NMR_Splash))
        self.backbutton.grid(column=0,row=1)
    def fetch_kwargs(self, **kwargs):
        self.populate_toggleables()

    def populate_toggleables(self):
        pass

    def organize(self):
        h = int(self.hours.get())
        m = int(self.minutes.get())
        s = int(self.seconds.get())
        status = self.status.get()
        if status == "shelf":
            directory_sorter.shelf(self.location, hours=h, minutes=m, seconds=s)
        elif status == "unshelf":
            directory_sorter.unshelf(self.location)

    def pickdir(self):
        self.location = filedialog.askdirectory(initialdir =  "$HOME/raw_data", title = "Select A File")+'/'
        self.directory_Button.configure(text = self.location)


class Sweep_Averager(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.guiTitle = tk.LabelFrame(self, text="Sweep Averager")
        self.guiTitle.grid(column=0, row=0)

        self.status = tk.StringVar(value="directory")
        
        self.location_Button = tk.Button(self.guiTitle, text="Select Location to Average", command=self.pickdir)
        self.location_Button.grid(column=0, row=1)
        tk.Radiobutton(self.guiTitle, text="Directory", value='directory', variable=self.status).grid(column=1,row=1)
        tk.Radiobutton(self.guiTitle, text="Nested Directory", value='nested', variable=self.status).grid(column=1,row=2)

        self.sweep_averager_button = tk.Button(self.guiTitle, text='Start', command=self.send_it)
        self.sweep_averager_button.grid(column=3, row=3)
        
        self.backbutton = tk.Button(self.guiTitle, text="Back", command = lambda: self.controller.show_frame(cont=NMR_Splash))
        self.backbutton.grid(column=2, row=3)
    def fetch_kwargs(self, **kwargs):
        #
        self.populate_toggleables()

    def populate_toggleables(self):
        #
        pass

    def send_it(self):
        status = self.status.get()
        if status == "directory":
            sweep_averager.avg_single_dir(self.location)
        elif status == "nested":
            sweep_averager.avg_nested_dirs(self.location)

    def pickdir(self):
        self.location = filedialog.askdirectory(initialdir =  "$HOME/raw_data", title = "Select A File")+'/'
        self.location_Button.configure(text = self.location)


class NMR_Splash(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        #tk.Label(self, text="NMR Toolsuite").grid(column=0,row=0)
        
        self.controller = controller

        self.splashFrame = tk.LabelFrame(self, text="NMR Toolsuite")
        self.splashFrame.grid(column=0, row=0, padx=120)
        self.goto_analyser = tk.Button(self.splashFrame,text="NMR Signal Extractor", command= lambda: self.controller.show_frame(cont=File_Selector))
        self.goto_analyser.grid(column=0, row=1, pady=10)

        self.goto_DAQ_extractor = tk.Button(self.splashFrame, text="DAQ Extractor", command = lambda: self.controller.show_frame(cont=DAQ_Extractor))
        self.goto_DAQ_extractor.grid(column=0,row=2, pady=10)

        self.ta1DirSorter = tk.Button(self.splashFrame, text="Sweep Sorter", command=lambda: self.controller.show_frame(cont=Directory_Sorter))
        self.ta1DirSorter.grid(column=0,row=3, pady=10)

        self.sweepavgr = tk.Button(self.splashFrame, text="Sweep Averager", command=lambda:self.controller.show_frame(cont=Sweep_Averager))
        self.sweepavgr.grid(column=0, row=4, pady=10)

        self.globalinterpreter = tk.Button(self.splashFrame, text="Global Interpreter", command = lambda:self.controller.show_frame(cont=Global_Interpreter))
        self.globalinterpreter.grid(column=0,row=5, pady=10)

    def fetch_kwargs(self, **kwargs):
        pass
### Future tkinter Windows time permitting ###

class File_Selector(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        

        self.controller = controller
        #self.wm_iconbitmap('icon.ico')
        self.guiTitle = tk.Label(self, text="NMR Data Analyser")
        self.guiTitle.grid(column=1,row=1)

        self.rawsigDataFileSelector = tk.LabelFrame(self, text = "Select Raw Data File")
        self.rawsigDataFileSelector.grid(column = 2, row = 2, padx=10, pady=10)
        

        self.bldataFileSelector = tk.LabelFrame(self, text = "Select Baseline Data File")
        self.bldataFileSelector.grid(column = 0, row = 2, padx=10, pady=10)

        self.return_to_splash = tk.Button(self, text="Return to Splash", command= lambda: self.controller.show_frame(cont=NMR_Splash))
        self.return_to_splash.grid(column=1, row=3)
       
        self.Switches = tk.LabelFrame(self, text = "File Parsing Options")
        self.Switches.grid(column = 0, row = 1, padx=10, pady=10)

        self.delimeter = tk.LabelFrame(self, text="Backslash/ASCII File Delimeter")
        self.delimeter.grid(column=2, row=1, padx=10, pady=10)

        self.skipLines = tk.LabelFrame(self, text="Header Lines (Skip this # of lines)")
        self.skipLines.grid(column=1, row=2, padx=10, pady=10)

        self.continueButton = tk.LabelFrame(self, text="Next Step: Data Selection")
        self.continueButton.grid(column=3,row=4)

        self.rawsigbutton()
        self.baselinebutton()
        self.vnaneRadioButton()
        self.fileDelimeter()
        self.goTransition()



    def vnaneRadioButton(self):
        self.vnaVmeType = tk.StringVar(self.Switches)
        self.vnaVmeType.set('VNA')
        tk.Radiobutton(self.Switches, text="VNA", variable=self.vnaVmeType, value="VNA").pack()
        tk.Radiobutton(self.Switches, text="VME", variable=self.vnaVmeType, value="VME").pack()
        #self.vnaVmeType.grid(column=1, row=1)

    def fileDelimeter(self):
        self.fileDelimeter = tk.StringVar()
        e = tk.Entry(self.delimeter, textvariable=self.fileDelimeter)
        e.pack()
        self.fileDelimeter.set("\\t")

    def skipLinesPulldown(self):
        #Future proof headroom
        skip = [str(i) for i in range(1,21)]
        tkvar = tk.StringVar(self)
        tkvar.set(skip[0])
        self.skiplinesPulldown = tk.OptionMenu(self.skipLines, tkvar, *skip)
        self.skiplinesPulldown.grid(column=1, row=2)
 
    def baselinebutton(self):
        self.baselinebutton = tk.Button(self.bldataFileSelector, text = "Select Baseline",command = self.baselinefileDialog)
        self.baselinebutton.grid(column = 1, row = 2)
 
    def baselinefileDialog(self):
        if self.vnaVmeType.get() == "VNA":
            ftyps = (('VNA File', "*.s1p"),("all files","*.*"))
        elif self.vnaVmeType.get() == "VME":
            ftyps = (("VME File", "*.ta1"),("all files","*.*"))
        self.blfilename = filedialog.askopenfilename(initialdir =  "$HOME", title = "Select A File", filetypes = ftyps)
        self.bllabel = tk.Label(self.bldataFileSelector, text = "")
        self.bllabel.grid(column = 1, row = 2)
        self.bllabel.configure(text = self.blfilename)
        self.blFilePreview()

    def blFilePreview(self):
        self.bldataFile = tk.LabelFrame(self, text='200-line Baseline Data Preview')
        self.bldataFile.grid(column=0, row=3, pady=10, padx=10)
        delimeter = self.fileDelimeter.get()
        choice = self.vnaVmeType.get()
        self.bltxt = scrolledtext.ScrolledText(self.bldataFile)
        #txt['font'] = ('Noto Sans Gothic', '12')
        self.bltxt.pack(expand=True, fill='both')
        if delimeter == '\\t':
            delimeter ='\t'

        h2, header, tf_file, lines_to_skip = v.gui_bl_file_preview(self.blfilename, delimeter)

        for r, row in enumerate(h2):
            line = ""
            for c, col in enumerate(h2[r].split(delimeter)):
                line += col
            if r == lines_to_skip:
                self.bltxt.insert(tk.END, "#"*5+" WHERE THE PROGRAM DETECTS THE DATA BEGINNING "+"#"*5+'\n')
            if r<99:
                self.bltxt.insert(tk.END, line)
            if r == 99:
                self.bltxt.insert(tk.END, line)

        self.blskiplines = lines_to_skip

    def fetch_kwargs(self, **kwargs):
        self.signalstart = kwargs.pop("signalstart", tk.StringVar())
        self.signalend = kwargs.pop("signalend", tk.StringVar())

        self.xmin = kwargs.pop('xmin', tk.StringVar(value="-∞"))
        self.xmax = kwargs.pop('xmax', tk.StringVar(value="∞"))

        try:
            self.xmin.get()
        except AttributeError:
            self.xmin.set("-∞")
        try:
            self.xmax.get()
        except AttributeError:
            self.xmax.set("-∞")

    def rawsigbutton(self):
        self.rawsigbutton = tk.Button(self.rawsigDataFileSelector, text = "Select Signal",command = self.rawsigfileDialog)
        self.rawsigbutton.grid(column = 1, row = 1)
 
    def rawsigfileDialog(self):
        if self.vnaVmeType.get() == "VNA":
            ftyps = (('VNA File', "*.s1p"),("all files","*.*"))
        elif self.vnaVmeType.get() == "VME":
            ftyps = (("VME File", "*.ta1"),("all files","*.*"))
        self.rawsigfilename = filedialog.askopenfilename(initialdir =  "$HOME", title = "Select A File", filetypes =
        ftyps)
        self.rawsiglabel = tk.Label(self.rawsigDataFileSelector, text = "")
        self.rawsiglabel.grid(column = 1, row = 1)
        self.rawsiglabel.configure(text = self.rawsigfilename)
        #print("".join(list(self.rawsigfilename.split('/')[-1])[:-4]))
        self.teFilePreview()

    def teFilePreview(self):
        self.rawsigDataFile = tk.LabelFrame(self, text='200-line Raw Data Preview')
        self.rawsigDataFile.grid(column=2, row=3, padx=10, pady=10)
        delimeter = self.fileDelimeter.get()
        choice = self.vnaVmeType.get()
        self.rawtext = scrolledtext.ScrolledText(self.rawsigDataFile)
        #txt['font'] = ('Noto Sans Gothic', '12')
        self.rawtext.pack(expand=True, fill='both')
        if delimeter == '\\t':
            delimeter ='\t'
        header = []
        h2 = []
        

        # Get the info
        header, h2, self.TE_DATE, self.I, self.T,\
        self.cccst3_t, self.vapor_pressure_t, \
        self.rawsigskiplines, self.centroid, \
        self.spread = v.gui_rawsig_file_preview(self.rawsigfilename, delimeter, self.vnaVmeType.get())
        
        

        for r, row in enumerate(h2):
            line = ''
            for c, col in enumerate(h2[r].split(delimeter)):
                line += col
            if r == self.rawsigskiplines:
                self.rawtext.insert(tk.END, "#"*5+" WHERE THE PROGRAM DETECTS THE DATA BEGINNING "+"#"*5+'\n')
            if r<99:
                self.rawtext.insert(tk.END, line)
            if r == 99:
                self.rawtext.insert(tk.END, line)
        
    def goTransition(self):
        self.gotransition = tk.Button(
                                        self.continueButton, text = "Continue",
                                        command = lambda: self.controller.show_frame(cont=Data_Selector, 
                                        vnavme=self.vnaVmeType.get(), 
                                        rawsigdatapath=self.rawsigfilename, 
                                        bldatapath=self.blfilename,
                                        rawsigskiplines=self.rawsigskiplines,
                                        blskiplines=self.blskiplines,
                                        impression=True,
                                        rawsigtime=self.TE_DATE, mag_current = self.I,
                                        temperature=self.T,
                                        vapor_pressure_t=self.vapor_pressure_t,
                                        cccst3_t=self.cccst3_t,
                                        signalstart=self.signalstart,
                                        signalend=self.signalend,
                                        xmin=self.xmin,
                                        xmax = self.xmax,
                                        centroid=self.centroid,
                                        spread=self.spread
                                        )
                                      )
        self.gotransition.grid(column = 1, row = 1)
        
    def get_dataframe(self):
        return v.gui_file_fetcher(
                                    self.rawsigfilename, self.blfilename, self.vnaVmeType.get(), impression=False, datatype=self.vnaVmeType.get(),
                                    blskiplines=self.blskiplines, rawsigskiplines=self.rawsigskiplines
                                 )


class Data_Selector(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        
        self.controller = controller

        self.guiTitle = tk.Frame(self)#, text="Options")
        self.guiTitle.grid(column=1,row=0)

        self.toggleables = tk.LabelFrame(self.guiTitle, text="Data Selection")
        self.toggleables.grid(column=1, row=2)
    
    def update_everything(self, impression=False, usertriggered=False):
        self.binning = int(self.binningvalue.get())
        self.update_dataframe(impression=impression)
        if usertriggered:
            self.trim_data()
        self.data_displayer()
        self.populatetoggleables()
        self.update_graph()
        self.backforth()

    def onwards(self):
        #self.update_dataframe(impression=False)
        #self.trim_data()
        self.update_everything_ut()
        self.startcolumn = self.yname.get()
        self.controller.show_frame(
            cont=Fitting_Page, vnavme=self.vnavme,
            rawsigdatapath=self.rawsigDataFile, bldatapath=self.bldataFile,
            blskiplines=self.blskiplines, rawsigskiplines=self.rawsigskiplines,
            df=self.df, start_index=self.start_index, end_index=self.end_index,
            xname = self.xname, yname = self.yname, binning=self.binningvalue,
            xlabel=self.xaxlabel, ylabel=self.yaxlabel,
            xmin=self.xmin, xmax=self.xmax, signalstart=self.signalstart,
            signalend=self.signalend, rawsigtime=self.rawsigtime, temperature=self.T,
            mag_current=self.I, vapor_pressure_t=self.vapor_pressure_t,
            cccst3_t=self.cccst3_t, centroid=self.centroid, 
            spread=self.spread, startcolumn=self.startcolumn
                                    )

    def backforth(self):
        self.backforthframe = tk.LabelFrame(self.guiTitle, text="Stage Controller")
        self.backforthframe.grid(column=1, row=3)
        self.onwardsframe = tk.LabelFrame(self.backforthframe, text="Continue to Fitting")
        self.onwardsframe.grid(column=1, row=1)
        self.onwardsbutton = tk.Button(
                                        self.onwardsframe, text="Continue",
                                        command=lambda: self.onwards()
                                       )
        self.onwardsbutton.pack()
        self.reselectframe = tk.LabelFrame(self.backforthframe, text="Back to Data Selection")
        self.reselectframe.grid(column=1, row=2)
        self.reselectbutton = tk.Button(self.reselectframe,text="Data Selection", 
                                        command=lambda: self.controller.show_frame(
                                        cont=File_Selector,
                                        signalstart=self.signalstart,
                                        signalend=self.signalend,
                                        xmin=self.xmin,
                                        xmax = self.xmax)
                                        )
        self.reselectbutton.pack()

    def update_indecies(self):
        try:
            self.start_index = self.df.index[self.df[self.xname.get()] == \
            v.nearest(float(self.signalstart.get()), self.df[self.xname.get()])][0]-self.df.index[0]
            self.end_index = self.df.index[self.df[self.xname.get()] == \
            v.nearest(float(self.signalend.get()), self.df[self.xname.get()])][0]-self.df.index[0]
        except IndexError:
            print("Some index error was raised at the index finding for the pandas dataframe"
                  "when you entered the signal start and end information")
            print("Could be due to malformed signal range. Please recheck your inputs.")
        except:
            print("Error in index finding. Signal highlighting failed - Ignore on first appearance")

    def trim_data(self):
        """                     self.xmin.set("-∞")
                                self.xmax.set("∞")
            What needs to be found
        

        """

        inf = "∞"
        if self.xmin.get() == '-'+inf:
            if self.xmax.get() == inf:
                print("No data was trimmed.")         
        else:
            try:
                self.df = self.df[self.df[self.xname.get()] <= float(self.xmax.get())] 
                # Just lop-off anything > xmax
            except:
                print("Exception thrown in xmax-lopping. Check the xmax entry, ensure int or float type")
            try:
                self.df = self.df[self.df[self.xname.get()] >= float(self.xmin.get())]
            except:
                print("Exception thrown in xmin-lopping of dataframe. Check the xmin entry,"
                      "ensure int or float type")

        if self.signalstart.get() == '':
            if self.signalend.get() == '':
                print("No signal was selected")
                self.start_index = 0
                self.end_index = len(self.df)
                return False
        else:
            self.update_indecies()

    def populatetoggleables(self):
        """
        Populates the self.toggleables tk.LabelFrame created in the __init__

        This class is a bit cyclical, and can't follow the traditional __init__
            philosophy, and must have its controller invoke certain methods
            to get attributes that would regularly be passed through the initalization
            stage of the class, but with tkinter's framework, that proves to be
            difficult to overcome.
        """
        # Handles the X/Y axis selector & label
        columns = self.df.columns.to_list()
        self.xaxpulldownframe = tk.LabelFrame(self.toggleables, text="X-Axis Column")
        self.xaxpulldownframe.grid(column=1, row=1)
        self.yaxpulldownframe = tk.LabelFrame(self.toggleables, text="Y-Axis Column")
        self.yaxpulldownframe.grid(column=1, row=2)
        self.xaxlabelframe = tk.LabelFrame(self.toggleables, text="X-Axis Label")
        self.xaxlabelframe.grid(column=3, row=1)
        self.yaxlabelframe = tk.LabelFrame(self.toggleables, text="Y-Axis Label")
        self.yaxlabelframe.grid(column=3, row=2)


        self.xaxlabelentry = tk.Entry(self.xaxlabelframe, textvariable=self.xaxlabel)
        self.yaxlabelentry = tk.Entry(self.yaxlabelframe, textvariable=self.yaxlabel)
        self.xaxlabelentry.pack()
        self.yaxlabelentry.pack()


        self.xaxpulldown = tk.OptionMenu(self.xaxpulldownframe,self.xname, *columns)
        
        self.yaxpulldown = tk.OptionMenu(self.yaxpulldownframe, self.yname, *columns)
        self.xaxpulldown.pack()
        self.yaxpulldown.pack()

        # Handles the binnings
        binnings = [str(i) for i in range(1, 200)]
        self.binningframe = tk.LabelFrame(self.toggleables, text="Bin Width (Enter an Integer)")
        self.binningframe.grid(column=2, row=3)
            
        self.binningpulldown = tk.Entry(self.binningframe, textvariable=self.binningvalue)
        self.binningpulldown.pack()

        # Handles the xminimum and xmaximum in the dataframe
        self.xminframe = tk.LabelFrame(self.toggleables, text="Minimum X")
        self.xmaxframe = tk.LabelFrame(self.toggleables, text="Maximum X")
        self.xminframe.grid(column=1, row=4)
        self.xmaxframe.grid(column=3, row=4)

        

        self.xminentry = tk.Entry(self.xminframe, textvariable=self.xmin)
        self.xmaxentry = tk.Entry(self.xmaxframe, textvariable=self.xmax)
        self.xminentry.pack()
        self.xmaxentry.pack()

        # Chance for the user to highlight the signal data
        self.signalstartframe = tk.LabelFrame(self.toggleables, text="Signal Start (X-axis Value)")
        self.signalstopframe = tk.LabelFrame(self.toggleables, text="Signal Stop (X-axis Value)")
        self.signalstartframe.grid(column=1,row=5)
        self.signalstopframe.grid(column=3,row=5)

        self.signalstartentry = tk.Entry(self.signalstartframe, textvariable=self.signalstart)
        self.signalendentry = tk.Entry(self.signalstopframe, textvariable=self.signalend)
        self.signalstartentry.pack()
        self.signalendentry.pack()



        # Lastly, the Update-Button
        self.updateframe = tk.LabelFrame(self.toggleables, text="Update Data")
        self.updateframe.grid(column=2, row=6)
        self.updatebutton = tk.Button(self.updateframe, text ="Apply Settings", 
                                      command = self.update_everything_ut)
        self.updatebutton.pack()

    def update_everything_ut(self):
        # A the User triggered version of updating everything
        self.update_everything(usertriggered=True)

    def fetch_kwargs(self, **kwargs):
        #kwargs
        self.startcolumn = kwargs.pop('startcolumn', None)
        self.vnavme = kwargs.pop('vnavme', None)
        self.rawsigDataFile = kwargs.pop('rawsigdatapath', None)
        self.bldataFile = kwargs.pop('bldatapath', None)
        self.blskiplines = kwargs.pop('blskiplines', None)
        self.rawsigskiplines = kwargs.pop('rawsigskiplines',None)
        impression = kwargs.pop('impression', False)
        self.rawsigtime = kwargs.pop('rawsigtime', None)
        self.I = kwargs.pop("mag_current", None)
        self.T = kwargs.pop("temperature", None)
        self.binning = 1
        self.vapor_pressure_t = kwargs.pop("vapor_pressure_t",None)
        self.cccst3_t = kwargs.pop("cccst3_t", None)
        #print(impression)
        self.update_dataframe(impression=impression)
        self.start_index = 0
        self.end_index = len(self.df)
        self.xname = tk.StringVar()
        self.yname = tk.StringVar()
        self.binningvalue = tk.StringVar()
        self.binningvalue.set('1')
        self.centroid = kwargs.pop('centroid', None)
        self.spread = kwargs.pop('spread', None) 
        
        self.xaxlabel = tk.StringVar()
        self.yaxlabel = tk.StringVar()
        self.xaxlabel.set("Frequency (MHZ)")

        if self.vnavme == "VNA":
            self.yaxlabel.set("Re(Z) Impedence [Ω]")
        elif self.vnavme == "VME":
            self.yaxlabel.set("Potential [V]")
        
        self.signalstart = kwargs.pop("signalstart", tk.StringVar())
        self.signalend = kwargs.pop("signalend", tk.StringVar())

        self.xmin = kwargs.pop('xmin', tk.StringVar())
        self.xmax = kwargs.pop('xmax', tk.StringVar())

        cols = self.df.columns.to_list()
        self.xname.set(cols[0])
        self.yname.set(cols[1])
        self.update_everything()

    def update_dataframe(self, impression=False):
        try:
            self.df = v.gui_file_fetcher(
                                        self.rawsigDataFile, self.bldataFile, 
                                        self.vnavme, impression=impression, 
                                        
                                        blskiplines=self.blskiplines, rawsigskiplines=self.rawsigskiplines, 
                                        binning=self.binning
                                     )
        except ValueError:
            pass

    def update_graph(self):
        self.graph=tk.LabelFrame(self, text="Graph")
        self.graph.grid(column=2, row=0)
        self.update_indecies()
        #print("Start index:", self.start_index, "\nEnd Index:", self.end_index)
        #print("Redsig Status:", False if [self.start_index, self.end_index] == [0, len(self.df)] else True)
        quirky = v.ggf(
                self.df, self.start_index, self.end_index, gui=True, 
                binning=int(self.binningvalue.get()),
                plttitle="Converted Data", x=self.xname.get(), y=self.yname.get(),
                xlabel=self.xaxlabel.get(), ylabel=self.yaxlabel.get(), 
                redsig=False if [self.start_index, self.end_index] == [0, len(self.df)] else True,
                clearfigs=True
                            )

        self.figure = quirky['fig']
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        
    def data_displayer(self):
        self.ConvertedDf = tk.LabelFrame(self.guiTitle, text="Data")
        self.ConvertedDf.grid(column = 1, row = 1, padx=15)
        self.dftxt = scrolledtext.ScrolledText(self.ConvertedDf, width=95)
        #txt['font'] = ('Noto Sans Gothic', '12')
        self.dftxt.pack(fill='both')
        #print("Tab Delimited\n", self.df.to_string().split('\n')[0])
        for index, line in enumerate(self.df.to_string().split('\n')):
            self.dftxt.insert(tk.END, line+'\n')


class Fitting_Page(tk.Frame):
    def __init__(self,parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.automatefits = []
        
        self.fitpageframe = tk.LabelFrame(self, text="Fitting Page")
        self.fitpageframe.grid(column=1, row=1)
        self.toggleables = tk.LabelFrame(self.fitpageframe, text="Fit Settings")
        self.toggleables.grid(column=1, row=1)

    def update_indicies(self):
        try:
            self.start_index = self.df.index[self.df[self.xname.get()] == \
            v.nearest(float(self.signalstart.get()),
            self.df[self.xname.get()])][0]-\
            self.df.index[0]
            self.end_index = self.df.index[self.df[self.xname.get()] == \
            v.nearest(float(self.signalend.get()),
              self.df[self.xname.get()])][0]-\
              self.df.index[0]
        except IndexError:
            print("Some index error was raised at the index finding for" 
                  "the pandas dataframe when you entered the "
                  "signal start and end information")
            print("Could be due to malformed signal range. Please recheck your inputs.")
        except:
            print("Error in index finding. Signal highlighting failed.")

    def fetch_kwargs(self, **kwargs):
        self.startcolumn = kwargs.pop('startcolumn', None)

        self.vnavme = kwargs.pop('vnavme',None)
        self.rawsigdatapath = kwargs.pop('rawsigdatapath',None)
        self.bldatapath = kwargs.pop('bldatapath', None)
        self.blskiplines = kwargs.pop('blskiplines', None)
        self.rawsigskiplines = kwargs.pop('rawsigskiplines', None)
        self.vapor_pressure_t = kwargs.pop("vapor_pressure_t",None)
        self.cccst3_t = kwargs.pop("cccst3_t", None)
        self.isautomated = kwargs.pop('isautomated',False)
        self.centroid = kwargs.pop('centroid', None)
        self.spread = kwargs.pop('spread', None) 


       
        self.df=kwargs.pop('df', None)
        self.start_index=kwargs.pop('start_index', None)
        self.end_index=kwargs.pop('end_index', None)
        self.xname = kwargs.pop('xname',None)
        self.yname = kwargs.pop('yname',None)
        self.binningvalue=kwargs.pop('binning',None)
        self.xaxlabel = kwargs.pop('xlabel', None)
        self.yaxlabel = kwargs.pop('ylabel', None)
        self.xmin=kwargs.pop('xmin',None)
        self.xmax=kwargs.pop('xmax',None)
        self.signalstart=kwargs.pop('signalstart',None)
        self.signalend=kwargs.pop('signalend',None)
        self.rawsigtime = kwargs.pop('rawsigtime',None)
        self.T = kwargs.pop('temperature', None)
        self.I = kwargs.pop("mag_current", None)

        self.lorentzian_x0 = tk.StringVar(value="0")
        self.lorentzian_w = tk.StringVar(value="0")
        self.lorentzian_A = tk.StringVar(value="0")
        self.lorentzian_B = tk.StringVar(value="0")


        self.mutouse = tk.StringVar(value='proton')
        self.material_type = tk.StringVar()
        self.checkboxstatus = tk.StringVar(value="0")
        self.material_type.set("TEMPO Doped Araldite")
        self.plottitle=tk.StringVar()
        self.plottitle.set("".join(list(self.rawsigdatapath.split('/')[-1])[:-4]))
        self.integrate = tk.StringVar()
        self.integrate.set('0')
        self.fitlorentzian = tk.StringVar()
        self.fitlorentzian.set('0')
        self.type_of_fit = tk.StringVar()
        self.type_of_fit.set("sin")
        self.btext = tk.StringVar()
        self.ttext = tk.StringVar()
        self.ttext.set(str(self.T))
        try:
            self.btext.set(str(round(self.I/9.7332,4)))
        except TypeError:
            print("WARNING: No Magnet current exists in", self.rawsigdatapath.split('/')[-1], 
                "TE-Value will NOT be calculated")
            self.btext.set(self.I)

        self.ptext = tk.StringVar()
        self.ptext.set(datetime.datetime.now().strftime("%Y_%m_%d_%H:%M:%S")+"_Visualizer_Instance")
        self.xminentry = tk.StringVar()
        self.xmaxentry = tk.StringVar()
        self.xminentry.set('')
        self.xmaxentry.set('')

        self.init_one()

    def update_graph(self, graph=None, repeat=False, p_title=None, automated=False):
        self.update_indicies()
        if graph is None:
            plt.clf()
            plt.close('all')
            try:
                b = float(self.btext.get())
                T = float(self.ttext.get())
            except ValueError:
                b = self.btext.get()
                T = self.ttext.get()
            try:
                xmin = float(self.xminentry.get())
                xmax = float(self.xmaxentry.get())
            except ValueError:
                xmin = self.xminentry.get()
                xmax = self.xmaxentry.get()
            try:
                fls, fle = float(self.signalstart.get()), float(self.signalend.get())
            except ValueError:
                fls, fle =0,0
                pass  # It doesn't even matter if this fails because of fltest.
            # Get that plot title during automation
            plot_title = p_title if p_title is not None else self.plottitle.get()
            fltest = True if self.fitlorentzian.get() == '1' else False
            ub = 9.274009994*10**(-24) # Bohr Magnetron 
            up = 1.521*10**(-3)*ub     # Proton Magnetic Moment
            ud = 0.307012207*up        # doi.org/10.1016/j.physleta.2003.09.030
            
            temuval = up if self.mutouse.get() == "proton" else ud
            #print(self.mutouse.get())
            quirky = v.ggf(
                                self.df, self.start_index, self.end_index, gui=True, 
                                plttitle=plot_title, x=self.xname.get(), y=self.yname.get(),
                                xlabel=self.xaxlabel.get(), ylabel=self.yaxlabel.get(), 
                                redsig=True if [self.start_index, self.end_index] != [0, len(self.df)]\
                                else False,
                                binning=int(self.binningvalue.get()), 
                                integrate=True if self.integrate.get() == '1' else False,
                                fitlorentzian=fltest, fitlorentziancenter_bounds=[fls,fle],
                                b=b, T=T,   # Its okay if type isnt right, because below line ensures type
                                thermal_equalibrium_value=True if type(b) == float and type (T) == float\
                                 else False,
                                xmin=xmin if type(xmin) == float else None, xmax=xmax if type(xmax) ==\
                                 float else None,filename=self.rawsigdatapath,
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
        if not automated:
            #print("hitteth")
            self.graph=tk.LabelFrame(self, text="Graph")
            self.graph.grid(column=2, row=1)
            self.canvas = FigureCanvasTkAgg(self.figure, master=self.graph)
            
            self.canvas.draw()
            self.canvas.get_tk_widget().pack()
        else:
            return quirky

    def updatexy_selector(self):
        columns = self.df.columns.to_list()
        self.xaxpulldownframe = tk.LabelFrame(self.plotsettingsframe, text="X-Axis Column")
        self.xaxpulldownframe.grid(column=1, row=2)
        self.yaxpulldownframe = tk.LabelFrame(self.plotsettingsframe, text="Y-Axis Column")
        self.yaxpulldownframe.grid(column=1, row=3)
        self.xaxlabelframe = tk.LabelFrame(self.plotsettingsframe, text="X-Axis Label")
        self.xaxlabelframe.grid(column=3, row=2)
        self.yaxlabelframe = tk.LabelFrame(self.plotsettingsframe, text="Y-Axis Label")
        self.yaxlabelframe.grid(column=3, row=3)

        
        xaxlabelentry = tk.Entry(self.xaxlabelframe, textvariable=self.xaxlabel)
        yaxlabelentry = tk.Entry(self.yaxlabelframe, textvariable=self.yaxlabel)
        xaxlabelentry.pack()
        yaxlabelentry.pack()


        self.xaxpulldown = tk.OptionMenu(self.xaxpulldownframe, self.xname, *columns)
        
        self.yaxpulldown = tk.OptionMenu(self.yaxpulldownframe, self.yname, *columns)
        self.xaxpulldown.pack()
        self.yaxpulldown.pack()

    def show_lorentzian_toggleables(self):
        if not self.enabled:
            self.lorentzian_x0_entry = tk.Entry(self.lorentzian_coersion_frame, textvariable=self.lorentzian_x0).grid(column=3, row=1)
            self.lorentzian_w_entry = tk.Entry(self.lorentzian_coersion_frame, textvariable=self.lorentzian_w).grid(column=3, row=2)
            self.lorentzian_B_entry = tk.Entry(self.lorentzian_coersion_frame, textvariable=self.lorentzian_B).grid(column=3, row=3)
            self.lorentzian_A_entry = tk.Entry(self.lorentzian_coersion_frame, textvariable=self.lorentzian_A).grid(column=3, row=4)
            self.lorentzian_x0_label = tk.Label(self.lorentzian_coersion_frame, text="Centroid (x0) Guess:").grid(column=1, row=1)
            self.lorentzian_w_label = tk.Label(self.lorentzian_coersion_frame, text="FWHM (w) Guess:").grid(column=1, row=2)
            self.lorentzian_B_label = tk.Label(self.lorentzian_coersion_frame, text="Direction (-1/1) (B) Guess:").grid(column=1, row=3)
            self.lorentzian_A_label = tk.Label(self.lorentzian_coersion_frame, text="Vertical Shift (A) Guess:").grid(column=1, row=4)


            self.enabled = True

    def populatetoggleables(self):
        """
        Populates the self.toggleables tk.LabelFrame created in the __init__

        This class is a bit cyclical, and can't follow the traditional __init__
            philosophy, and must have its controller invoke certain methods
            to get attributes that would regularly be passed through the initalization
            stage of the class, but with tkinter's framework, that proves to be
            difficult to overcome.
        """
        # Handles the X/Y axis selector & label
        

        self.fitnameframe = tk.LabelFrame(self.toggleables, text="Fit Name")
        self.fitnameframe.grid(column=1,row=1)
        self.fitname = tk.StringVar()
        self.fitname.set("Fit 1")
        self.fitnameentry = tk.Entry(self.fitnameframe, textvariable=self.fitname)
        self.fitnameentry.pack()

        self.plotsettingsframe = tk.LabelFrame(self.toggleables, text="Plot Specifics")
        self.plotsettingsframe.grid(column=1, row=2)

        # Chance for the user to highlight the signal data
        self.signalstartframe = tk.LabelFrame(self.plotsettingsframe, text="Signal Start (X-axis Value)")
        self.signalstopframe = tk.LabelFrame(self.plotsettingsframe, text="Signal Stop (X-axis Value)")
        self.signalstartframe.grid(column=1,row=4)
        self.signalstopframe.grid(column=3,row=4)

        self.signalstartentry = tk.Entry(self.signalstartframe, textvariable=self.signalstart)
        self.signalendentry = tk.Entry(self.signalstopframe, textvariable=self.signalend)
        self.signalstartentry.pack()
        self.signalendentry.pack()

        # Chance for the user to set the graph width for the dataset.
        self.graphxstartframe = tk.LabelFrame(self.plotsettingsframe, text="Set Graph Xmin")
        self.graphxstartframe.grid(row=5, column=1)
        self.graphxendframe = tk.LabelFrame(self.plotsettingsframe, text="Set Graph Xmax")
        self.graphxendframe.grid(row=5,column=3)
        self.graphxsentry = tk.Entry(self.graphxstartframe, textvariable=self.xminentry)
        self.graphxsentry.pack()
        self.graphxeentry = tk.Entry(self.graphxendframe, textvariable=self.xmaxentry)
        self.graphxeentry.pack()

        self.updatexy_selector()


        # Radio button for fit type
        #tk.Radiobutton(self.Switches, text="VNA", variable=self.vnaVmeType, value="VNA").pack()
        self.fitradioframe = tk.LabelFrame(self.toggleables, text="Type of Fit")
        self.fitradioframe.grid(column=1,row=5)
        tk.Radiobutton(self.fitradioframe, text="Sin", variable=self.type_of_fit, value='sin').pack()
        tk.Radiobutton(self.fitradioframe, text="Third Order Polynomial", 
            variable=self.type_of_fit, value='third_order').pack()
        tk.Radiobutton(self.fitradioframe, text="Fourth Order Polynomial", 
            variable=self.type_of_fit, value='fourth_order').pack()
        tk.Radiobutton(self.fitradioframe, text="Fifth Order Polynomial", 
            variable=self.type_of_fit, value='fifth_order').pack()
        tk.Radiobutton(self.fitradioframe, text="Sixth Order Polynomial", 
            variable=self.type_of_fit, value='sixth_order').pack()

        self.enabled = False # I want to see the command function on two lines below executed once, and no more. 
                             # This is a flag that I use to toggle when i've executed that already.
        self.lorentzian_coersion_frame = tk.LabelFrame(self.toggleables, text="Raw Signal Fitting ONLY")
        self.lorentzian_coersion_frame.grid(column=1, row=6)
        self.show_lorentzian_toggleables()
        tk.Radiobutton(self.lorentzian_coersion_frame, text="Lorentzian", variable=self.type_of_fit,value='lorentzian_ellie').grid(column=2, row=0)
        tk.Radiobutton(self.lorentzian_coersion_frame, text="Signal Fit", variable=self.type_of_fit, value="absorbtion_dispersion_ellie").grid(column=2, row=5)

        
        # Plottitle
        self.titleframe = tk.LabelFrame(self.toggleables, text="Plot Title")
        self.titleframe.grid(column=1,row=7)
        self.titlentry = tk.Entry(self.titleframe, textvariable=self.plottitle)
        self.titlentry.pack()

        # Integrate and Fit lorentzian things
        self.auxtoggleframe = tk.LabelFrame(self.toggleables, text="Additional Parameters")
        self.auxtoggleframe.grid(column=1,row=8)
        self.auxTEFrame = tk.Frame(self.auxtoggleframe)
        self.auxTEFrame.grid(column=0, row=1)
        self.mutoggleframe=tk.LabelFrame(self.auxtoggleframe, text="Magnetic Moment for TE")
        self.mutoggleframe.grid(column=1,row=1)
        tk.Radiobutton(self.mutoggleframe, text="Proton Magnetic Moment", variable=self.mutouse, value='proton').grid(column=1, row=1)
        tk.Radiobutton(self.mutoggleframe, text="Deuteron Magnetic Moment", variable=self.mutouse, value='deuteron').grid(column=1,row=2)

        self.integratecheck = tk.Checkbutton(self.auxTEFrame, text='Integrate Data Points', 
            variable=self.integrate, onvalue='1', offvalue='0')
        self.lorentziancheck = tk.Checkbutton(self.auxTEFrame, text='Fit Lorentzian to Data', 
            variable=self.fitlorentzian, onvalue='1', offvalue='0')
        self.integratecheck.grid(row=1)
        self.lorentziancheck.grid(row=2)
        # B and T in the fit and lorentzian things
        self.teframe = tk.LabelFrame(self.auxTEFrame, text="Thermal Equalibrium Values")
        self.teframe.grid(row=3)
        self.tlabel = tk.Label(self.teframe, text='T')
        self.tlabel.grid(row=1, column=1)
        self.blabel = tk.Label(self.teframe, text="B")
        self.blabel.grid(row=2,column=1)
        self.tentry = tk.Entry(self.teframe, textvariable=self.ttext)
        self.tentry.grid(row=1,column=2)
        self.bentry = tk.Entry(self.teframe, textvariable=self.btext)
        self.bentry.grid(row=2,column=2)
        
        self.mtypefram = tk.LabelFrame(self.auxTEFrame, text="Material Type:")
        self.mtypefram.grid(row=4)
        self.mtypeentry = tk.Entry(self.mtypefram, textvariable=self.material_type)
        self.mtypeentry.grid(row=3,column=2)

        self.major_buttons_frame = tk.LabelFrame(self.toggleables)
        self.major_buttons_frame.grid(column=1,row=9)
        

        # Add Fit to df Button
        self.tryfitframe = tk.LabelFrame(self.major_buttons_frame, text="Create Fit Subtraction")
        self.tryfitframe.grid(column=1, row=1)
        self.tryfitbutton = tk.Button(self.tryfitframe, text="Fit the Data", command= self.addfit)
        self.tryfitbutton.pack()


        # The Update-Button
        self.updateframe = tk.LabelFrame(self.major_buttons_frame, text="Update Graph")
        self.updateframe.grid(column=2, row=1)
        self.updatebutton = tk.Button(self.updateframe, text ="Update Graph", command = self.update_graph)
        self.updatebutton.pack()

        # Go back to the data trimming stage
        self.reverse_reverse()
        # Start over
        self.populatesaving()

        # Automate feature:

        """
        self.auxtoggleframe, text='Integrate Data Points', variable=self.integrate, onvalue='1', offvalue='0'
        """
        self.automateframe = tk.LabelFrame(self.fitpageframe, text="Automation")
        self.automatecheckbox=tk.Label(self.automateframe, text="Apply Current Extraction Techniques to Entire Directory")
        self.automateframe.grid(row=3,column=1)
        self.automatecheckbox.pack()
        self.automatebutton = tk.Button(self.automateframe, text="Start", command=self.repeat_ad_nauseum)
        self.automatebutton.pack()
        if self.isautomated == True:
            self.isautomated_button=tk.Button(self.automateframe, text="Continue to Next Issue")
            self.isautomated_button.pack()
        #self.automatechekboxflavortext=tk.Label("Automation")
        # 

    def populatesaving(self):
        self.savingframe = tk.LabelFrame(self.fitpageframe, text="Saving Options")
        self.savingframe.grid(column=1,row=2)

        self.savebutton = tk.Button(self.savingframe, text="Save Graph", command=self.savefig)
        self.savebutton.grid(column=1, row=2)

        self.persistenceframe = tk.LabelFrame(self.savingframe, text="Write to File")
        self.persistenceframe.grid(column=1,row=3)
        self.persistencebutton = tk.Button(self.persistenceframe, text="Save Settings and Data", 
            command=self.addentry)
        self.persistencebutton.grid(column=1, row=1)
        self.plabel = tk.Label(self.persistenceframe, text='Instance Name')
        self.plabel.grid(column=0, row=3)
        self.pentry = tk.Entry(self.persistenceframe, textvariable=self.ptext)
        self.pentry.grid(column=2,row=3)

    def addentry(self, k=[], h=None):
        # Arguments to be passed in the same order
        # as the headers list in vna_visualizer.py
        
        headers = ["name", "material", "time", "dtype", "blpath", "rawpath", "xmin",
                       "xmax", "sigstart", "sigfinish", "blskiplines",
                       'rawsigskiplines', "B", "T", "CCCCS.T3 (K)", "Vapor Pressure (K)", 
                       "TEvalue", "data_area", "ltzian_area",
                       "data_cal_constant","ltzian_cal_constant", 'a', 'w', 'x0', 
                       "lorentzian chisquared (distribution)", "σ (Noise)", "σ (Error Bar)", 
                       "lorentzian relative-chisquared (error)",
                       "Sweep Centroid", "Sweep Width", 'e_f0', 'e_w', 'e_kmax', 'e_theta']
        c = [self.pentry.get(),  self.material_type.get(), self.rawsigtime, self.vnavme, 
             self.bldatapath, self.rawsigdatapath, self.xminentry.get(), self.xmaxentry.get(),
             self.signalstart.get(),self.signalend.get(), self.blskiplines, 
             self.rawsigskiplines, self.btext.get(),
             self.ttext.get(), self.cccst3_t, self.vapor_pressure_t, self.tevalue, 
             self.dataarea, self.ltzian_integration, self.data_cal_constant,
             self.fit_cal_constant, self.ltzian_a, self.ltzian_w, self.ltzian_x0, 
             self.tlorentzian_chisquared, self.sigma_error, self.sigmaforchisquared, 
             self.klorentzian_chisquared, self.centroid, self.spread]
        
        if len(k) != 0:
            with open(k[0]+'.csv', 'w') as f:
                self.df.to_csv(f)
            v.add_entry(*k, headers=headers if h is not None else h)
        else:
            with open(self.pentry.get()+'.csv', 'w') as f:
                self.df.to_csv(f)
            v.add_entry(*c, headers=headers if h is not None else h)
        
    def data_displayer(self):
        self.ConvertedDf = tk.LabelFrame(self, text="Data")
        self.ConvertedDf.grid(column = 1, row = 1, padx = 35, pady = 50)
        self.dftxt = scrolledtext.ScrolledText(self.ConvertedDf)
        #txt['font'] = ('Noto Sans Gothic', '12')
        self.dftxt.pack(expand=True, fill='both')
        #print("Tab Delimited\n", self.df.to_string().split('\n')[0])
        for index, line in enumerate(self.df.to_string().split('\n')):
            self.dftxt.insert(tk.END, line+'\n')

    def addfit(self):
        """
        TODO: Add a method that checks the types of fits available in VNA_Visualizer, that is able to fit all of the
        data between those indexes, and return a chi-squared/dof statistic that is used in auto-selecting the fit
        routine for the update-phase.
        """
        plt.clf()
        plt.close('all')
        test = len(self.automatefits)-1
        if test >= 0:
            if self.automatefits[test][1] == self.fitname.get():
                print("\nWARNING: Previous fit named:", self.automatefits[test][1], 
                    "was overridden.\nChange fit name if you are doing multiple subtraction\n")
                self.automatefits[test] = [self.type_of_fit.get(), self.fitname.get()]
            else:
                self.automatefits.append([self.type_of_fit.get(), self.fitname.get()])
        else:    
            self.automatefits.append([self.type_of_fit.get(), self.fitname.get()])
        self.update_indicies()
        self.binning = int(self.binningvalue.get())
        try:
            p0 = [float(self.lorentzian_x0), float(self.lorentzian_w), float(self.lorentzian_A), float(self.lorentzian_B)] if self.fitname.get() == "lorentzian_ellie" else None
            bounds = [[float(self.lorentzian_x0)-.1, -numpy.inf, float(self.lorentzian_A)-.05, -numpy.inf],[float(self.lorentzian_x0)+.1, numpy.inf, float(self.lorentzian_A)+.05, numpy.inf]] if self.fitname.get() == "lorentzian_ellie" else [[-numpy.inf, -numpy.inf, -numpy.inf, -numpy.inf ],[numpy.inf,numpy.inf,numpy.inf,numpy.inf]]
        except ValueError:
            print("***WARNING: Error in type conversion for RAWSIGNAL fit coersion. p0 WILL NOT be passed.")
            p0 = None
        self.df, fig, chsq, rawsigfit = v.gff(
                            self.df, self.start_index, self.end_index, fit_sans_signal=True, 
                            function=[self.type_of_fit.get()], fitname=self.fitname.get(), 
                            binning=self.binning, gui=True, redsig=True, x=self.xname.get(),
                            y=self.yname.get(), plottitle=self.plottitle, p0=p0, bounds = bounds
                        )

        #'e_f0', 'e_w', 'e_kmax', 'e_theta'
        self.e_f0, self.e_w, \
        self.e_kmax, self.e_theta = rawsigfit.pop('e_f0', None), \
            rawsigfit.pop("e_w", None), \
            rawsigfit.pop('e_kmax', None), \
            rawsigfit.pop("e_theta", None)

        print(" "*15, "CHI SQUARED VALUES FOR EACH FIT")
        print("#"*65)

        for key in chsq:
            val = chsq[key]
            print("{0:<1s}{1:^5s}{0:1s}{2:^31s}{0:1s}{3:^25s}{0:1s}".format("#","Fit", key, str(val)))
            #print("#Fit #\t", key, " #\t Chisquared:", val, " #")
        print("#" * 65)
        self.update_graph(graph=fig)
        self.updatexy_selector()

    def init_one(self, failed=False):
        self.binning = int(self.binningvalue.get())
        # The cooler version of this class' __init__ called after __init__
        #       This needs to be convoluded due to tkinter's oblique-ness
        #       that makes it really uncomfortable to do class-inheritance.
        self.populatetoggleables()
        self.reverse_reverse()
        self.update_graph()

    def savefig(self, automated=False, p_title=None):
        self.update_graph(automated=automated, p_title=p_title)
        if automated:
            self.figure.savefig(self.pentry.get()+" S"+str(self.item))
        else:
            self.figure.savefig(self.pentry.get())

    def reverse_reverse(self):
        # Cha-cha real smooth back to the data trimming stage.
        self.reverseframe = tk.LabelFrame(self.major_buttons_frame, text="Back to Data Trimming")
        self.reverseframe.grid(column=1, row=2)

        self.gotransition = tk.Button(
                                        self.reverseframe, text = "Data Trimming",
                                        command = lambda: self.controller.show_frame(cont=Data_Selector, 
                                        vnavme=self.vnavme, 
                                        rawsigdatapath=self.rawsigdatapath, 
                                        bldatapath=self.bldatapath,
                                        rawsigskiplines=self.rawsigskiplines,
                                        blskiplines=self.blskiplines,
                                        impression=False, 
                                        rawsigtime=self.rawsigtime, 
                                        temperature=self.T,
                                        mag_current=self.I,
                                        vapor_pressure_t=self.vapor_pressure_t,
                                        cccst3_t=self.cccst3_t,
                                        signalstart=self.signalstart,
                                        signalend=self.signalend,
                                        xmin=self.xmin,
                                        xmax = self.xmax,
                                        startcolumn=self.startcolumn
                                        )
                                      )
        self.gotransition.pack()

        self.back_to_beginning = tk.LabelFrame(self.major_buttons_frame, text="Back to Beginning")
        self.back_to_beginning.grid(column=2,row=2)
        self.bbl = tk.Button(self.back_to_beginning, text="Start Over", 
            command = lambda: self.controller.show_frame(cont=File_Selector,
                                        signalstart=self.signalstart,
                                        signalend=self.signalend,
                                        xmin=self.xmin,
                                        xmax = self.xmax
                                        )
                                      )
        self.bbl.pack()

    def update_te(self):
        # Get the info
        delimeter = '\t'
        _, _, self.rawsigtime, self.I, self.T,\
        self.cccst3_t, self.vapor_pressure_t, \
        self.rawsigskiplines, self.centroid, \
        self.spread = v.gui_rawsig_file_preview(self.rawsigdatapath, delimeter, self.vnavme) 
        #self.rawsigtime = self.TE_DATE
        #print(self.T)
        
    def update_indecies(self):
        try:
            self.start_index = self.df.index[self.df[self.xname.get()] == \
            v.nearest(float(self.signalstart.get()), self.df[self.xname.get()])][0]-self.df.index[0]
            self.end_index = self.df.index[self.df[self.xname.get()] == \
            v.nearest(float(self.signalend.get()), self.df[self.xname.get()])][0]-self.df.index[0]
        except IndexError:
            print("ERROR: index error at the index finding of the dataframe.  CHECK YOUR INPUTS.")
        except:
            print("IGNORE: Signal highlighting failed.")

    def trim_data(self):
        """                     
        self.xmin.set("-∞")
        self.xmax.set("∞")
        What needs to be found
        """

        inf = "∞"
        if self.xmin.get() == '-'+inf:
            if self.xmax.get() == inf:
                print("No data was trimmed.")         
        else:
            try:
                self.df = self.df[self.df[self.xname.get()] <= float(self.xmax.get())] # Just lop-off anything > xmax
            except:
                print("Exception thrown in xmax-lopping. Check the xmax entry, ensure int or float type")
            try:
                self.df = self.df[self.df[self.xname.get()] >= float(self.xmin.get())]
            except:
                print("Exception thrown in xmin-lopping of dataframe. Check the"
                    " xmin entry, ensure int or float type")

        if self.signalstart.get() == '':
            if self.signalend.get() == '':
                print("No signal was selected")
                self.start_index = 0
                self.end_index = len(self.df)
                return False
        else:
            self.update_indecies()

    def automator(self, file, originalplottitle, originalentryname, extension, tedirectory, graphs, graphdata, home, failed=False, failedno=0):
        # based on VME/VNA file selection what y-axis are we going to apply the user's settings to first on a blind loop
        npriev = self.startcolumn
        if npriev is None:
            print("**WARNING: The Y-axis that was selected after file selection"
                " no longer exists, or is invalid. Defaulting to file-type default "
                "(Potential (V) if .ta1; Z_re if .s1p)")
            npriev = "Potential (V)" if self.vnavme == "VME" else "Z_re"


        # update attribute
        self.rawsigdatapath = file
        # Run method to update other attributes
        self.update_te()
        # Redo binning if necessary?
        self.binning = int(self.binningvalue.get())
        # Update critical attributes used to fit the function
        # (starting/ending indexes)
        self.update_indicies()
        # Fetch the fresh dataframe
        self.df = v.gui_file_fetcher(
                                file, self.bldatapath, self.vnavme, impression=False, 
                                blskiplines=self.blskiplines, rawsigskiplines=self.rawsigskiplines, 
                                binning=self.binning
                             )
        # Trim down the dataframe
        self.trim_data()
        # Update critical attributes used to fit the function
        # (starting/ending indexes)
        self.update_indicies()
        # If the user fit more than one function to the dataframe
        # this is how it works
        if not failed:
            for index, tupp in enumerate(self.automatefits):
                """
                if index == 0, npriev is predefined to be the default y-axis to try and fit with gff
                (aka General Fitting Function)

                The dataframe is then updated by gff

                The previous function name (defined in self.automatefites which saves the user's fit 
                    name and function each time they fit a column in the df)
                    will then become the second, third .... nth column of data to refit, then subtract.

                """
                f = tupp[0] # Function name (sin, third-order, fourth-order ... , exponential) 
                            # Litterally eval()'ed, dont tell opsec, or Professor Arvind Narayan that I did this
                n = tupp[1] # The name that the user gave their template fit before clicking the "fit data" button
                            # Used to itteratively map / shift fitting, and naming of fits, subtractions, etc.
                self.df, fig, chsq, rawsigfit = v.gff(
                                    self.df, self.start_index, self.end_index, fit_sans_signal=True, 
                                    function=[f], fitname=n, 
                                    binning=self.binning, gui=True, redsig=True, x=self.xname.get(),
                                    y=npriev, plottitle=originalplottitle+" S"+str(self.item)
                                )
                
                # Save this, because if we loop again, we're gonna need to fit subtract fit-subtracted data, 
                #   assuming thats what the user did; I made it so; actually otherwise the user overwrites
                #   their last fit.
                npriev = tupp[1]
            # Save the figure
            os.chdir(graphs)
            
            self.savefig(automated=True, p_title=originalplottitle+" S"+str(self.item)) # UNCOMMENT TO SAVE EVERYTHING.
            
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
                print("WARNING: TE value Failed, indicating that B, or T was not of proper type.")
                self.B = self.I
                self.tevalue = 0

            headers = ["name", "material", "time", "dtype", "blpath", "rawpath", "xmin",
                   "xmax", "sigstart", "sigfinish", "blskiplines",
                   'rawsigskiplines', "B", "T", "CCCCS.T3 (K)", "Vapor Pressure (K)", 
                   "TEvalue", "data_area", "ltzian_area",
                   "data_cal_constant","ltzian_cal_constant", 'a', 'w', 'x0', 
                   "lorentzian chisquared", "σ (Noise)","σ (Error Bar)", 
                   "lorentzian relative-chisquared (error)", "Sweep Centroid", 
                   "Sweep Width", 'e_f0', 'e_w', 'e_kmax', 'e_theta']
            # Write to the global_analysis file
            c = [originalplottitle + " S"+str(self.item),  self.material_type.get(), 
             self.rawsigtime, self.vnavme, self.bldatapath, self.rawsigdatapath, self.xminentry.get(), self.xmaxentry.get(),
             self.signalstart.get(),self.signalend.get(), self.blskiplines, 
             self.rawsigskiplines, str(self.B),
             str(self.T), self.cccst3_t, self.vapor_pressure_t, self.tevalue, 
             self.dataarea, self.ltzian_integration, self.data_cal_constant,
             self.fit_cal_constant, self.ltzian_a, self.ltzian_w, self.ltzian_x0,
             self.tlorentzian_chisquared, self.sigma_error, self.sigmaforchisquared, 
             self.klorentzian_chisquared, self.centroid, self.spread, self.e_f0, self.e_w, self.e_kmax, self.e_theta]
            os.chdir(graphdata)
            #print("Made it to line 1254")
            self.addentry(k=c, h =headers)
            # Say that we've done a thing
            os.chdir(home)
            self.item+=1
            # Free your mind (memory)
            self.figure.clf()
            plt.close(self.figure)
            #self.canvas.destroy()
            gc.collect()
        
        # Coffee time.
        elif failed:
            self.init_one()

    def repeat_ad_nauseum(self):
        """
            TODO: Ensure self.TE_VAL gets updated in each iteration of automator

        """
        home = os.getcwd()
        try:
            os.chdir("graphs") # semantic satiation
        except FileNotFoundError:
            os.mkdir("graphs") # semantic satiation
        os.chdir(home)
        try:
            os.chdir("graph_data") # semantic satiation
        except FileNotFoundError:
            os.mkdir("graph_data") # semantic satiation
        os.chdir(home)
        graphs = home+"/graphs/" # semantic satiation
        graphdata = home+"/graph_data/" # semantic satiation
        # too many occurances of 'graph' here
        
        
        
        tedirectory = "/".join(self.rawsigdatapath.split('/')[:-1])   
        # Assuming linux directory deliniation '/', Just remove the specific te file
        
        # Create a list of TE/Polarization files to apply signal "filtering"
        # "filtering" is the user's choices from the original file that they loaded into the program
        # automation only becomes available on the last page.

        tefiles = []
        extension = ".ta1" if self.vnavme == "VME" else ".s1p"
        
        # Create the TE/Enchanced files list
        for file in os.listdir(tedirectory):
            if file.endswith(extension):
                tefiles.append(tedirectory+'/'+file)
        #print(tefiles)
        #exit()

        # To be implemented later
        self.failedfiles = []  # TODO: pass quirky into this namespace, and pop a key "hassucceeded" 
                          # if True: do not append to this list
                          # else: append filename to this bad larry
                          # rewrite the loop, and cycle back through
                          # this list. It will involve proper invoking of fetch_kwargs()
                          # Which will be difficult to resolve logistically with self.item adding "S %ITEM"
                          # to the names of things.
        # Used to create unique instance names so pandas doesn't overwrite identical entries. (also human readability)
        self.item = 0
        originalentryname = self.pentry.get()
        # Do the same thing to the plot title
        originalplottitle = self.plottitle.get()
        todo = len(tefiles)
        timedeltas = []
        for file in tefiles:
            try:
                t1 = time.time()
                self.automator(file, originalplottitle, originalentryname, extension, tedirectory, graphs, graphdata, home)
                t2 = time.time()
                timedeltas.append(t2-t1)
                print(self.item, "of", todo, '['+str(round(self.item*100/todo,4))+'%]', "ETA: ", round((todo-self.item)*numpy.mean(timedeltas),1), 's')
            except KeyError:
                print("Key error detected. breaking with loop, and will cycle back later. Most likely a fitting error. Check warnings & Errors.")
                #self.failedfiles.append([file, self.item])
                break
        #"""self.isautomated = True  # Will reconfigure gui for issues
        for failed in self.failedfiles:
            print("Issue fitting", failed[0][:-1])
            self.automator(file[0], originalplottitle, originalentryname, extension, tedirectory, graphs, graphdata, home, failed=True, failedno=failed[1])
            print("User has corrected issue.")
        for file in self.failedfiles:
            self.userinput(file)



root = NMR_Visualizer()
root.mainloop()
