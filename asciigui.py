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
import daq_muncher, directory_sorter,sweep_averager,global_interpreter,spin_extractor,asciigui_backend
import datetime,pandas,os,numpy,gc,time,multiprocessing,variablenames,matplotlib,argparse

def main(args):
    def options():
        print("NMR Toolsuite options:")
        functions = [asciigui_backend.DAQExtractor, asciigui_backend.DirSorter, asciigui_backend.SweepAverager, asciigui_backend.NMRAnalyzer, asciigui_backend.GlobalInterpreter, asciigui_backend.SpinCurves]
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

    functions = [asciigui_backend.DAQExtractor, asciigui_backend.DirSorter, asciigui_backend.SweepAverager, asciigui_backend.NMRAnalyzer, asciigui_backend.GlobalInterpreter,asciigui_backend.SpinCurves]
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