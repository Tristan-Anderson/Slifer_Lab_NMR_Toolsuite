"""
Tristan Anderson
Tristan.Anderson@unh.edu
"""
import pandas, os, numpy, datetime


def fetch_df(path):
	try:
		with open(path, 'r') as f:
			df = pandas.read_csv(f)
		return df
	except FileNotFoundError:
		print("Can not find path")

def merger(primary_path:str, secondary_path:str, desired_columns:list, shared_column="time"):
	primary_df = fetch_df(primary_path)
	primary_df['time'] = pandas.to_datetime(primary_df['time'], format="%Y-%m-%d %H:%M:%S")
	primary_df = primary_df.sort_values(by=shared_column)
	indexes_to_grab = primary_df.loc[:, shared_column]
	secondary_df = fetch_df(secondary_path)
	secondary_df['time'] = pandas.to_datetime(secondary_df['time'], format="%m/%d/%Y %I:%M:%S %p")
	secondary_df = secondary_df.sort_values(by=shared_column)

	primary_df = primary_df.set_index(shared_column)
	secondary_df = secondary_df.set_index(shared_column)


	for i in desired_columns:
		primary_df.loc[indexes_to_grab, i] = secondary_df.loc[indexes_to_grab, i]

	return primary_df




primary_df = merger("global_analysis.csv", "datasets/dec_2020/rawdata/data_record_12-10-2020.csv",
		['CCS.F10 (K)','IFOFF (V)', 'Phase Tune (V)', "Diode Tune (V)", "CCX.T3 (K)", "CCX.T1 (K)", "SIG (V)", "UCA Voltage (V)", "Mmwaves Frequency (GHz)", "CCCS.T2 (K)", "CCS.F11 (K)"])

with open("global_analysis_2.csv", 'w') as f:
	primary_df.to_csv(f)