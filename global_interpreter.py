"""
Tristan Anderson
tja1015@wildcats.unh.edu

The Tree of learning bears the noblest fruit,
but noble fruit tastes bad.

Proceed Formally.
"""


import pandas, numpy
from scipy.stats import mode
import datetime
from matplotlib import pyplot as plt
from matplotlib import rc
plt.locator_params(axis='y', nbins=6)
#rc('font', )
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
#rc('font',**{'family':'serif','serif':['Times New Roman']})
#rc('text', usetex=True)


def deuterontepol(B,T):
	# The good-old fashioned thermal polarization eqn
	# 	thanks to the zeeman interaction (2j+1), derived from the 
	# 	Boltzmann law w/ j=1; or if you're really fancy
	# 	you can do the QM density operator for j=1
	# default Mu is for the proton
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
	# The good-old fashioned thermal polarization eqn
	# 	thanks to the zeeman interaction (2j+1), derived from the 
	# 	Boltzmann law w/ j=1/2
    # default Mu is for the proton
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

def collator(datapath, d,m,y, te=False, constant=1, home=None, deuteron=False, to_save = [], title=None, enforce_T3=False, enforce_VP=False, prevanalized=None, N=1):
	plt.clf()
	print(y,m,d, "Enhanced" if te == False else "")
	if prevanalized is None:
		if not te:
			pltsave = "Enhanced_Results"
			with open(datapath+"enhanced_global_analysis.csv", 'r') as f:
				df = pandas.read_csv(f)

		else:
			pltsave = "TE_Results"
			#with open(datapath+"global_analysis_ellie_requested.csv", 'r') as f:
			with open(datapath+"global_analysis.csv", 'r') as f:
				df = pandas.read_csv(f)

		if title is not None:
			pltsave = title

		# From global_analysis files.
		rows_to_keep =["name", "time", "B", "ltzian_area", "data_area", "x0", "CCCS.T3 (K)", "Vapor Pressure (K)", "TEvalue"]
		mhz_to_b = 42.58

		rows_to_delete = []
		for column in df:
			if column not in rows_to_keep:
				rows_to_delete.append(column)

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
	#print(df)
	df["time"] = pandas.to_datetime(df["time"], format="%Y-%m-%d %H:%M:%S")
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
		
		if not deuteron:
			if mode(teval)[0] == 0: # tanh(x) = 0 iff x=0. Here, x = uB/(kT) ==> B = 0 (we didn't get I for some reason from PSU)
				bviax0 = y1b
				y1a = y1b
				constants = tpol(bviax0, y2)/y3*100
				viax0 = tpol(bviax0, y2) # average temperature that I average here, since the since global_analysis
										 # 		is just .ta1 compction.
			else:
				constants = teval/y3*100

			N = numpy.mean([len(y1a), len(y1b), len(t3y), len(y3), len(vpy), len(y3a)])
			B_x0_BEST = numpy.mean((y1a+y1b)/2)
			B_x0_UNCERT = numpy.std((y1a+y1b)/2)/(N)**.5
			print("B", "{0:.8f}".format(B_x0_BEST), "±", "{0:.8f}".format(B_x0_UNCERT))
			T_BEST = numpy.mean((t3y+vpy)/2)
			T_UNCERT = numpy.std((t3y+vpy)/2)/(N)**.5
			print("T", "{0:.8f}".format(T_BEST),"±", "{0:.8f}".format(T_UNCERT))
			TE_BEST = tpol(B_x0_BEST, T_BEST)*100
			TE_UNCERT = (((pTtpol(B_x0_BEST, T_BEST)*T_UNCERT)**2+(pBtpol(B_x0_BEST, T_BEST)*B_x0_UNCERT)**2)**.5)*100
			print("TE", "{0:.8f}".format(TE_BEST),"±", TE_UNCERT)
			A_BEST = numpy.mean((y3*0.7+y3a*.3))
			A_UNCERT = numpy.std((y3*0.7+y3a*.3))/(N)**.5
			print("Area", "{0:.8f}".format(A_BEST),"±", "{0:.8f}".format(A_UNCERT))
			CAL_BEST = TE_BEST/A_BEST
			CAL_UNCERT = ((CAL_BEST**2)*(A_UNCERT/A_BEST)**2+(CAL_BEST**2)*(TE_UNCERT/TE_BEST)**2)**.5
			
			print("Cal", "{0:.8f}".format(CAL_BEST),"±", "{0:.8f}".format(CAL_UNCERT), "(% Polarization / (Volt-area))")
			
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
				#constants = teval/y3a*100
				constants = deuterontepol(y1a, t3y)/y3a*100
			
			
			N = numpy.mean([len(y1a), len(t3y), len(y3a)])
			B_x0_BEST = numpy.mean(y1a)
			B_x0_UNCERT = numpy.std(y1a)/(N)**.5
			print("B", "{0:.8f}".format(B_x0_BEST), "±", "{0:.8f}".format(B_x0_UNCERT))
			T_BEST = numpy.mean(t3y)
			T_UNCERT = numpy.std(t3y)/(N)**.5
			print("T", "{0:.8f}".format(T_BEST),"±", "{0:.8f}".format(T_UNCERT))
			TE_BEST = deuterontepol(B_x0_BEST, T_BEST)*100
			TE_UNCERT = (((pTdeuterontepol(B_x0_BEST, T_BEST)*T_UNCERT)**2+(pBdeuterontepol(B_x0_BEST, T_BEST)*B_x0_UNCERT)**2)**.5)*100
			print("TE", "{0:.8f}".format(TE_BEST),"±", "{0:.8f}".format(TE_UNCERT))
			A_BEST = numpy.mean(y3a)
			A_UNCERT = numpy.std(y3a)/(N)**.5
			print("Area", "{0:.8f}".format(A_BEST),"±", "{0:.8f}".format(A_UNCERT))
			CAL_BEST = TE_BEST/A_BEST
			

			CAL_UNCERT = ((CAL_BEST**2)*(A_UNCERT/A_BEST)**2+(CAL_BEST**2)*(TE_UNCERT/TE_BEST)**2)**.5
			print("Cal", "{0:.8f}".format(CAL_BEST),"±", "{0:.8f}".format(CAL_UNCERT), "(% Polarization / (Volt-area))")
	

		fig, ax = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(8.5, 11), constrained_layout=True)
		teinfo = [B_x0_BEST, B_x0_UNCERT, T_BEST, T_UNCERT, TE_BEST, TE_UNCERT, A_BEST, A_UNCERT, CAL_BEST, CAL_UNCERT]
		
		#ax[2].scatter(x,y3a, color="red")
		ax[2].errorbar(x,y3a, yerr=numpy.std(y3a)/(len(y3a))**.5, color="red")
		ax[2].set_ylabel("Data Area", color="red")
		#ax[2].set_ylim(-.01, .02)

	else:
		B_x0_BEST, B_x0_UNCERT, T_BEST, T_UNCERT, TE_BEST, TE_UNCERT, A_BEST, A_UNCERT, CAL_BEST, CAL_UNCERT = to_save
		const = numpy.mean(constant) # This is passed to the function

		if deuteron:
			fig, ax = plt.subplots(nrows=4, ncols=1, sharex=True, figsize=(8.5, 11), constrained_layout=True)
			print("Max Pol", "{0:.8f}".format(max(y3a)*CAL_BEST), "±", "{0:.8f}".format(max(y3a)*CAL_UNCERT))
			print("Min Pol", "{0:.8f}".format(min(y3a)*CAL_BEST), "±", "{0:.8f}".format(min(y3a)*CAL_UNCERT))

			# This draws the green uncertainty-band for our polarization. It is generally
			#	Too thin to see without cranking up the chart's DPI.
			#ax[2].fill_between(x,y3a*(CAL_BEST-CAL_UNCERT), y2=y3a*(CAL_BEST+CAL_UNCERT), color='black', alpha=0.3)
			ax[2].errorbar(x,y3a*(CAL_BEST), yerr=y3a*(CAL_UNCERT),alpha=0.5, color='orange')
			ax[2].scatter(x,y3a*CAL_BEST, color='blue',zorder=2, s=2)

			results_df["Scaled Polarization (%) (Errorless)"] = y3a*const  # ERRORLESS MEANS NO UNCERT PROPOGATION

			# "BEST" is with uncert
			results_df["Best Scaled Polarization (%)"] = y3a*CAL_BEST
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
			print("Max Pol", "{0:.8f}".format(max(y3)*CAL_BEST), "±", "{0:.8f}".format(max(y3)*CAL_UNCERT))
			print("Min Pol", "{0:.8f}".format(min(y3)*CAL_BEST), "±", "{0:.8f}".format(min(y3)*CAL_UNCERT))

			# This draws the green uncertainty-band for our polarization. It is generally
			#	Too thin to see without cranking up the chart's DPI.
			ax[2].fill_between(x,y3*(CAL_BEST-CAL_UNCERT), y2=y3*(CAL_BEST+CAL_UNCERT), color='black', alpha=0.3)
			ax[2].scatter(x,y3*CAL_BEST, color='black')

			results_df["Scaled Polarization (%) (Errorless)"] = y3*const  # ERRORLESS MEANS NO UNCERT PROPOGATION

			# "BEST" is with uncert
			results_df["Best Scaled Polarization (%)"] = y3*CAL_BEST
			results_df["Uncert in Scaled polarization"] = y3*CAL_UNCERT


		ax[2].set_ylabel("Scaled Polarization (%)")
	


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



