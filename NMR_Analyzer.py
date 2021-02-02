"""
Tristan Anderson
tja1015@wildats.unh.edu

Proceed Formally.
"""

"""
VNA Visualizer is an api developed to help visualize the Slifer Laboratory's VNA data. It is meant to be ran
with the gui, but can be called directly from LABView for real-time fitting; since this is python, proceed
formally for this toolsuite has not been optimized.

If future maintenance is needed, see documentation in UNH-NPG>lab_work>students_ugrad>Tristan Anderson>TE Extraction
"""
import variablenames
import pandas, numpy, datetime, matplotlib, math, traceback
from scipy.optimize import curve_fit as fit
from matplotlib import pyplot as plt
from matplotlib.patches import Polygon
from statistics import mode

global fig_size_x, fig_size_y
fig_size_x,fig_size_y = 16,9

font = {'size': 18}
matplotlib.rc('font', **font)


def nearest(test_val, iterable):
    # In an iterable data-structure, find the nearest to the
    # value presented.
    # An iterable structure is an object that has
    # the __iter__() method in: dir(object)
    return min(iterable, key=lambda x: abs(x - test_val))


def add_entry(*rowvals,**kwargs):
    ##################    What it does     ####################
    # Adds a line to the persistence csv *if* it exists       #
    # If the csv does not exist, an empty one will be created #
    # Then the entry will be added to the new file            #
    ################## What it does but simple ################
    # this function takes arguments passed to it in the order #
    # of the 'headers' list, and creates an entry (row) in the#
    # persistence csv.                                        #
    ###########################################################

    def gen_persistence(path, columns):
        # Creates a comma separated value file at path
        # with the columns that you give it
        with open(path + '.csv', 'w') as f:
            for index, column in enumerate(columns):
                f.write(column)
                if index < len(columns) - 0:
                    f.write(',')
                else:
                    f.write('\n')

    def get_persistence(headers, fname, addition=''):
        # Read the DF, if it doesn't exist: then makes one
        # THIS FUNCTION RETURNS A pandas.DataFrame() type.
        try:
            with open(fname, 'r') as f: # Read the df
                return pandas.read_csv(f)
        except (FileNotFoundError, pandas.errors.EmptyDataError):   # if it doesnt exists
            gen_persistence('global_analysis'+addition, headers) # make it
        finally:
            try:
                with open(fname, 'r') as f: # Read the df.
                    return pandas.read_csv(f)
            except FileNotFoundError:   # If even THAT (^) fails,
                print("Something went wrong in the add_entry function")
                exit()  # Give up.
    h_orig = variables.na_global_analysis_headers
    headers=kwargs.pop("headers",h_orig)
    getdf=kwargs.pop('getdf', False)
    addition = kwargs.pop('addition', '')
    dontwrite = kwargs.pop('dontwrite', False)

    fname = "global_analysis"+addition+".csv"


    if len(headers) != len(rowvals):
        if len(headers) > len(rowvals):
            print("*Advisory: More headers than rowvalues in add_entry.")
            print("             are you passing every header that you need?")
        else:
            print("***ERROR: More rowvals than headers in add_entry.")
            print("          DATA IS BEING DROPPED and not added to global_analysis.csv")
            print("          RECHECK headers and rowvalues.")
    # Get the persistence df. Then add an entry to it passed to the function in *rowvals
    df = get_persistence(headers, fname, addition=addition).append(pandas.DataFrame(dict(zip(headers,rowvals)), index=[0]),
                                                ignore_index=True)
    with open(fname, 'w') as f:
        df.to_csv(f, index=False)


def return_persistence_df(path):
    try:
        with open(path, 'r') as f:
            return pandas.read_csv(f)
    except FileNotFoundError:
        print("File was not at specified path")


def gui_bl_file_preview(filename, delimeter):
    h2, header, tf_file, lines_to_skip = [], [], [], 0
    with open(filename, 'r') as f:
            for index, line in enumerate(f):
                header.append(len(line.split(delimeter)))
                h2.append(line)
            data_width = mode(header)
            for element in header:
                if element == data_width:
                    tf_file.append(False)
                else:
                    tf_file.append(True)
            lines_to_skip = 0
            while any(tf_file[lines_to_skip:]):  # While any values are true, iterate through it, deleting the first occurance
                lines_to_skip += 1
            h2 = h2[:lines_to_skip+200] 
    return h2, header, tf_file, lines_to_skip


def gui_rawsig_file_preview(rawsigfilename, delimeter, vnaVmeType):
    h2, header, tf_file = [], [], []
    with open(rawsigfilename, 'r') as f:
        for index, line in enumerate(f):
            ##########################################
            """
                This if-else block extracts data from
                the data files that are given to the
                gui. It reads and interprets the header
                of the TE file, and will attempt to use
                the data for later on.
            """
            l = line.split(delimeter)
            if vnaVmeType.upper() == "VNA":
                if index == 1: # dateline for vna
                    dateline = list(line)
                    #! Date: 12/17/2019 11:17:25 AM
                    #&&&&&&& mm/dd/YYYY II:MM:SS %p"
                    TE_DATE = datetime.datetime.strptime("".join(dateline[8:]),"%m/%d/%Y %I:%M:%S %p\n")
                    I = None
                    T = None
                    cccst3_t = None
                    vapor_pressure_t = None
                    centroid = None
                    spread = None
            elif vnaVmeType.upper() == "VME":
                if index == 0:
                    dateish = l[1]
                    #2019-12-19 23:59:47
                    TE_DATE = datetime.datetime.strptime(dateish, "%Y-%m-%d %H:%M:%S")
                    #Time\t2019-12-19 22:01:07\tVapor Pressure Temperature (K)\t1.219363
                    vp = l[3] # Vapor pressure
                    vapor_pressure_t = vp
                    try:
                        float(vp)
                        vptf = True
                    except:
                        vptf = False

                if index == 1:
                    #Magnet Current (A)\t48.666000\tCCCS.T3 (K)\t2.860396
                    I = l[1]
                    t3 = l[3]
                    cccst3_t = t3
                    
                    try:
                        I = float(I)
                        itf = True
                    except ValueError:
                        itf = False
                        print("WARNING: TE-File is reporting: Magnet Current (A)", I)

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
                    #Central Freq (MHz)\t212.990000\tFreq Span (MHz)\t0.400000
                    centroid = l[1]
                    spread = l[3]


            header.append(len(line.split(delimeter)))
            h2.append(line)
    data_width = mode(header)

    for element in header:
        if element == data_width:
            tf_file.append(False)
        else:
            tf_file.append(True)
    lines_to_skip = 0
    while any(tf_file[lines_to_skip:]):  # While any values are true, iterate through it, deleting the first occurance
        lines_to_skip += 1
    #lines_to_skip -= 1 # Python indexing; will grab the last line in the header if you do this. Which probably not be properly formtted...
    h2 = h2[:lines_to_skip+200]
    return header, h2, TE_DATE, I, T, cccst3_t, vapor_pressure_t, lines_to_skip, centroid, spread


