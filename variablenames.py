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
dm_time_colname = "Time"
 
# What is the primary thermistor? 
dm_primary_thermometer_colname = "CCX.T3 (K)"

# What is the secondary thermistor?
dm_secondary_thermometer_colname = "Vapor Pressure Temperature (K)"

# What is the magnet PSU reading?
dm_magnet_psu_amperage_colname = "Magnet Current (A)"

# What is the DAQ NMR Sweep centroid?
dm_sweep_centroid_colname  = "Central Freq (MHz)"

# What is the DAQ NMR Sweep span?
dm_sweep_width_colname = "Freq Span (MHz)"

# What is the NMR Status column?
dm_system_status_colname = "NMR Status"

# What are the NMR Status entries that dont pertain to interesting
#	physics per the lab operator?
dm_system_status_nulls = ['---']

# What directory do you want to place the status entries that dont matter? per line 44
dm_system_null_status_directory = 'null_status'

# What column should I look for to be the terminal column to DAQ data, and begin searching for NMR
#	data? 
dm_terminal_colname = 'NMR Data'