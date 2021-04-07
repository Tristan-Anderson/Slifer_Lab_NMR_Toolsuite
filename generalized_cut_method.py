import pandas, os,  multiprocessing, numpy, time, matplotlib
import numpy as np
from scipy.optimize import curve_fit as fit
from matplotlib import pyplot as plt

def get_karlmethod_generated(filename='utilities/saveme_9_14.csv'):
	with open(filename, 'r') as f:
		df = pandas.read_csv(f)
	x = 'time'
	y = 'sum'
	vv = [index for index,val in enumerate(df[x])]

	df[x] = pandas.to_datetime(df[x], format="%Y-%m-%d %H:%M:%S")
	df = df.sort_values(by=x)
	return df

def get_impression(df, title='9_14_2020 dataset'):
	x = 'time'
	y = 'sum'
	y1='leftmost'
	y2='rightmost'

	fig, ax = plt.subplots(ncols=3, figsize=(5.5, 5.5))

	fig.suptitle(title)

	v1 = (df[y1].values+df[y2].values)/2

	print(len(df[y1]))
	print(len(df[y2]))
	print(len(df[x]))

	ax[0].scatter(df[x], v1, label='Average')
	ax[0].grid(True)
	ax[0].legend(loc='best')

	ax[1].scatter(df[x], df[y1], label=y1)
	ax[1].scatter(df[x], v1, label=y2)
	ax[1].grid(True)
	ax[1].legend(loc='best')

	ax[2].set_title("Signal End Points")
	ax[2].grid(True)
	#ax[2].scatter(df[x], v1, label='Average')
	#ax[2].scatter(df[x], df[y1], label=y1)
	#ax[2].scatter(df[x], df[y2], label=y2)
	ax[2].scatter(df[x], df[y1]-df[y2], label=y1+'-'+y2)
	ax[2].legend(loc='best')

	

	


	"""
	ax[1].hist(df[y], bins=250)
	ax[1].set_title('histogram')
	ax[1].grid(True)


	ax[0].scatter(df[x], df[y], label='original dataset', color='blue')
	ax[0].set_title('karlmethod')

	ax[0].grid(True)
	ax[0].legend(loc='best')"""

	plt.show()
	input('ENTER to continue')


def main():

	df = get_karlmethod_generated()

	get_impression(df)

main()