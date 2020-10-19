"""
Tristan Anderson
tja1015@wildcats.unh.edu

The Tree of learning bears the noblest fruit,
but noble fruit tastes bad.

Proceed Formally.
"""

# Omitted the correlative uncertainty in the calibration constant
# 	since the TE value and Area values both are dependent on T and B 

"""
TODO: Ship the toolsuite with a .ini so columnames can be generalized. 

TODO: Seperate the TE from the Enhanced routines. Condense TE error propogation

"""

import pandas, numpy
from scipy.stats import mode
import datetime
from matplotlib import pyplot as plt
from matplotlib import rc
plt.locator_params(axis='y', nbins=6)
font = {'size': 12}
rc('font', **font)


def report(number, sigfigs=3):
	# This reports significant figures
	# by exploiting the exponential format
	# since I could not find something prebuilt.
	formatstring = "{0:."+str(sigfigs)+"E}"
	string = str(float(formatstring.format(number)))
	return string

def deuterontepol(B,T):
	# Spin 1 TE Equation
	k = 1.38064852 * 10 ** -23
	
	gammad_over_2pi = 6.535902311 #MHz/T
	h_over_2kb=2.4*10**-5
	a=h_over_2kb*gammad_over_2pi
	x = a*B/T
	return 4*numpy.tanh(x)/(3+numpy.tanh(x)**2)

def pBdeuterontepol(B,T):
	# Partial derivative for uncert propogation
	# default Mu is for the proton
	
	k = 1.38064852 * 10 ** -23
	gammad_over_2pi = 6.535902311 #MHz/T
	h_over_2kb=2.4*10**-5
	a=h_over_2kb*gammad_over_2pi
	x = a*B/T
	return - 4*a*(numpy.tanh(x)**2-3)*(1/numpy.cosh(x)**2)/(T**2*(numpy.tanh(x)**2+3)**2)

def pTdeuterontepol(B,T):
	# Partial derivative for uncert propogation
	# default Mu is for the proton
	
	k = 1.38064852 * 10 ** -23
	gammad_over_2pi = 6.535902311 #MHz/T
	h_over_2kb=2.4*10**-5
	a=h_over_2kb*gammad_over_2pi
	x =a*B/T
	return 4*a*B*(numpy.tanh(x)**2-3)*(1/numpy.cosh(x)**2)/(T**2*(numpy.tanh(x)**2+3)**2)	

def tpol(b, t, mu = 1.4106067873 * 10 ** -26):
	# Spin 1/2 TE Equation
    k = 1.38064852 * 10 ** -23
    x = mu * b / (k * t)
    return numpy.tanh(x)

def pBtpol(b, t, mu = 1.4106067873 * 10 ** -26):
	# Partial derivative for uncert propogation
    # default Mu is for the proton
    k = 1.38064852 * 10 ** -23
    x = mu * b / (k * t)
    return - mu/(k*t)*1/(numpy.cosh(x))**2

def pTtpol(b, t, mu = 1.4106067873 * 10 ** -26):
	# Partial derivative for uncert propogation
    # default Mu is for the proton
    k = 1.38064852 * 10 ** -23
    x = mu * b / (k * t)
    return - mu*b/(k*t**2)*1/(numpy.cosh(x))**2