def gui_file_fetcher(RAWSIG_Path, Baseline_Path, vnavmetype, impression=False, blskiplines=4, binning=1, rawsigskiplines=4):
    # this provides a wrapper for the api you've
    #   developed here
    """
     Fetches Data
        - Reads Data from paths
            - skips certain number of lines
            - Assumes tab delimiting
            - Returns DF [MHz, Re(S11), Im(S11)]
        - Converts Data if necessary
            - Changes S11 parameter basis to Re(Z)
        - Returns Data
    """
    if vnavmetype == "VNA":
        return vna_frames(
            RAWSIG_Path, Baseline_Path,  impression=impression, title=RAWSIG_Path.split('/')[-1].split('.')[0],
            binning=binning, rawsigskiplines=rawsigskiplines, blskiplines=blskiplines
        )
    else:
        return vme_frames(
            RAWSIG_Path, Baseline_Path,
            binning=binning, rawsigskiplines=rawsigskiplines, blskiplines=blskiplines
        )


def vme_frames(RAWSIG_Path, Baseline_Path, binning=1, blskiplines=4, rawsigskiplines=4):
    te_df = vme_file_parser(RAWSIG_Path, rawsigskiplines)
    # Fetch TE-Data
    copy_tedf = te_df

    baseline_df = vme_file_parser(Baseline_Path, blskiplines)
    # Fetch Background Data

    if binning > 1:
        # this rebins the data before anything is converted.
        bl = []
        te = []
        baseline_df_binned = pandas.DataFrame()
        te_df_binned = pandas.DataFrame()
        for column in te_df:
            x = 0
            x_l = []
            for index, val in enumerate(te_df[column]):
                if index % (binning) == 0 and index != 0:
                    x_l.append(x / binning)
                    x = 0
                x += val

            te_df_binned[column] = x_l

        for column in baseline_df:
            x = 0
            x_l = []
            for index, val in enumerate(baseline_df[column]):
                if index % (binning) == 0 and index != 0:
                    x_l.append(x / binning)
                    x = 0
                x += val

            baseline_df_binned[column] = x_l
        te_df = te_df_binned
        baseline_df = baseline_df_binned

    
    y = variablenames.na_vme_yaxis_default
    x = variablenames.na_vme_xaxis_default
    

    master2 = te_df.subtract(baseline_df, axis='index')
    # SUBTRACT AFTER CONVERSION
    master2[x] = te_df[x]
    # Correct the X-Axis
    master2["Raw "+y] = te_df[y]
    master2["BL "+y] = baseline_df[y]

    

    return master2


def vna_frames(
        RAWSIG_Path, Baseline_Path, impression=False,
        title="", z_im=False, binning=1, blskiplines=4, rawsigskiplines=4
):
    """
        Responsible for collecting and converting the dataframes
            Mainly for non-gui use.

    """
    te_df = vna_file_parser(RAWSIG_Path, rawsigskiplines)
    # Fetch TE-Data

    baseline_df = vna_file_parser(Baseline_Path, blskiplines)
    # Fetch Background Data

    if binning > 1:
        # this rebins the data before anything is converted.
        bl = []
        te = []
        baseline_df_binned = pandas.DataFrame()
        te_df_binned = pandas.DataFrame()
        for column in te_df:
            x = 0
            x_l = []
            for index, val in enumerate(te_df[column]):
                if index % (binning) == 0 and index != 0:
                    x_l.append(x / binning)
                    x = 0
                x += val

            te_df_binned[column] = x_l

        for column in baseline_df:
            x = 0
            x_l = []
            for index, val in enumerate(baseline_df[column]):
                if index % (binning) == 0 and index != 0:
                    x_l.append(x / binning)
                    x = 0
                x += val

            baseline_df_binned[column] = x_l
        te_df = te_df_binned
        baseline_df = baseline_df_binned

    r = "Re(S11)"
    i = "Im(S11)"
    zre = "Z_re"
    zim = "Z_im"
    te_converted = get_z(te_df)
    # Convert the TE

    baseline_converted = get_z(baseline_df)
    # Convert baseline TE

    master2 = baseline_converted.subtract(te_converted, axis='index')
    # SUBTRACT AFTER CONVERSION
    master2["MHz"] = te_df["MHz"]
    # Correct the X-Axis
    master2["Raw Re(Z)"] = te_converted[zre]
    master2["Raw Im(Z)"] = te_converted[zim]
    master2["BL Re(Z)"] = baseline_converted[zre]
    master2["BL Im(Z)"] = baseline_converted[zim]

    if impression:
        # Delivers impression of the data if the data is not
        from matplotlib.gridspec import GridSpec

        def format_axes(fig, x):
            for i, ax in enumerate(fig.axes):
                ax.set_xlabel(x)
                if i == 0:
                    ax.set_ylabel("Re(S11)")
                elif i == 1:
                    ax.set_ylabel("Im(S11)")
                elif i > 1:
                    ax.set_ylabel("Re(Z): Impedence [Ω]")

                ax.legend(loc='best')

        fig = plt.figure(constrained_layout=True, figsize=(32, 18))

        gs = GridSpec(3, 2, figure=fig)
        ax1 = fig.add_subplot(gs[0, 0])  # R s11
        ax2 = fig.add_subplot(gs[0, 1])  # I s11
        if z_im:
            ax3 = fig.add_subplot(gs[1, 0])  # R Z
            ax4 = fig.add_subplot(gs[1, 1])  # I Z
        else:
            ax3 = fig.add_subplot(gs[1, :])
        ax5 = fig.add_subplot(gs[2, :])  # RZTE-RZBG

        y = 'Z_re'
        yy = 'Z_im'
        yyy = "Re(S11)"
        yyyy = "Im(S11)"

        xlabel = "MHz"
        x = master2[xlabel].values
        y1 = te_df[yyy].values
        y2 = baseline_df[yyy].values

        y3 = te_df[yyyy].values
        y4 = baseline_df[yyyy].values

        y5 = te_converted[y].values
        y5a = baseline_converted[y].values

        y6 = te_converted[yy].values
        y6a = baseline_converted[yy].values

        ax1.scatter(x, y1, label=yyy + ' TE', s=10, c='r')
        ax1.scatter(x, y2, label=yyy + ' Baseline', s=10, c='b')
        ax2.scatter(x, y3, label=yyyy + ' TE', s=10, c='r')
        ax2.scatter(x, y4, label=yyyy + ' Baseline', s=10, c='b')

        ax3.scatter(x, y5a, label=y + ' Baseline', s=3, c='g')
        ax3.scatter(x, y5, label=y + ' TE', s=1, c='magenta')
        if z_im:
            ax4.scatter(x, y6a, label=yy + ' Baseline', s=3, c='g')
            ax4.scatter(x, y6, label=yy + " TE", s=1, c='magenta')

        ax5.scatter(x, y5 - y5a, label=y + " Subtraction", s=10, c='orange')
        fig.suptitle(title)
        format_axes(fig, xlabel)

        now = datetime.datetime.now()
        date_time = now.strftime("%m_%d_%Y %H%M%S")
        plt.savefig(title + "_Impression_" + date_time, dpi=200)
        print(title + "_Impression_" + date_time + ".png", "Saved to current working\
        directory.")

    return master2


