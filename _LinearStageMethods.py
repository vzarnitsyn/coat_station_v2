import gclib

def OpenLinearStage():
	g = gclib.py()
	g.GOpen('169.254.100.26 -s ALL')
	return g


def StepDMC(stepX = 0,stepY = 0,stepZ = 0):
	 #make an instance of the gclib python class
	speed = 25000
	acceleration = 60000
	trans_factor = 1.5875

	stx = stepX/trans_factor
	sty = stepY/trans_factor
	stz = stepZ/trans_factor
	acc = acceleration/trans_factor
	sp = speed/trans_factor
	
	try:
		g = OpenLinearStage() # at this point only opens fixed IP
		c = g.GCommand #alias the command callable
		c("ST;")
		c("AC " + str(acc) + ","+str(acc) + ","+str(acc) + ";")
		c("SP " + str(sp) + ","+str(sp) + ","+str(sp) + ";")
		c("PR " + str(stx) + ","+str(sty)+","+ str(stz)+"; BG;")
		
	except gclib.GclibError as e:
		print('Unexpected GclibError:', e)
	finally:
		g.GClose() #don't forget to close connections!

	return


def JoggDMC(vX = 0,vY = 0,vZ = 0):
	speed = 25000
	jog_speed = 150
	acceleration = 60000
	trans_factor = 1.5875

	acc = acceleration/trans_factor
	spx = vX*jog_speed/trans_factor
	spy = vY*jog_speed/trans_factor
	spz = vZ*jog_speed/trans_factor

	try:
		g = OpenLinearStage()
		c = g.GCommand #alias the command callable
		c("ST;")
		c("AC " + str(acc) + ","+str(acc) + ","+str(acc) + ";")
		c("JG " + str(spx) + ","+str(spy)+","+ str(spz)+"; BG;")
	except gclib.GclibError as e:
		print('Unexpected GclibError:', e)
	finally:
		g.GClose() #don't forget to close connections!
	return

def LinearStageSimpleCommand(textCommand):
	try:
		g= OpenLinearStage()
		c = g.GCommand #alias the command callable
		c(textCommand)
	except gclib.GclibError as e:
		print('Unexpected GclibError:', e)
	finally:
		g.GClose() #don't forget to close connections!
	return

def CurrentLinearStagePosition():
	try:
		g= OpenLinearStage()
		c = g.GCommand #alias the command callable
	  # set positions internally in controller (numbers cycled like 1 .. 49 50 1)
		xcur = float(c("MG _TPA"))  #if not corrected should be 'self.posx + self.x[self.currentN-1] - self.x[0]'
		ycur = float(c("MG _TPB"))  #if not corrected should be 'self.posx + x[self.currentN-1] - x[0]'
		zcur = float(c("MG _TPC"))  #if not corrected should be 'self.posx + x[self.currentN-1] - x[0]'
	except gclib.GclibError as e:
		print('Unexpected GclibError:', e)
		raise Exception('Could not get the coordinates!')
	finally:
		g.GClose() #don't forget to close connections!
	return xcur,ycur,zcur

def LinearStageToPosition(xabs,yabs,zabs):
	speed = 25000
	acceleration = 60000
	trans_factor = 1.
	acc = acceleration/trans_factor
	spd = speed/trans_factor
	try:
		g= OpenLinearStage()
		c = g.GCommand #alias the command callable
		c("AC " + str(acc) + "," + str(acc) + "," + str(acc) + ";")
		c("SP " + str(spd) + "," + str(spd) + "," + str(spd) + ";")
		c("PA " + str(int(xabs)) + "," + str(int(yabs)) + "," + str(int(zabs)) + ";")
		c("BG;")
	
	except gclib.GclibError as e:
		print('Unexpected GclibError:', e)
		raise Exception('can not  Linear motion')
	finally:
		g.GClose() #don't forget to close connections!
	return

def IsLinearStageOn():
	motor = 1.0
	try:
		g= OpenLinearStage()
		c = g.GCommand #alias the command callable
		motor = float(c("MG _MOA"))
	except gclib.GclibError as e:
		print('Unexpected GclibError:', e)
	finally:
		g.GClose() #don't forget to close connections!

	if motor < 0.01:
		return True

	return False


def LinearStageCodeExecute(fname):
		#self.label.setText("You Clicked The Button!")	
		# Open File Dialog
		
		if len(fname)<3 :
			return
	
		try:
			g= OpenLinearStage()
			g.GProgramDownloadFile(fname)
			g.GCommand("XQ")
			# disable all keys which can change needle position

		except gclib.GclibError as e:
			print('Unexpected GclibError:', e)
		finally:
			g.GClose()	
		return