d="14"
m="9"
y="2020"

home= "sep_2020/data_record_9-14-2020/700pte/final_results/"	# Where the interpreter will drop final results.

print("First Half")
datapath = "sep_2020/data_record_9-14-2020/700pte/7p_divided_TEs/first_half/"
constants, teinfo = collator(datapath, d,m,y,te=True, home=home, title="628p-630p TE d-Prop", deuteron=True)# N=5)

datapath = "sep_2020/data_record_9-14-2020/914_701a_to_915_405p_enhanced/graph_data/"
collator(datapath, "15",m,y, home=home, constant=constants, to_save=teinfo, title="628p-630p TE calibrated ENHANCED d-Prop", deuteron=True)

print("\nSecond Half")
datapath = "sep_2020/data_record_9-14-2020/700pte/7p_divided_TEs/2nd_half/"
constants, teinfo = collator(datapath, d,m,y,te=True, home=home, title="641p-650p TE d-Prop", deuteron=True)#18)

datapath = "sep_2020/data_record_9-14-2020/914_701a_to_915_405p_enhanced/graph_data/"
collator(datapath, "15",m,y, home=home, constant=constants, to_save=teinfo, title="641p-650p TE calibrated ENHANCED d-Prop", deuteron=True)


print("\nGrand Total")
datapath = "sep_2020/data_record_9-14-2020/700pte/7p_lab/"
constants, teinfo = collator(datapath, d,m,y,te=True, home=home, title="Grand Total TE d-Prop", deuteron=True)# N=5)

datapath = "sep_2020/data_record_9-14-2020/914_701a_to_915_405p_enhanced/graph_data/"
collator(datapath, "15",m,y, home=home, constant=constants, to_save=teinfo, title="Grand Total TE-calibrated ENHANCED d-Prop", deuteron=True)

