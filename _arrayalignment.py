import numpy as np
import pandas as pd
from _arraygenerator import GenerateArray50
from sklearn import linear_model
from sklearn.linear_model import LinearRegression

def ManualAlignmentArray():
	boolArray = np.array(np.zeros(50),dtype=bool) # generate array with all falses
	indexMan = [1,4,16,20,31,35,47,50] # 8 point alignment
	for i in indexMan:
		boolArray[i-1] = True
	return boolArray



def AlignmentCalculator(x,y,z,MnManAlign):
	xst,_,zst = GenerateArray50() # generate reference array using generate standard Array procedure
	# train linear regression model using x,y,z corrected by the user (flag MnManAlign == True)
	# generate training set
	# filter unused elements out
	if MnManAlign.sum() < 3: # non value of regression if less than 3 points are given
		return

	man_filter = MnManAlign
	xtrain = x[man_filter]
	ytrain = y[man_filter]
	ztrain = z[man_filter]
	xfix = xst[man_filter]
	zfix = zst[man_filter] # y st does not participate in the training as it is always 0
	xzfix = np.column_stack((xfix,zfix))

	# generate models
	modelx = LinearRegression().fit(xzfix, xtrain)
	modely = LinearRegression().fit(xzfix, ytrain)
	print('R2 score for y fit')
	print(modely.score(xzfix,ytrain))
	modelz = LinearRegression().fit(xzfix, ztrain)
	# it would be nice to assess the fit quality somehow

	# predict values
	for i in range(50) :
		if not man_filter[i]:
			x[i] = modelx.predict([[xst[i],zst[i]]])
			y[i] = modely.predict([[xst[i],zst[i]]])
			z[i] = modelz.predict([[xst[i],zst[i]]])
	return







	