def vme_file_parser(filename, skiplines):
    # Find out file architecture
    header = ["MHz", "Potential (V)"]
    # Begin Function
    file = []
    with open(filename, 'r') as f:
        for index, line in enumerate(f):
            # enumerates file line-by-line with the file-line (index) it is
            # currently reading, and that file-line's content (line)
            if index > skiplines:
                # This takes care of the .s1p file header
                tl = line.split('\t')
                # Split each line into a list delimited by a tab.
                if len(tl) == 2:
                    # If we have all 2 columns saved and in a list...
                    k = [float(i) for i in tl]
                    # Store them in a list changing their types to floats
                    file.append(k)
                    # Save each line as a list inside another list
                else:
                    print("Something went wrong during file parsing.")
                    print(filename, "line: ", index, tl)
                    exit()
    master = pandas.DataFrame(file, columns=header)
    # Convert this list of lists (lines) into a useful structure
    return master


def vna_file_parser(filename, skiplines=4):
    """
    - Takes a tab-delimited file, and reads it line by line
    - You must make the s1p file a tab-delimited file. I did with the following
    bash script in the data-directory.

        This bash script modifies every file within the working directory
        and replaces sequences of spaces greater than one (i.e. "  ")  w/
        a tab character \t.
        #################################################################
        #!/bin/bash
        for d in */ ; do
            cd "$d"
            echo $d
            for file in *
            do
                sed 's/ \+ /\t/g' "$file" > tmpfile && mv tmpfile "$file"
                echo "$file"
            done

            cd ".."
        done
        #################################################################
    """
    # EXAMPLE FILE HEADER
    """
    ! COPPER MOUNTAIN TECHNOLOGIES, R60, 00111218, 19.1.1/3.0
    ! Date: 12/17/2019 11:46:47 AM
    ! Data: Format [Calibration Info]
    ! Frequency		S11: Re/Im F1                  
    # MHZ S RI R 50                                 # The program will detect that this is the last line
    2.11880000E+02	 4.71759300E-01	 1.83014927E-01 # In the header of the file.
    2.11880200E+02	 4.71734918E-01	 1.82917104E-01
    2.11880400E+02	 4.71852209E-01	 1.82842974E-01
    2.11880600E+02	 4.71729258E-01	 1.82838358E-01
    2.11880800E+02	 4.71775346E-01	 1.82808156E-01
    """
    # CHANGE: this list in the event that the order of the columns in the VNA have switched.
    header = ["MHz", "Re(S11)", "Im(S11)"]
    # Begin Function
    file = []
    with open(filename, 'r') as f:
        for index, line in enumerate(f):
            # enumerates file line-by-line with the file-line (index) it is
            # currently reading, and that file-line's content (line)
            if index > skiplines:
                # This takes care of the .s1p file header
                tl = line.split('\t')
                # Split each line into a list delimited by a tab.
                if len(tl) == 3:
                    # If we have all 3 columns saved and in a list...
                    k = [float(i) for i in tl]
                    # Store them in a list changing their types to floats
                    file.append(k)
                    # Save each line as a list inside another list
                else:
                    print("Something went wrong during file parsing.")
                    print(filename, "line: ", index, tl)
                    exit()
    master = pandas.DataFrame(file, columns=header)
    # Convert this list of lists (lines) into a useful structure
    return master


def get_z(df):
    # I swear to god this is correct.
    # This converts the Real and imaginary S11 components
    # Into Z: The impedance.

    Z_0 = 50

    s11_re = df["Re(S11)"].values
    s11_im = df["Im(S11)"].values
    z_numerator_re = 1 + s11_re
    z_numerator_im = s11_im
    z_denominator_re = 1 - s11_re
    z_denominator_im = s11_im * (-1)
    z_numerator_value = numpy.sqrt(z_numerator_re ** 2 + z_numerator_im ** 2)
    z_numerator_phase = numpy.arctan(z_numerator_im / z_numerator_re)
    z_denominator_value = numpy.sqrt(z_denominator_re ** 2 + z_denominator_im ** 2)
    z_denominator_phase = numpy.arctan(z_denominator_im / z_denominator_re)
    z_quotient_value = z_numerator_value / z_denominator_value
    z_quotient_phase = z_numerator_phase - z_denominator_phase
    z_value = Z_0 * z_quotient_value
    z_re = z_value * numpy.cos(z_quotient_phase)
    z_im = z_value * numpy.sin(z_quotient_phase)

    # IN the first argument, and in the 'columns' keyword of the following command, feel free to add
    #   one of the lists above in the zip(), and give it an appropriate name to propogate an intermediate
    #   impedence conversion forward through the gui and program execution.  
    packed = pandas.DataFrame(
        zip(df["MHz"].values, z_re, z_im),
        columns=["MHz", "Z_re", "Z_im"], dtype=float
    )
    return packed


def integrate_curve(start_index, end_index, df=None, x="MHz", y="Z_re"):
    # A trapezodial integration method.
    # It interpolates between datapoints.
    if df is not None:
        try:
            # Is it a dataframe?
            zre = df[y].values
            mhz = df[x].values
        except:
            # If it's not a dataframe, then it's a list. Because thats how I
            # call it.
            zre = df[0]
            mhz = df[1]
    df_len = len(zre)
    df_indecies = [i for i in range(0, df_len)]
    if start_index in df_indecies and end_index in df_indecies:
        integration = []
        for i in range(start_index, end_index):
            dx = mhz[i + 1] - mhz[i]
            dy = (zre[i + 1] + zre[i]) * dx / 2
            # Trapezodial reimann A = (a+b)*h/2
            integration.append(dy)
        return integration
    else:
        print("start, end, not in range(df_len)")
        raise IndexError


