import numpy as np

def GenerateArray50():
		x = np.zeros(68)
		y = np.zeros(68)
		z = np.zeros(68)
		
		stepx = 1834.3 /1.5875
		stepz = - 0.5*stepx
#
		for j in range(1,12):
		# make a row
			for i in range(1,6):
				x[(j-1)*6+1+i] = x[(j-1)*6+i] + stepx
				y[(j-1)*6+1+i] = y[(j-1)*6+i]
				z[(j-1)*6+1+i] = z[(j-1)*6+i]
			# step to next row
			x[(j-1)*6+1+6] = x[(j-1)*6+6] + stepx/2
			y[(j-1)*6+1+6] = y[(j-1)*6+6]
			z[(j-1)*6+1+6] = z[(j-1)*6+6] + stepz
		# change fill direction on x-axis
			stepx = -stepx
		# create a list of empty elements
		outlist = (0,1,6,7,19,26,29,31,32,34,36,38,41,43,55,61,66,67)
		for j in outlist:
			x[j] = -100000.0
			y[j] = -100000.0
			z[j] = -100000.0 # create unreasonably small value

		# filter unused elements out
		x_filter = x > -99999.0
		y_filter = y > -99999.0
		z_filter = z > -99999.0

		#x1 = list(filter(lambda x: x is not None, x))
		x1 = x[x_filter]
		#y1 = list(filter(lambda y: y is not None, y))
		y1 = y[y_filter]
		#z1 = list(filter(lambda z: z is not None, z))
		z1 = z[z_filter]

		return x1,y1,z1