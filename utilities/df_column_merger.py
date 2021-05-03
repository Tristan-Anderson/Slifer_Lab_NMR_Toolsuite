"""
Tristan Anderson
Tristan.Anderson@unh.edu
"""
import pandas, os, numpy, datetime


def fetch_df(path, delimiter=','):
	try:
		with open(path, 'r') as f:
			df = pandas.read_csv(f, delimiter=delimiter)
		return df
	except FileNotFoundError:
		print("Can not find path")

def merger(primary_path:str, secondary_path:str, desired_columns:list, shared_column="time"):
	"""

	--> Primary path is the global analysis file produced by analyzing NMR spectra
	--> Secondary path is the raw-data file recorded by the DAQ.
	--> Desired columns is a list of columns that you want to MIGRATE from the 
			raw-data file INTO the global analysis file.

	--> Shared column needs to be some form of timestamp.

	"""
	primary_df = fetch_df(primary_path)
	print(primary_df)
	primary_df[shared_column] = pandas.to_datetime(primary_df['Time'], format="%Y-%m-%d %H:%M:%S")
	primary_df = primary_df.sort_values(by=shared_column)

	indexes_to_grab = primary_df.loc[:, shared_column]
	"""
		if you get an index error, double check the delimeter of 
		the secondary path (the DAQ csv). If you see things like:
		9830  12/7/2020 11:59:58 PM\t3690248398.062093\tOff\...
		in the print statement, then make sure the delimeter is correct

	"""
	############ begin problem child ####################
	secondary_df = fetch_df(secondary_path)#, delimiter='\t')
	#secondary_df = secondary_df.loc[:, ~secondary_df.columns.str.contains('^Unnamed')]
	############ End problem child ####################

	print(secondary_df)


	#### Subject of frequenct problems right here child right here:
	"""
		1) is the delimeter correct for primary/secondary dataframes correct?
			- If yes, but still get ValueError: time data doesn't match format
			----> Ensure format
			- if we STILL fail:
		2) Duplicate the secondary file on your hard-disk removing extrenuous columns
			using software like excel, or libre office.
		3) If that doesn't work: give up.

 	"""
	secondary_df[shared_column] = pandas.to_datetime(secondary_df['Time'], format="%m/%d/%Y %I:%M:%S %p")
	#if "Time" in secondary_df.columns.tolist():
	#	secondary_df.drop('Time', inplace=True;)
	#####
	secondary_df = secondary_df.sort_values(by=shared_column)

	print(primary_df)
	primary_df = primary_df.set_index(shared_column)
	secondary_df = secondary_df.set_index(shared_column)

	print(primary_df)
	for i in desired_columns:
		"""
			Using the intersection (subsection) of common timestamps
			in both the global analysis and raw-data dataframes
			Assign for each column in the global analysis dataframe,
			data we want to fetch from the raw-data dataframe.

			*Brain implodes* 
		"""
		primary_df.loc[primary_df.index.intersection(indexes_to_grab), i] = secondary_df.loc[secondary_df.index.intersection(indexes_to_grab), i]
	print(primary_df)
	return primary_df

def main_df_column_merger():

	primary_df = merger(\
			# Global analysis file
			"/home/kb/research/wdirs/NMR_Toolsuite/datasets/dec_2020/data_record_12-11-2020/video/global_analysis.csv",
			# Daq data file
			"/home/kb/research/wdirs/NMR_Toolsuite/datasets/dec_2020/rawdata/data_record_12-11-2020_abridged.csv",
			['CCS.F10 (K)','IFOFF (V)', 'Phase Tune (V)', 
			"Diode Tune (V)", "CCX.T3 (K)", "CCX.T1 (K)", 
			"SIG (V)", "UCA Voltage (V)", "Mmwaves Frequency (GHz)",
			"CCCS.T2 (K)", "CCS.F11 (K)"])

	with open("/home/kb/research/wdirs/NMR_Toolsuite/datasets/dec_2020/data_record_12-11-2020/video/global_analysis_2.csv", 'w') as f:
		primary_df.to_csv(f)