def absorbtion_dispersion_ellie(f, f0, w, kmax, theta):
    # x = ((f0-f)/(w/2)); w=fwhm
    # k = kmax * cos**2(theta/2)
    # A = k * 1/(1+x**2) = kmax*cos(theta/2)**2/(1+x**2)
    # D = k * x/(1+x**2) = kmax*cos(theta/2)**2*x/(1+x**2)
    # Re(Z) = A * cos(theta) + D * sin(theta)
    return kmax*numpy.cos(theta/2)**2/(1+((f0-f)/(w/2))**2)*numpy.cos(theta) + kmax*numpy.cos(theta/2)**2*((f0-f)/(w/2))/(1+((f0-f)/(w/2))**2)*numpy.sin(theta)


def sin(xdata, a, t, p, b):
    return a * numpy.sin(t * xdata - p) - b


def sixth_order(x, a, b, c, d, e, f, g):
    return a * x ** 6 + b * x ** 5 + c * x ** 4 + d * x ** 3 + e * x ** 2 + f * x + g


def fifth_order(xdata, a, b, c, d, e, f):
    return a * xdata ** 5 + b * xdata ** 4 + c * xdata ** 3 + d * xdata * 2 + e * xdata + f


def fourth_order(xdata, a, b, c):
    return a * xdata ** 2 + b * xdata + c


def third_order(x, d, e, f, g):
    return d * x ** 3 + e * x ** 2 + f * x + g

def lorentzian_ellie(xdata, x0, w, A, B):
    return A +  1 / (numpy.pi) * (1 / 2 * w) / (((xdata - x0)) ** 2 + (1 / 2 * w) ** 2)


def lorentzian(xdata, x0, w, A):
    # https://mathworld.wolfram.com/LorentzianFunction.html
    # w = GAMMA = FWHM
    # x0 = x0 = Centering
    # A = Scaling

    #A = 1

    return A / (3.1415926535897932384626433) * (1 / 2 * w) / (((xdata - x0)) ** 2 + (1 / 2 * w) ** 2)


def gcurve(xdata, x0, sigma, A):
    return A*numpy.exp(-(xdata - x0)** 2 / (2 * sigma ** 2))

def exponential(xdata, tau, sigma, A, s):
    return A*numpy.exp(tau*xdata) + s


def chisquared(yobs, yex):
    return sum(abs((yobs-yex)**2/yex))


def getsigma(yobs, yex):
    # 1 = y_o-y_e**2/n*sigma**2
    # sigma = y_o-y_e/(n**.5)
    # This overestimates; and that's okay.
    return yobs-yex/(len(yobs)**.5)


def kchisq(yobs, yex, sigma):
    return sum(abs((yobs-yex)**2/sigma**2))/len(yobs)


def tpol(b, t, mu = 1.4106067873 * 10 ** -26):
    # default Mu is for the proton
    k = 1.38064852 * 10 ** -23
    return numpy.tanh(mu * b / (k * t))


