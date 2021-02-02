"""
Tristan Anderson
tja1015@wildcats.unh.edu

Proceed Formally.
"""

# Fortune:
"""
Is there life before breakfast?
"""

# Explanation:
"""
Mis-en-plas namespace that is imported by other modules of the NMR toolsuite
to supply variable and key names subject to change.

If you want to edit the primary and secondary thermistors - edit them here.

"""


####################################################################
"""
			 / \-----------------------------------, 
			 \_,|                                  | 
			    |    daq_muncher, sweep_averager   | 
			    |  ,---------------------------------
			    \_/________________________________/ 
"""
####################################################################
# In the DAQ csv, what is the time column labeled?
dmsa_time_colname = "Time"
 
# What is the primary thermistor? 
dmsa_primary_thermometer_colname = "CCX.T3 (K)"

# What is the secondary thermistor?
dmsa_secondary_thermometer_colname = "Vapor Pressure Temperature (K)"

# What is the magnet PSU reading?
dmsa_magnet_psu_amperage_colname = "Magnet Current (A)"

# What is the DAQ NMR Sweep centroid?
dmsa_sweep_centroid_colname  = "Central Freq (MHz)"

# What is the DAQ NMR Sweep span?
dmsa_sweep_width_colname = "Freq Span (MHz)"

# What is the NMR Status column?
dmsa_system_status_colname = "NMR Status"

# What are the NMR Status entries that dont pertain to interesting
#	physics per the lab operator?
dmsa_system_status_nulls = ['---']

# What directory do you want to place the status entries that dont matter? per line 44
dmsa_system_null_status_directory = 'null_status'

# What column should I look for to be the terminal column to DAQ data, and begin searching for NMR
#	data? 
dmsa_terminal_colname = 'NMR Data'
####################################################################
"""
			 / \---------------------, 
			 \_,|                    | 
			    |     NMR_Analyzer   | 
			    |  ,------------------
			    \_/__________________/ 
"""
####################################################################
na_primary_thermistor_name = dmsa_primary_thermometer_colname

na_secondary_thermistor_name = dmsa_secondary_thermometer_colname

na_vme_yaxis_default = "Potential (V)"

na_vme_xaxis_default = "MHz"

na_global_analysis_headers = ["name", "material", "time", "dtype", "blpath", "rawpath", "xmin",
               "xmax", "sigstart", "sigfinish", "blskiplines",
               'rawsigskiplines', "B", "T", dmsa_primary_thermometer_colname,
               dmsa_secondary_thermometer_colname,
               "TEvalue", "data_area", "ltzian_area",
               "data_cal_constant","ltzian_cal_constant", 'a', 'w', 'x0',
               "lorentzian chisquared (distribution)", "σ (Noise)", "σ (Error Bar)",
               "lorentzian relative-chisquared (error)",
               "Sweep Centroid", "Sweep Width", 'e_f0', 'e_w', 'e_kmax', 'e_theta']

####################################################################
"""
					  ___         ___  
					 (o o)       (o o) 
					(  V  ) gui (  V  )
					--m-m---------m-m--
"""
####################################################################
gui_primary_thermistor_name = dmsa_primary_thermometer_colname

gui_secondary_thermistor_name = dmsa_secondary_thermometer_colname
####################################################################
"""
					  ___              ___  
					 (o o)            (o o) 
					(  V  ) asciigui (  V  )
					--m-m--------------m-m--
"""
####################################################################
agui_primary_thermistor_name = dmsa_primary_thermometer_colname

agui_secondary_thermistor_name = dmsa_secondary_thermometer_colname

agui_allowable_file_extensions = ['.ta1', '.s1p']

agui_vnavme_default = 'vme'

agui_xname_default = na_vme_xaxis_default

agui_yname_default = na_vme_yaxis_default

agui_impression = False