def collator(datapath, te=False, constant=1, home=None, deuteron=False, to_save = [], title=None, enforce_T3=False, enforce_VP=False, prevanalized=None, N=1):
	plt.clf()

	if prevanalized is None:
		# Prevanalized is a toggleable function that allows
		# 	for a tertiary analysis on a dataset that has
		# 	already been analyzed by the global_interpreter
		#
		#		this section is for a first, fresh dataset analysis.
		
		pltsave = "Enhanced_Results" if not te else "TE_Results"
		
		pltsave = title if title is not None else pltsave
		
		with open(datapath, 'r') as f:
				df = pandas.read_csv(f)	


		# Header from global_analysis files.
		rows_to_keep =["name", "time", "B", "ltzian_area", "data_area", "x0", "CCCS.T3 (K)", "Vapor Pressure (K)", "TEvalue"]
		mhz_to_b = 42.58

		rows_to_delete = []
		for column in df:
			if column not in rows_to_keep:
				rows_to_delete.append(column)

		# Pull out the data needed to do the analysis from our file.
		if not deuteron:
			y1 = df["x0"].values.astype(float)
			y1b = df["x0"].values.astype(float)/mhz_to_b
		y3 = df["ltzian_area"].values.astype(float)
		y3a = df["data_area"].values.astype(float)
		relative_error = df["lorentzian relative-chisquared (error)"].values.astype(float)
		t3y = df["CCCCS.T3 (K)"].values.astype(float)
		vpy = df["Vapor Pressure (K)"].values.astype(float)
		sweep_centroids = df["Sweep Centroid"].values.astype(float)
		sweep_width = df["Sweep Width"].values.astype(float)
		teval = df["TEvalue"].values.astype(float) # unscaled
		

	else:
		# Prevanalized is a toggleable function that allows
		# 	for a tertiary analysis on a dataset that has
		# 	already been analyzed by the global_interpreter
		#
		#		This is the portion for the tertiary analysis
		with open(prevanalized, 'r') as f:
			df = pandas.read_csv(f)
		y1a = df['B via I (T)'].values
		y1 = df["x0"].values.astype(float)
		#y1b = df["x0"].values.astype(float)/mhz_to_b
		y3 = df["Lorentzian Area"].values.astype(float)
		y3a = df["Integrated Data Area"].values.astype(float)
		t3y = df["CCCS.T3 (K)"].values.astype(float)
		vpy = df["VP (K)"].values.astype(float)
		sweep_centroids = df["sweep centroid"].values.astype(float)
		sweep_width = df["sweep width"].values.astype(float)

	df["time"] = pandas.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
	dt_for_dmy = df.loc[1, "time"]

	y,m,d = dt_for_dmy.strftime("%Y,%m,%d").split(',')
	print(y,m,d, "Enhanced" if te == False else "")

	results_df = pandas.DataFrame()
	results_df["time"] = df["time"]

	x = df["time"].values
	y1a = df['B'].values
	for index, val in enumerate(y1a):
		if val == 'Off':
			y1a[index] = 0
		else:
			y1a[index] = float(val)

	if enforce_T3:
		print("Enforcing T3 Value.")
		vpy = t3y
	if enforce_VP:
		print("Enforcing VP Value.")
		t3y = vpy

	y2 = (t3y+vpy)/2

	if te:
		# Begin calculating the thermal equalibrium polarization, and calibration constant 
		#	for the polarization area method based on NMR signal extraction.
		if not deuteron:
			if mode(teval)[0] == 0: # tanh(x) = 0 iff x=0. Here, x = uB/(kT) ==> B = 0 (we didn't get I for some reason from magnet PSU)
				bviax0 = y1b
				y1a = y1b
				constants = tpol(bviax0, y2)/y3*100
				viax0 = tpol(bviax0, y2) # average temperature that I average here, since the since global_analysis
			else:
				constants = teval/y3*100

			# Get the number of datapoints.
			N = numpy.mean([len(y1a), len(y1b), len(t3y), len(y3), len(vpy), len(y3a)])
			
			# Get the math in line for the calibration constant
			# 	and uncert propogation 
			B_x0_BEST = numpy.mean((y1a+y1b)/2)
			B_x0_UNCERT = numpy.std((y1a+y1b)/2)/(N)**.5
			print("B", report(B_x0_BEST), "±", report(B_x0_UNCERT))
			T_BEST = numpy.mean((t3y+vpy)/2)
			T_UNCERT = numpy.std((t3y+vpy)/2)/(N)**.5
			T_VAR = numpy.var((t3y+vpy)/2)/(N)**.5
			
			# This Bandaid fix for the issues of not having enough datapoints
			#	I have yet to develop a reasonable confidence interval on low count set.
			if N < 10 and T_VAR/2 > T_UNCERT:
				T_UNCERT = T_VAR/2

			print("T", report(T_BEST),"±", report(T_UNCERT))
			TE_BEST = tpol(B_x0_BEST, T_BEST)*100
			TE_UNCERT = (((pTtpol(B_x0_BEST, T_BEST)*T_UNCERT)**2+(pBtpol(B_x0_BEST, T_BEST)*B_x0_UNCERT)**2)**.5)*100
			print("TE", report(TE_BEST),"±", TE_UNCERT)
			A_BEST = numpy.mean((y3*0.7+y3a*.3))
			A_UNCERT = numpy.std((y3*0.7+y3a*.3))/(N)**.5
			print("Area", report(A_BEST),"±", report(A_UNCERT))
			CAL_BEST = TE_BEST/A_BEST
			CAL_UNCERT = ((CAL_BEST**2)*(A_UNCERT/A_BEST)**2+(CAL_BEST**2)*(TE_UNCERT/TE_BEST)**2)**.5
			
			print("Cal", report(CAL_BEST),"±", report(CAL_UNCERT), "(% Polarization / (Volt-area))")
			
			# Save the data
			results_df["B via x0 (T)"] = y1b
			results_df["Integrated Data Area"] = y3a
			results_df["Lorentzian Area"] = y3
			results_df["Scaled Polarization (%)"] = y3*const
		
		elif deuteron:
			if mode(teval)[0] == 0: # tanh(x) = 0 iff x=0. Here, x = uB/(kT) ==> B = 0 (we didn't get I for some reason from PSU)
				bviax0 = y1b
				y1a = y1b
				constants = deuterontepol(bviax0, y2a)/y3*100

			else:
				# Recalculate the TE equation  legacy analysis may have not always done it correctly.
				constants = deuterontepol(y1a, t3y)/y3a*100
			
			N = numpy.mean([len(y1a), len(t3y), len(y3a)])
			B_x0_BEST = numpy.mean(y1a)
			B_x0_UNCERT = numpy.std(y1a)/(N)**.5
			print("B", report(B_x0_BEST), "±", report(B_x0_UNCERT))
			T_BEST = numpy.mean(t3y)
			T_UNCERT = numpy.std(t3y)/(N)**.5
			T_VAR = numpy.var((t3y+vpy)/2)/(N)**.5
			
			# Haven't developed intelligent way to handle uncertainties. 
			if N < 10 and T_VAR/2 > T_UNCERT:
				T_UNCERT = T_VAR/2

			print("T", report(T_BEST),"±", report(T_UNCERT))
			TE_BEST = deuterontepol(B_x0_BEST, T_BEST)*100
			TE_UNCERT = (((pTdeuterontepol(B_x0_BEST, T_BEST)*T_UNCERT)**2+(pBdeuterontepol(B_x0_BEST, T_BEST)*B_x0_UNCERT)**2)**.5)*100
			print("TE", report(TE_BEST),"±", report(TE_UNCERT))
			A_BEST = numpy.mean(y3a)
			A_UNCERT = numpy.std(y3a)/(N)**.5
			print("Area", report(A_BEST),"±", report(A_UNCERT))
			CAL_BEST = TE_BEST/A_BEST
			

			CAL_UNCERT = ((CAL_BEST**2)*(A_UNCERT/A_BEST)**2+(CAL_BEST**2)*(TE_UNCERT/TE_BEST)**2)**.5
			print("Cal", report(CAL_BEST),"±", report(CAL_UNCERT), "(% Polarization / (Volt-area))")
	

		fig, ax = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(8.5, 11), constrained_layout=True)
		teinfo = [B_x0_BEST, B_x0_UNCERT, T_BEST, T_UNCERT, TE_BEST, TE_UNCERT, A_BEST, A_UNCERT, CAL_BEST, CAL_UNCERT]
		
		#ax[2].scatter(x,y3a, color="red")
		ax[2].errorbar(x,y3a, yerr=numpy.std(y3a)/(len(y3a))**.5, color="red")
		ax[2].set_ylabel("Data Area", color="red")
		#ax[2].set_ylim(-.01, .02)

	else:	
		# Propogate what happened earlier, forward onto this second "enhanced" dataset. to_save is a variable
		#	containing the results of the te handling
		B_x0_BEST, B_x0_UNCERT, T_BEST, T_UNCERT, TE_BEST, TE_UNCERT, A_BEST, A_UNCERT, CAL_BEST, CAL_UNCERT = to_save
		const = numpy.mean(constant) # This is passed to the function

		if deuteron:
			fig, ax = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(8.5, 11), constrained_layout=True)
			print("Max Pol", report(max(y3a)*CAL_BEST), "±", report(max(y3a)*CAL_UNCERT))
			print("Min Pol", report(min(y3a)*CAL_BEST), "±", report(min(y3a)*CAL_UNCERT))

			ax[2].errorbar(x,y3a*(CAL_BEST), yerr=y3a*(CAL_UNCERT),alpha=0.5, color='orange')
			ax[2].scatter(x,y3a*CAL_BEST, color='blue',zorder=2, s=2)

			# "BEST" is with uncert
			results_df["Scaled Polarization (%)"] = y3a*CAL_BEST
			results_df["Uncert in Scaled polarization"] = y3a*CAL_UNCERT
		
		else:
			fig, ax = plt.subplots(nrows=6, ncols=1, sharex=True, figsize=(8.5, 11), constrained_layout=True)

			ax[5].grid(True)
			ax[5].scatter(x,constants, label="Calibration Constants (Are Averaged)", color="peru")
			ax[5].set_ylabel("Calibration Constants",color="peru")
			tevaluesaxis = ax[5].twinx()
			vix0 = tpol(y1b, y2)


			tevaluesaxis.scatter(x, vix0, label="TE Value via x0", color="mediumpurple")
			tevaluesaxis.errorbar(x, [TE_BEST for i in x], yerr=TE_UNCERT, color='hotpink', alpha=0.5, label="TE w/ Error")
			tevaluesaxis.set_ylabel("TE Value",color="mediumpurple")
			tevaluesaxis.legend(loc='best')
			tevaluesaxis.set_yscale('symlog')

			results_df['TE via x0'] = vix0
			results_df["cal_constant"] = constants
			results_df['TEvalue'] = teval
			results_df["TE Best"] = TE_BEST
			results_df["TE Uncert"] = TE_UNCERT

			
			
			
			ax[2].errorbar(x, y3*CAL_BEST, yerr=y3*CAL_UNCERT, color="green")
			print("Max Pol", report(max(y3)*CAL_BEST), "±", report(max(y3)*CAL_UNCERT))
			print("Min Pol", report(min(y3)*CAL_BEST), "±", report(min(y3)*CAL_UNCERT))

			# This draws the green uncertainty-band for our polarization. It is generally
			#	Too thin to see without cranking up the chart's DPI.
			ax[2].errorbar(x,y3*(CAL_BEST-CAL_UNCERT), yerr=y3a*(CAL_UNCERT),alpha=0.5, color='orange')
			ax[2].scatter(x,y3*CAL_BEST, color='blue', zorder=2, s=2)

			# "BEST" is with uncert
			results_df["Scaled Polarization (%)"] = y3*CAL_BEST
			results_df["Uncert in Scaled polarization"] = y3*CAL_UNCERT

		ax[2].set_ylabel("Scaled Polarization (%)")
	
	# Begin ubiquitous stuff, and general useful data.
	fig.suptitle(y+" "+m+" "+d+" "+pltsave)
	
	ax[0].set_title("Magnetic Field Strength")
	ax[0].scatter(x,y1a, label="B via I (T)", color='purple')
	
	ax[0].set_ylabel("B via I (T)",  color='purple')
	ax[0].legend(loc='best')
	if not deuteron:
		bviagmr = ax[0].twinx()
		bviagmr.scatter(x,y1b, color='slateblue')
		bviagmr.set_ylabel("B via x0 (T)",  color='slateblue')

	
	ax[1].scatter(x,t3y, label="CCCS.T3 (K)", color="maroon")
	ax[1].scatter(x,vpy, label="Vapor Pressure (K)",color="orange")
	ax[1].set_ylabel('Kelvin')
	ax[1].legend(loc='best')

	ax[3].set_ylabel("MHz")
	ax[3].errorbar(x, sweep_centroids, yerr=sweep_width, label="Sweep Centroid + Width", alpha=0.45, color="orange")
	
	if deuteron:
		ax[0].grid(True)
		ax[1].grid(True)
		ax[2].grid(True)
		ax[3].grid(True)
		ax[3].legend(loc='best')

		if home is not None:
			plt.savefig(home+d+"_"+pltsave)
			if prevanalized is None:
				results_df["B via I (T)"] = y1a
				results_df["B via x0 (T)"] = None
				results_df["CCCS.T3 (K)"] = t3y
				results_df["VP (K)"] = vpy
				results_df["Integrated Data Area"] = y3a
				results_df["Lorentzian Area"] = y3
				results_df["Reduced Relative Chi-Square"] = relative_error
				results_df["x0"] = None
				results_df["sweep centroid"] = sweep_centroids
				results_df["sweep width"] = sweep_width
				with open(home+d+"_"+pltsave+".csv", 'w') as f:
					results_df.to_csv(f, index=False)
		else:
			plt.savefig(datapath+pltsave, dpi=300)
		if te:
			# List passing > typing lots
			return constants, teinfo
		return False
	
	else:
		results_df["B via I (T)"] = y1a
		results_df["CCCS.T3 (K)"] = t3y
		results_df["VP (K)"] = vpy
		results_df["Reduced Relative Chi-Square"] = relative_error
		results_df["x0"] = y1
		results_df["sweep centroid"] = sweep_centroids
		results_df["sweep width"] = sweep_width
		# A visual aid for how poorly the user is able to extract the lorentzian (;
		# A functional form that is better than the lorentzian is "Voight Curve"
		#	which is a curve that's a linear combination of the convolutions
		#	of a dominating lorentzian curve, and a secondary gaussian distribution

		ax[3].scatter(x, relative_error, label="Reduced Relative Chi-Square", color='peru')
		ax[3].set_yscale('logit')	# Not the BEST scale that I should be using. Please find an alternative.
		
		ax[4].scatter(x, y1, label="Lorentzian Centroid (x0)", color='green')
		ax[4].errorbar(x, sweep_centroids, yerr=sweep_width, label="Sweep Centroid + Width", alpha=0.45, color="orange")
		ax[4].errorbar(x, sweep_centroids, alpha=.45, color='orange')
		ax[4].grid(True)
		ax[4].legend(loc='best')

	ax[0].grid(True)
	ax[1].grid(True)
	ax[2].grid(True)
	ax[3].grid(True)
	ax[3].legend(loc='best')
	

	
	

	if home is not None:
		plt.savefig(home+d+"_"+pltsave)
		with open(home+d+"_"+pltsave+".csv", 'w') as f:
			results_df.to_csv(f, index=False)
	else:
		plt.savefig(datapath+pltsave, dpi=300)
	if te:
		return constants, teinfo
	return False



"""
Useage:

home= ""		# Where the interpreter will drop final results.
datapath = ""	# Where the TE global analysis csv is

# constants and teinfo are calibration parameters, and some statistics passed foward to the enhanced calculation
constants, teinfo = collator(datapath, d,m,y,te=True, home=home, title="TE d-Prop", deuteron=True)

datapath = ""	# Where the enhanced global analysis csv is
collator(datapath, home=home, constant=constants, to_save=teinfo, title="ENHANCED d-Prop", deuteron=True)
"""