def gff(df, start, finish, fitname, **kwargs):
    """
    Generalized Fitting Function

    #####################################################################
    # THIS FUNCTION OPERATES BY ARRAY INDEXES, NOT BY NUMERICAL VALUES. #
    #   __nearest IS YOUR FRIEND                                        #
    #####################################################################

    Fucntion parameters that should be used together are grouped
        together in the definition of the function.

    This fitting function has two modes
        It can fit the data arround a signal slice TO ONE FUNCTION that you 
            provide it (generally the fastest thing to do)
            OR it fits N-funtions to N-specific regions of data.

        - fit_sans_signal: Fits the data arround a signal TO ONE 
          SINGLE FUNCTION
                Fits the data arround the signal, where the signal is 
                selected by index placement within the column of the 
                dataframe. Within this function, the signal is generally 
                within: ydata[s:f].

                If sf, and ff parameters are not assigned a value during 
                this functions invocation, the function will
                default to fitting EVERYTHING EXCEPT THE SIGNAL

                If sf and ff parameters ARE assigned a value during this 
                function's invocation, the function will
                fit data in the following slice types:
                        Region 1: (xdata[sf:start], ydata[sf:start]); 
                        Region 2: (xdata[finish:ff], ydata[finish:ff])
        - Normal:
                Expects variables "function", "fit_bounds" to be populated,
                and of equal length. "function" must be a list of function
                names callable within the namespace.
                "fit_bounds" must be a list of tupples AKA: 
                        [(s1, f1), (s2,f2), ..., (sn,fn)] that are the 
                index-respective fitting slices that we "zip" and fit with 
                the function at the same index in "function"
                ############################################################
                # I am currently grappling the logic of generalizing this  #
                # function so that I can truly have an  n-generalized      #
                # method of fitting as many functions to as many regions of#
                # data that I want.                                        #
                # Proceed Formally.                                        #
                ############################################################

    """
    def get_function(f_name,xdata,var):
        if f_name == "sin":
            yfit = sin(xdata, var[0], var[1], var[2], var[3])
        
        elif f_name =="absorbtion_dispersion_ellie":
            yfit = absorbtion_dispersion_ellie(xdata, var[0], var[1], var[2], var[3])

        elif f_name =="lorentzian_ellie":
            yfit = lorentzian_ellie(xdata, var[0], var[1], var[2], var[3])

        elif f_name == "fourth_order":
            yfit = fourth_order(xdata, var[0], var[1], var[2])

        elif f_name == "third_order":
            yfit = third_order(xdata, var[0], var[1], var[2], var[3])

        elif f_name == "fifth_order":
            yfit = fifth_order(
                xdata, var[0], var[1], var[2], var[3],
                var[4], var[5]
            )
        elif f_name == "sixth_order":
            yfit = sixth_order(
                xdata, var[0], var[1], var[2], var[3], var[4],
                var[5], var[6]
            )
        elif f_name == "exponential":
            yfit = exponential(xdata, var[0], var[1], var[2], var[3])
        else:
            print("Function not in get_function in VNA_Visualizer\n"
                  "If you added a function be sure you have done\n"
                  "It everywhere.\n")
            print("#"*15, '\n',"TRACEBACK PRINTED TO \'debug\' FILE.")
            with open('debug', 'w') as f:
                traceback.print_stack(file=f)
            return False
        return yfit

    # Get kw arguments
    # Sets which Y to evaluate
    y = kwargs.pop('y', "Z_re")

    # Sets which X to evaluage
    x = kwargs.pop('x', "MHz")

    # Do you want to see this graph? Useful when fitting unfamiliar data
    preview = kwargs.pop('preview', False)

    # Give the plot a title
    plttitle = kwargs.pop('plttitle', '')

    # Used to fit the general form of the NMR data
    # (useful for isolating just the peak)
    fit_sans_signal = kwargs.pop("fit_sans_signal", False)

    # What function do you want to fit the NMR data with?
    function = kwargs.pop("function", [])

    # Expects a 2D array with the innner dimension being
    # tupples: [(x1,x2), (x3,x4) ... (xn-1, xn)]
    # Each tupple represents the index x-range to fit each function in
    # the function list
    fit_bounds = kwargs.pop("fit_bounds", [])

    # If fiting without the signal, this is used to narrow the fit region
    # to the left of the peak.
    #
    #     (sf index)  (start index)    (finish index)  (ff index)
    #             |            |    --     |            |
    #             |            |    --     |            |
    #  not fitting|  fitting   |  ------   |  fitting   | not fitting
    #             V            V --    --- V            V 
    # ------------|++++++++++++|-       ---|++++++++++++|-------------
    #  sf region  |            |   SIGNAL  |            |  ff region   
    
    sf = kwargs.pop('sf', None)  # (ff region)

    # If fiting without the signal, ff is used to narrow the fit region
    # to the RIGHT of the peak. Marked by the ASCII art above.

    ff = kwargs.pop('ff', None)

    # Toggles saving the figure
    savefit = kwargs.pop('savefit', False)

    # If the above is toggled, the file needs a name
    filename = kwargs.pop('filename', 'UNNAMED_GRAPH')

    # Helps with plot sizing and accuracy with TE calculation placed
    # On the graph
    binning = kwargs.pop('binning', 1)

    # Sets the window for data
    xmin = kwargs.pop('xmin', None)
    xmax = kwargs.pop('xmax', None)

    # Are you using a gui?
    gui = kwargs.pop('gui', False)

    data_colors = {0: 'blue', 1: "orange", 2: 'magenta'}
    # A circuit of colors that helps visually identify different fitting
    #   sections by coloring the data
    fit_colors = {0: 'yellow', 1: "blue", 2: "green"}
    # A circuit of colors that helps visually identify different fit lines
    #   by coloring the fits

    # If this function is being called by the automator in gui.py, we need to know about it
    automated = kwargs.pop('automated', False)

    # If This function is being used to fit a lorentzian to the raw signal
    #   Via Ellie's NMR Model methods, then a p0 is needed.
    p0 = kwargs.pop('p0', None)

    bounds = kwargs.pop('bounds', [[-numpy.inf, -numpy.inf, -numpy.inf, -numpy.inf ],[numpy.inf,numpy.inf,numpy.inf,numpy.inf]])

    if xmin is not None and xmax is not None:
        # R's equalivent of doing slicing by value
        df = df[(df.x > xmin) & (df.x < xmax)]

    xdata = df[x].values
    if automated:
        try:
            ydata = df[y].values
        except KeyError:
            # This happens most often during 
            print("***ERROR: Key Error: \'"+str(y)+"\'")
            print("*ADVICE: Check your fit function, did the function fail to fit?")
            print("*ADVICE: No entry exists by the name \'"+str(y)+"\'")
            #print("***: Aborting.")
    else:
        ydata = df[y].values

    
    x_to_fit = []
    y_to_fit = []
    if fit_sans_signal and len(function) == 1:
        # Fit data arround the signal to one function
        # fits dataset to 1 function DEMANDS SF & FF to have been called.
        # start & finish are the signal
        # sf and ff are the left and right starting and finishing bounds
        # for the fits.

        # x&y data are sliced like: [sf:start] & [finish:ff]
        try:
            if sf is None or ff is None:
                # We really need sf and ff to have been called, otherwise,
                # the program use all of the data around the signal.
                raise NameError
                # if you have data that fits relatively well: great!
                # You can save some typing. Otherwise if you are having
        except NameError:
            # troubblesome data on the endpoints of your dataset,
            # then calling sf and ff here will curb that.
            ff = len(xdata) - 1
            sf = 0

        y_fit_data = []
        f_name = function[0]

        x_to_fit.append(xdata[sf:start])
        x_to_fit.append(xdata[finish:ff])
        y_to_fit.append(ydata[sf:start])
        y_to_fit.append(ydata[finish:ff])

        x_data_for_fit = numpy.concatenate(x_to_fit)
        y_data_for_fit = numpy.concatenate(y_to_fit)
        
        fitnames =['sin', 'third_order', 'fourth_order', 'fifth_order', 'sixth_order', "lorentzian_ellie", "absorbtion_dispersion_ellie"]
        chsq = {}
        for f in fitnames:
            try:
                var, _ = fit(eval(f), x_data_for_fit, y_data_for_fit)  # Prof. Narayan is screaming because I'm evaling' here
                yfit = get_function(f, x_data_for_fit, var)
                chsq[f] = chisquared(y_data_for_fit, yfit)/(len(y_data_for_fit)-3) # reduced chisquared
            except: # We probably failed fitting
                chsq[f] = "FITTING ERROR"
        try:
            # We try to fit the data that we sliced from above.
            var, pcov = fit(eval(f_name), x_data_for_fit, y_data_for_fit, p0=p0, bounds=bounds)
            #print(f_name, var)
        except:  # If we failed fitting
            rawsigfit = {}
            fig, ax = plt.subplots(figsize=(fig_size_x, fig_size_y))
            ax.scatter(xdata, ydata, c='black', s=2 * binning, label="Data")
            ax.scatter(
                x_data_for_fit, y_data_for_fit, c='r', s=2 * binning,
                label="Data we've fitted"
            )
            ax.legend(loc='best')
            fig.suptitle(plttitle)
            if gui:
                print("***ERROR: Main fit subtraction failed for", f_name, '\n')
                return df, fig, chsq, rawsigfit, True

            plt.show()
            print("ERROR: Fitting failed on function: " + str(function[0]))
            exit()


        yfit = get_function(f_name, xdata, var)



        if savefit:
            # I can save the fit for you if you toggle this flag.
            fig, ax = plt.subplots(figsize=(fig_size_x, fig_size_y))
            ax.set_title(plttitle + " " + fitname + " fit")
            ax.scatter(xdata, ydata, c='black', s=2 * binning, label="Data")
            # Plots all of the data regardless if it will be plotted
            # over later
            ax.scatter(
                x_data_for_fit, y_data_for_fit, c='g', s=2 * binning,
                label="Data we've fitted"
            )
            # Plots the fit data, that you saw bsliced above this line

            ax.scatter(
                xdata[start:finish], ydata[start:finish], c='r',
                s=2 * binning, label="Signal"
            )
            # Plots the data within [start:finish] to help the user see
            # where they are telling the
            # program where the signal is.
            ax.scatter(xdata, yfit, c='b', s=2 * binning, label="Fit")
            # Plots the fit of the data

            ax.set_ylabel(y)
            ax.set_xlabel(x)
            ax.legend(loc='best')
            plt.savefig(filename + "_FIT", dpi=600)

        if preview:
            # Allows the user to preview the data while they are fidgeting
            # with other parameters
            fig, ax = plt.subplots(figsize=(fig_size_x, fig_size_y))
            # responsible for the fitting regions,
            # signal-highlighting (...etc)
            ax.set_title("Preview of " + fitname + " fit")
            ax.scatter(xdata, ydata, c='black', s=2 * binning, label="Data")
            ax.scatter(
                x_data_for_fit, y_data_for_fit, c='g', s=2 * binning,
                label="Data we've fitted"
            )
            ax.scatter(
                xdata[start:finish], ydata[start:finish], c='r',
                s=2 * binning, label="Signal"
            )
            ax.scatter(xdata, yfit, c='b', s=2 * binning, label="Fit")

            ax.set_ylabel(y)
            ax.set_xlabel(x)
            ax.legend(loc='best')
            plt.show()

    else:  # n-GENERALIZED fitting
        fitz = []
        # Where we place our ydata.
        for index, f_name in enumerate(function):
            # Iterate through functions we gotta fit
            bound_tupple = fit_bounds[index]
            # Find the indexes to which we can slice the data
            sfit, efit = bound_tupple[0], bound_tupple[1]
            xfit, yfit = xdata[sfit:efit], ydata[sfit:efit]
            # Slice x and y data for fitting
            
            var, _ = fit(eval(f_name), xfit, yfit)
            # Fit that stuff
            fitz.append(get_function(fdata, xdata, var))

            # Append the ydata to this place where we store our
            # ydata, then repeat

        if len(fitz) == 2:
            # This is a band-aid solution for when
            # n=len(function); as n=2
            # when in n-GENERALIZED fitting; not really generalized, is it?
            y_combined_fit_data = []
            index = 0
            first_bound_s = fit_bounds[index][0]
            first_bound_f = fit_bounds[index][1]
            fit1 = fitz[index]

            second_bound_s = fit_bounds[index + 1][0],
            second_bound_f = fit_bounds[index + 1][1]
            fit2 = fitz[index + 1]

            r = (fit1 - fit2) ** 2

            cross_index = numpy.where(r == numpy.amin(r))[0][0]
            y_combined_fit_data.append(fit1[first_bound_s:cross_index])
            y_combined_fit_data.append(fit2[cross_index:second_bound_f])
            yfit = numpy.concatenate(y_combined_fit_data)

            if savefit:
                fig, ax = plt.subplots(figsize=(fig_size_x, fig_size_y))
                ax.set_title(plttitle + " " + fitname + " fits")
                ax.scatter(
                    xdata, ydata, c='black', s=2 * binning,
                    label="Data"
                )
                ax.scatter(
                    xdata[start:finish], ydata[start:finish], c='r',
                    s=2 * binning, label="Signal"
                )
                for index, f_name in enumerate(function):
                    fit_function_ydata = fitz[index]
                    ss, ff = fit_bounds[index][0], fit_bounds[index][1]
                    ax.scatter(
                        xdata[ss:ff], ydata[ss:ff],
                        c=data_colors[index], s=2 * binning,
                        label="Data for Fit " + str(index)
                    )
                    if index == 0:
                        ax.scatter(
                            xdata[ss:cross_index],
                            fit_function_ydata[ss:cross_index],
                            c=fit_colors[index], s=2 * binning,
                            label="Fit" + str(index)
                        )
                    elif index == 1:
                        ax.scatter(
                            xdata[cross_index:ff],
                            fit_function_ydata[cross_index:ff],
                            c=fit_colors[index], s=2 * binning,
                            label="Fit" + str(index)
                        )

                ax.set_ylabel(y)
                ax.set_xlabel(x)
                ax.legend(loc='best')

                plt.savefig(filename + " " + fitname + " fits", dpi=600)

            if preview:
                fig, ax = plt.subplots(figsize=(fig_size_x, fig_size_y))
                ax.set_title("Preview of " + fitname + " fits")
                ax.scatter(
                    xdata, ydata, c='black', s=2 * binning,
                    label="Data"
                )
                ax.scatter(
                    xdata[start:finish], ydata[start:finish], c='r',
                    s=2 * binning, label="Signal"
                )
                for index, f_name in enumerate(function):
                    fit_function_ydata = fitz[index]
                    ss, ff = fit_bounds[index][0], fit_bounds[index][1]
                    ax.scatter(
                        xdata[ss:ff], ydata[ss:ff],
                        c=data_colors[index], s=2 * binning,
                        label="Data for Fit " + str(index)
                    )
                    ax.scatter(
                        xdata, fit_function_ydata,
                        c=fit_colors[index], s=2 * binning,
                        label="Fit" + str(index)
                    )

                ax.set_ylabel(y)
                ax.set_xlabel(x)
                ax.legend(loc='best')
                plt.show()

    if len(yfit) == len(xdata):
        df[fitname] = yfit
        df[fitname + " Subtraction"] = ydata - yfit

    if gui:
        if fitname == "absorbtion_dispersion_ellie": 
            rawsigfit = dict(zip(['f0', 'w', 'kmax', 'theta'],var))
        else:
            rawsigfit = {}
        fig, ax = plt.subplots(figsize=(fig_size_x, fig_size_y))
        ax.set_title(plttitle + " " + fitname + " fit")
        ax.scatter(xdata, ydata, c='black', s=2 * binning, label="Data")
        # Plots all of the data regardless if it will be plotted
        # over later
        ax.scatter(
            x_data_for_fit, y_data_for_fit, c='g', s=2 * binning,
            label="Data we've fitted"
        )
        # Plots the fit data, that you saw bsliced above this line

        ax.scatter(
            xdata[start:finish], ydata[start:finish], c='r',
            s=2 * binning, label="Signal"
        )
        # Plots the data within [start:finish] to help the user see
        # where they are telling the
        # program where the signal is.
        ax.scatter(xdata, yfit, c='b', s=2 * binning, label="Fit")
        # Plots the fit of the data

        ax.set_ylabel(y)
        ax.set_xlabel(x)
        ax.legend(loc='best')
        #print("Made it here")
        return df, fig, chsq, rawsigfit, False

    else:
        print("Fitting data needs to be reshaped.")
        print("yfit is", len(yfit), "points long.")
        print("x-axis is", len(xdata), "points long.")
        exit()
    return df


