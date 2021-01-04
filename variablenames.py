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
# In the DAQ csv, what is the time column labeled?
time_colname = "Time"
 
# What is the primary thermistor? 
primary_thermometer_colname = "CCX.T3 (K)"

# What is the secondary thermistor?
secondary_thermometer_colname = "Vapor Pressure Temperature (K)"

# What is the magnet PSU reading?
magnet_psu_amperage_colname = "Magnet Current (A)"

# What is the DAQ NMR Sweep centroid?
sweep_centroid_colname  = "Central Freq (MHz)"

# What is the DAQ NMR Sweep span?
sweep_width_colname = "Freq Span (MHz)"

# What is the NMR Status column?
system_status_colname = "NMR Status"

# What are the NMR Status entries that dont pertain to interesting
#	physics per the lab operator?
system_status_nulls = ['---']

# What directory do you want to place the status entries that dont matter? per line 44
system_null_status_directory = 'null_status'

# What column should I look for to be the terminal column to DAQ data, and begin searching for NMR
#	data? 
terminal_colname = 'NMR Data'