def ggf(master, s, f, **kwargs):
    ub = 9.274009994*10**(-24) # Bohr Magnetron 
    up = 1.521*10**(-3)*ub     # Proton Magnetic Moment

    # Sets the plot width of the graph. Does nothing to the data
    xmin = kwargs.pop("xmin", None)
    xmax = kwargs.pop("xmax", None)

    # Sets the plot title
    plttitle = kwargs.pop('plttitle', "")

    # What are going to be the x and y
    x = kwargs.pop('x', "MHz")
    y = kwargs.pop('y', "Z_re")

    # Lets give those Axis labels
    xlabel = kwargs.pop('xlabel', "Frequency (MHz)")
    ylabel = kwargs.pop('ylabel', "Re(Z) Impedence [Ω]")

    # If we save the graph, what name are we going to give the .png?
    filename = kwargs.pop('filename', "")

    # Highlight the data we fitted with green datapoints
    fit_marking = kwargs.pop('fit_marking', False)
    # Used in tandem with the above line to highlight green datapoints.
    fit_bounds = kwargs.pop('fit_bounds', [])


    # Do not show the graph before it is saved.
    noshow = kwargs.pop('noshow', True)

    # If you binned your data, you should resize your scatter-dot size
    binning = kwargs.pop('binning', 1)

    # Do you want to highlight in red where you told the program where the
    # signal was?
    redsig = kwargs.pop('redsig', False)

    # Do you want to integrate the data across the interval where you said
    # that the signal was?
    integrate = kwargs.pop('integrate', False)

    # If you want the thermal equalibrium value:
    thermal_equalibrium_value = kwargs.pop("thermal_equalibrium_value", False)

    # Thermal polarization equation variables
    b = kwargs.pop('b', None)
    T = kwargs.pop('T', None)

    # If you've done a fit subtraction, do you want to fit a lorentzian
    # to the signal
    fitlorentzian = kwargs.pop('fitlorentzian', False)

    # Do you have some data to compare it to?
    edata = kwargs.pop('edata', -1)

    # Returns the figure for viewing in the second page of the gui
    gui = kwargs.pop('gui', False)

    # Closes and clears all figures to save memory.
    clearfigs = kwargs.pop('clearfigs', False)

    # Passed  if fitlorentzian is true
    fitlorentziancenter_bounds = kwargs.pop('fitlorentziancenter_bounds', None)

    # If this function is being called by the automator in gui.py, we need to know about it
    automated = kwargs.pop('automated', False)
    
    # Added 2020.9.18 Selectable proton, deuteron magnetic moment for gui.
    temu = kwargs.pop('temu', up) 
    

    if clearfigs:
        plt.clf()
        plt.close()

    df = master
    if xmin is not None and xmax is not None:
        df = df[(df[x]<xmax)&(df[x]>xmin)]
    

    start = s
    finish = f
    xdata = df[x].values

    if automated:
        try:
            ydata = df[y].values
        except KeyError:
            # This happens most often during 
            print("***WARNING: Key Error: \'"+str(y)+"\'")
            print("***ADVICE: Check your fit function, did the function fail to fit?")
            print("***ADVICE: No entry exists by the name \'"+str(y)+"\'")
            #print("***: Aborting.")
    else:
        ydata = df[y].values

    dpi = 100
    if xmin is None and xmax is None:
        xmin = min(xdata)
        xmax = max(xdata)
    
    guidict = {}

    fig, ax = plt.subplots(figsize=(fig_size_x, fig_size_y))
    ax.set_title(plttitle)

    # Fancy graph text stuff
    xtxt = dpi * 1
    xtab = dpi * 8
    ypp = dpi * 8.75
    ys = dpi * .2

    if not fitlorentzian:
        ax.scatter(
            xdata, ydata, c='Blue', s=2 * binning,
            label='Data'
        )

    ax.annotate(
        "Bin Width: " + str(binning),
        xy=(xtxt + xtab, ypp - ys),
        xycoords='figure pixels'
    )

    if fit_marking:
        # Highlights the data green that was used to fit the y axis.
        fit_x = []
        fit_y = []
        if len(fit_bounds) == 0:
            if sf is None and ff is None:
                sf = 0
                ff = len(xdata) - 1
            fit_bounds.append([sf, start])
            fit_bounds.append([finish, ff])
        if len(fit_bounds) > 0:
            for bounds in fit_bounds:
                fit_x.append(xdata[bounds[0]:bounds[1]])
                fit_y.append(ydata[bounds[0]:bounds[1]])

        xf = numpy.concatenate(fit_x)
        xy = numpy.concatenate(fit_y)
        ax.scatter(xf, xy, c='g', s=2 * binning, label="Data Fitted")

    if fitlorentzian:
        # Am I supposed to divide by the binning?
        integrated_value = sum(integrate_curve(0, len(df[x]) - 1, df,x=x, y=y))/binning
        guidict["data_area"] = integrated_value

        if True:
            # Adds subplot that quantifies noise band during lorentzian fit
            #  here  ---  ---
            #  ---  ---  ---
            #  ---  --- ----

            """
                         K
                        A A
                       E   E
                      P     P
            ##########       #########
            
            looks at the data around the signal (the #'s), and plots their y-values into a histogram to
            get an estimate on the error attached to each datapoint. 
            """
            left = df[df[x] <= fitlorentziancenter_bounds[0]]
            right = df[df[x] >= fitlorentziancenter_bounds[1]]
            histodata = left.append(right)

            about_peak = histodata[y].values  # y-data about the peak

            binwidth = math.ceil((len(about_peak)**.5)*1.5)
            hist_y, hist_x = numpy.histogram(about_peak, bins=binwidth)
            hist_x = hist_x[1:]

            histo = fig.add_subplot(331)
            #histo.scatter(hist_x, hist_y, label="Scatter", color='red')
            #gcurve(xdata, x0, sigma, A):
            try:
                maxsig = max(hist_x) - min(hist_x)
                hvar, _ = fit(gcurve, hist_x, hist_y,
                              bounds=[(min(hist_x)/2, 0, 0), (max(hist_x)/2, maxsig, max(hist_y))]
                             )
                h_fit = gcurve(hist_x, hvar[0], hvar[1], hvar[2])
                guidict["noisesigma"] = hvar[1]
                histo.plot(hist_x, h_fit, label="Gaussian", color='red')
                histo.annotate("σ: "+str(round(hvar[1], 5)), xy=(max(hist_x)*(1-(1-min(hist_x))*0.75),
                                                                 max(hist_y)*0.5))

            except RuntimeError:
                print("Noise band fitting failed. Measurement error will not be included.")
                hvar = [0,0,0]

            histo.hist(about_peak, label="Noise Band About Signal", bins=binwidth, color='b')
            histo.title.set_text("Error Quantification")
            histo.yaxis.tick_right()
            histo.legend(loc='best', prop={'size':6})

        

        fl, _ = fit(lorentzian, xdata, ydata, bounds=[(fitlorentziancenter_bounds[0], -numpy.inf, -numpy.inf),
                                                      (fitlorentziancenter_bounds[1], numpy.inf, numpy.inf)])

        ltzian = lorentzian(xdata, fl[0], fl[1], fl[2])

        guidict['x0'] = fl[0]  # x0 = Centering
        guidict['w'] = fl[1]  # w = A parameter FWHM
        guidict['a'] = fl[2]  # A = Scaling
        lchisq = chisquared(ydata, ltzian)/(len(ltzian)-1)
        
        relative_error = getsigma(ydata, ltzian)
        avgrelerror = sum(relative_error)/len(relative_error)
        cqs = kchisq(ydata, ltzian, avgrelerror)
        
        guidict['tristan lorentzian chisquared'] = lchisq
        guidict['karl chisquared'] = cqs
        guidict['karl sigma'] = sum(relative_error)/len(relative_error)
        df["Lorentzian signalfit"] = ltzian

        ax.errorbar(xdata, ydata, yerr=avgrelerror, c='Blue', barsabove=True,
            label='Data')

        ax.errorbar(xdata[s:finish], ydata[s:finish], yerr=avgrelerror, c='red', barsabove=True,
            label='Signal')

        #cqs = kchisq(ydata, ltzian, hvar[1]*cqs/len(ydata))
        #print("karlchisq", cqs)
        #print("Reduced karlchisq", cqs/(len(ydata)-3))
        
        # Am I supposed to divide by the binning?
        ltzian_integration = sum(integrate_curve(s, finish, df=df, x=x,y="Lorentzian signalfit"))/binning

        ax.plot(
            xdata, ltzian, linewidth=4, color='orange',
            label="Lorentzian signal-fit"
        )

        ax.annotate(
            "Fit Area: " + str(
                round(ltzian_integration, 6)
            ),
            xy=(xtxt, ypp), xycoords='figure pixels'
        )
        ax.annotate(
            "Peak Center: " + str(round(fl[0],3)
            )+" MHz",
            xy=(xtxt,ypp-43*ys), xycoords='figure pixels'
        )
        ax.annotate(
            "Reduced Chisquared (Distribution): " + str(round(lchisq,5)
            ),
            xy=(xtxt+xtab+80,ypp-43*ys), xycoords='figure pixels'
        )
        ax.annotate(
            "Reduced Relative Chisquared (Errorbar): " + str(round(cqs, 5)
                ), color="blue",
            xy=(xtxt+xtab+80,ypp-42*ys), xycoords='figure pixels')
        guidict["ltzian_integration"] = ltzian_integration

        
    if integrate:
        
        integrated_value = sum(integrate_curve(s, finish, df,x=x, y=y))
        guidict["data_area"] = integrated_value
        ix = xdata[s:finish]
        iy = ydata[s:finish]
        #print(integrated_value, '\n', ix, iy)
        v = df
        v = v[v["MHz"] > xmin]
        v = v[v["MHz"] < xmax]
        
        ax.annotate(
            "Data Area: " + str(round(integrated_value, 6)),
            xy=(xtxt, ypp - ys), xycoords='figure pixels'
        )
        
        verts = [[ix[0], 0],*zip(ix, iy),[ix[-1],0]]
        try:
            poly = Polygon(verts, facecolor='0.9', edgecolor='0.5')
            ax.add_patch(poly)
        except ValueError:
            #print("Signal Polygon shading Failed to draw for: ", filename)
            # HOTFIX:
            # TODO FIXME FIND out why this keeps "failing sucessfully".
            #   It's drawing the polygon, but complaining that it can't
            #   draw the polygon... WAT?
            pass
   
    try:
        if thermal_equalibrium_value:
            if b is not None and T is not None:
                TE_Val = tpol(b, T, mu=temu)
                #print(TE_Val, temu, b, T)
                guidict["TE_Value"] = TE_Val
            else:
                raise FileExistsError  # which just wont happen naturally here

            ax.annotate(
                "T-E Polarization (unscaled): " + str(
                    round(TE_Val, 6)
                ),
                xy=(xtxt, ypp - 2 * ys), xycoords='figure pixels'
            )

            if fitlorentzian:
                ax.annotate(
                    "Fit Calibration Constant: " + str( \
                        round(TE_Val / ltzian_integration, 6)
                    ),
                    xy=(xtxt + xtab, ypp),
                    xycoords='figure pixels'
                )
                guidict["fit_cal_constant"] = TE_Val / ltzian_integration
            if integrate:
                ax.annotate(
                    "Data Calibration Constant: " + str( \
                        round(TE_Val / integrated_value, 6)
                    ),
                    xy=(xtxt + xtab, ypp-2*ys),
                    xycoords='figure pixels'
                )
                guidict["data_cal_constant"] = TE_Val / integrated_value
    except FileExistsError:
        print("B and T were not declared, and the user requested the"
              "TE polarization value. Exception was thrown. Please double"
              "check the B and T entries in the GUI.")

    if redsig and not fitlorentzian:
        ax.scatter(
            xdata[s:finish], ydata[s:finish],
            c="r", s=2 * binning, label='Signal'
        )

    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    if xmin is not None and xmax is not None:
        ax.set_xlim(xmin, xmax)
    ax.legend(loc='best')
    guidict['fig'] = fig
    guidict['df'] = df
    if gui:
        return guidict
    plt.savefig(filename, dpi=dpi)
    if not noshow:
        plt.show()
