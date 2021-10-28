from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel
from PyQt5.QtWidgets import QFileDialog, QRadioButton, QDoubleSpinBox
from PyQt5.QtCore import QTimer, QDateTime
from PyQt5 import uic
from PyQt5.Qt import Qt
from datetime import datetime
import sys
import string
import gclib
import numpy as np
import pandas as pd 
from _LinearStageMethods import StepDMC,JoggDMC,CurrentLinearStagePosition,LinearStageToPosition
from _LinearStageMethods import IsLinearStageOn,LinearStageSimpleCommand,LinearStageCodeExecute
from _arraygenerator import GenerateArray50
from _arrayalignment import AlignmentCalculator,ManualAlignmentArray


class UI(QMainWindow):
	def __init__(self):
		super(UI, self).__init__()
		
		
		# Load the ui file
		uic.loadUi("code_interface_v1_1.ui", self)

		# define constants and internal variables
		self.speed = 25000
		self.jog_speed = 150
		self.acceleration = 60000
		self.jump_interval = 200
		self.codeRunName=" "
		self.SecondsRunning = 0
		self.Jogg_Step = 1 # 1 means Jogg 0 means step
		self.MoveSpeed = 1 # 1 is low, 2 is medium, 3 is high
		self.IsInMotion = 0 # 0 means no, 1 means yes
		
		# generate mn positions
		self.x,self.y,self.z = GenerateArray50()
		self.NeedToAlignArray = ManualAlignmentArray()
		self.ManAlignArray = np.array(np.zeros(50),dtype=bool) # generate array with all falses
		# print(self.ManAlignArray)
		self.posx = 0
		self.posy = 0
		self.posz = 0
		self.currentN = 1 
		self.currentToAlign = 1
		self.cntManAlign = 8 

		# Define our widgets
		# define Timer widget (non visible)
		self.timer=QTimer()

		# Define radio buttons
		
		self.RadioButtonDMC_ON = self.findChild(QRadioButton,"Button_DCM_ON")
		self.RadioButtonDMC_OFF = self.findChild(QRadioButton,"Button_DCM_OFF")
		# Define speed selector radio buttons
		self.RadioButtonHighSpeed = self.findChild(QRadioButton,"HighSpeedRadioButton")
		self.RadioButtonMediumSpeed = self.findChild(QRadioButton,"MediumSpeedRadioButton")
		self.RadioButtonLowSpeed = self.findChild(QRadioButton,"LowSpeedRadioButton")
		self.RadioButtonDMC_OFF = self.findChild(QRadioButton,"Button_DCM_OFF")



		self.StopButton = self.findChild(QPushButton, "StopMotionButton")
		
		
# Define step/jogg widgets

		self.UpScreenStepButton = self.findChild(QPushButton, "Step_move_up_screen_button")
		self.DownScreenStepButton = self.findChild(QPushButton, "Step_move_down_screen_button")
		self.ForwardStepButton = self.findChild(QPushButton, "Step_move_forward_button")
		self.BackStepButton = self.findChild(QPushButton, "Step_move_back_button")
		self.UpStepButton = self.findChild(QPushButton, "Step_move_up_button")
		self.DownStepButton = self.findChild(QPushButton, "Step_move_down_button")
		self.BigStepForwardButton = self.findChild(QPushButton, "Step_move_forward_2_9_cm_button")
		self.BigStepBackButton = self.findChild(QPushButton, "Step_move_back_3_cm_button")


# define move parameters widgets
		self.RadioJoggButton = self.findChild(QRadioButton,"JoggRadioButton")
		self.RadioStepButton = self.findChild(QRadioButton,"StepRadioButton")
		self.RadioButton1000 = self.findChild(QRadioButton,"radioButton_1000um")
		self.RadioButton200 = self.findChild(QRadioButton,"radioButton_200um")
		self.RadioButton50 = self.findChild(QRadioButton,"radioButton_50um")
		self.RadioButton20 = self.findChild(QRadioButton,"radioButton_20um")		

# define functionss associated with step widgets

		self.UpScreenStepButton.clicked.connect(self.MoveUpScreenDMC)
		self.DownScreenStepButton.clicked.connect(self.MoveDownScreenDMC)
		self.ForwardStepButton.clicked.connect(self.MoveForwardDMC)
		self.BackStepButton.clicked.connect(self.MoveBackDMC)
		self.UpStepButton.clicked.connect(self.MoveUpScreenDMC)
		self.DownStepButton.clicked.connect(self.MoveDownScreenDMC)
		self.BigStepForwardButton.clicked.connect(lambda: self.LinearStageLinearMove(jogg = 0,sty=29000))
		self.BigStepBackButton.clicked.connect(lambda: self.LinearStageLinearMove(jogg = 0,sty=-30000))


		# Define mn alignment widgets
		self.ThisIsN1Button = self.findChild(QPushButton, "This_is_n1_Button")
		self.AcceptAndGoToNextButton = self.findChild(QPushButton, "Accept_and_Go_Button")
		self.GoToNextButton = self.findChild(QPushButton, "Go_to_next_Button")
		self.GoToN1Button = self.findChild(QPushButton, "Go_to_n1_Button")
		self.CurrentMNLabel = self.findChild(QLabel, "current_needle_label")
		self.CurrentCoatCycle = self.findChild(QLabel, "current_cycle_value")

		# define spin box and label for number of coats
		self.NumberOfCoatsSpinBox = self.findChild(QDoubleSpinBox, "Number_of_coats_SpinBox")

		#define alignment save and download buttons
		self.AlignmentDownloadButton = self.findChild(QPushButton, "DownloadAlignmentButton")
		self.AlignmentFilelabel = self.findChild(QLabel, "alignment_file_label")
		self.AlignmentSaveButton = self.findChild(QPushButton, "SaveAlignmentButton")


		#define script running buttons
		self.FileOpenButton = self.findChild(QPushButton, "File_Dialog_Button")
		self.OpenedFilelabel = self.findChild(QLabel, "code_file_label")
		self.CoordinatesDownloadButton = self.findChild(QPushButton, "Download_current_coordinates_Button")
		self.FileRunButton = self.findChild(QPushButton, "File_Run_Button")
		self.ExitButton = self.findChild(QPushButton, "Exit")


		# timer timeout label and signal action
		self.TimeLabel = self.findChild(QLabel, "TimeRunningSeconds")
		self.timer.timeout.connect(self.RegularUpdateTime)


		# RadioButtons actions
		self.RadioJoggButton.toggled.connect(self.set_Jog_Step)
		self.RadioButton1000.toggled.connect(self.selectIntervalChange)
		self.RadioButton200.toggled.connect(self.selectIntervalChange)
		self.RadioButton50.toggled.connect(self.selectIntervalChange)
		self.RadioButton20.toggled.connect(self.selectIntervalChange)
		self.RadioButtonDMC_ON.toggled.connect(self.selectOnOffChange)
		self.RadioButtonDMC_OFF.toggled.connect(self.selectOnOffChange)

		# set initial stage of MotorOn
		self.RadioButtonDMC_ON.setChecked(IsLinearStageOn())


		# Click The Buttons
		self.FileOpenButton.clicked.connect(self.FileOpenclicker)
		self.AlignmentDownloadButton.clicked.connect(self.AlignmentDownloadClicker)
		self.AlignmentSaveButton.clicked.connect(self.AlignmentSaveClicker)

		self.StopButton.clicked.connect(self.StopMotionClicker)

		self.ThisIsN1Button.clicked.connect(self.FixN1Position)
		self.GoToNextButton.clicked.connect(lambda: self.GoToNextPosition(dN = 1))
		self.AcceptAndGoToNextButton.clicked.connect(self.AcceptAndGoToNextPosition)
		self.GoToN1Button.clicked.connect(self.GoToN1Position)
		self.CoordinatesDownloadButton.clicked.connect(self.DownloadCoordinates)
		self.FileRunButton.clicked.connect(self.FileRun)
		self.ExitButton.clicked.connect(self.CloseProg)

		# change in SpinBox
		self.NumberOfCoatsSpinBox.valueChanged.connect(self.CoatNumberChanged)
		self.DownloadCoordinates()
		self.CoatNumberChanged()

		# define multipoint alignment labels and buttons
		self.MultiPointAlignAndGoButton = self.findChild(QPushButton, "ButtonAlignNAlignAndGoToNext")
		self.MultiPointGoBackButton = self.findChild(QPushButton, "ButtonAlignNGoBack")
		self.MultiPointGoForwardButton = self.findChild(QPushButton, "ButtonAlignNGoForward")
		self.CalculateAlignmentButton = self.findChild(QPushButton, "ButtonCalculateAlignment")
		self.DefaultAlignmentButton = self.findChild(QPushButton, "ButtonDefaultAlignment")
		self.JustAlignedMNLabel = self.findChild(QLabel, "labelJustAligned")
		

			# define functionss associated with multipoint alignment

		self.MultiPointAlignAndGoButton.clicked.connect(self.MultiPointAlignAndGoButtonClicked)
		self.MultiPointGoBackButton.clicked.connect(self.MultiPointGoBackButtonClicked)
		self.MultiPointGoForwardButton.clicked.connect(self.MultiPointGoForwardButtonClicked)
		self.CalculateAlignmentButton.clicked.connect(self.CallAlignmentCalculator)
		self.DefaultAlignmentButton.clicked.connect(self.DefaultAlignment)





		# Show The App
		self.show()

	def selectIntervalChange(self):
		if self.RadioButton20.isChecked():
			self.jump_interval = 20
		if self.RadioButton50.isChecked():
			self.jump_interval = 50
		if self.RadioButton200.isChecked():
			self.jump_interval = 200
		if self.RadioButton1000.isChecked():
			self.jump_interval = 1000

		
		return

	def selectOnOffChange(self):
		if IsLinearStageOn() and self.RadioButtonDMC_ON.isChecked():
			return
		elif (not IsLinearStageOn()) and self.RadioButtonDMC_OFF.isChecked():
			return

		try:
			if self.RadioButtonDMC_ON.isChecked():
				LinearStageSimpleCommand("SH")
			if self.RadioButtonDMC_OFF.isChecked():
				LinearStageSimpleCommand("MO")

		except :
			print('Unexpected Linear Stage Error')
		finally:
			return
		return


	def FileOpenclicker(self):
		#self.label.setText("You Clicked The Button!")	
		# Open File Dialog
		fname = QFileDialog.getOpenFileName(self, "Open File", "C:/Share/WorkingCoatingPrograms", "All Files (*);;Text Files (*.txt);; DMC Files (*.dmc)" )
		
		# Output filename to screen
		if fname:
			self.OpenedFilelabel.setText(fname[0])
			self.codeRunName = fname[0]


	def AlignmentDownloadClicker(self):
		#self.label.setText("You Clicked The Button!")	
		# Open File Dialog
		fname = QFileDialog.getOpenFileName(self, "Open File", "C:/py/alignments", "All Files (*);" )
		
		# Output filename to screen
		if fname:
			self.AlignmentFilelabel.setText(fname[0])
			df = pd.read_csv(fname[0])
			self.x = df[['0']].values.reshape(50)
			print(self.x.shape)
			self.y = df[['1']].values.reshape(50)
			self.z = df[['2']].values.reshape(50)


	def DefaultAlignment(self):
		# should be used with caution as ton of work is cancelled by this switch to default
		self.x,self.y,self.z = GenerateArray50()
		self.ManAlignArray = np.array(np.zeros(50),dtype=bool) # generate array with all falses
		return





	def AlignmentSaveClicker(self):
		fname = QFileDialog.getSaveFileName(self, 'Save Alignment',self.AlignmentFilelabel.text() , "Align Files (*.txt);;All Files (*)")
		if fname[0] == '':
			return
		if fname:
			self.AlignmentFilelabel.setText(fname[0])
			pd.DataFrame(np.vstack((self.x,self.y,self.z)).T).to_csv(fname[0])

		return
			

	def StopMotionClicker(self):
		try:
			LinearStageSimpleCommand("ST")
			self.IsInMotion = 0
		except:
			return
		
		self.ToggleButton()
		self.timer.stop()  
		return 

	def MoveUpScreenDMC(self):
		stx = -self.jump_interval
		vx = -1
		jogg = self.Jogg_Step
		self.LinearStageLinearMove(jogg = jogg, stx=stx,vx=vx)
		return

	def MoveDownScreenDMC(self):
		stx = self.jump_interval
		vx = 1
		jogg = self.Jogg_Step
		self.LinearStageLinearMove(jogg = jogg, stx=stx,vx=vx)
		return


	def MoveForwardDMC(self):
		sty = self.jump_interval
		vy = 1
		jogg = self.Jogg_Step
		self.LinearStageLinearMove(jogg = jogg, sty=sty,vy=vy)
		return

	def MoveBackDMC(self):
		sty = -self.jump_interval
		vy = -1
		jogg = self.Jogg_Step
		self.LinearStageLinearMove(jogg = jogg, sty=sty,vy=vy)
		return	

	def MoveUpDMC(self):
		self.LinearStageLinearMove(jogg = self.Jogg_Step, stz=-self.jump_interval,vz=-1)
		return

	def MoveDownDMC(self):
		self.LinearStageLinearMove(jogg = self.Jogg_Step, stz=self.jump_interval,vz=1)
		return
	
	def LinearStageLinearMove(self,jogg = 0,stx=0,sty=0,stz=0,vx=0,vy=0,vz=0):
			
			if self.IsInMotion == 1: # if it is already in motion - stop it
				self.StopMotionClicker()
				return

			if jogg == 1 : # jogg == 1
				if (vx*vx+vy*vy+vz*vz) > 0 :
					if self.RadioButtonLowSpeed.isChecked():
						vx,vy,vz = 0.5*vx,0.5*vy,0.5*vz
					if self.RadioButtonHighSpeed.isChecked():
						vx,vy,vz = 2*vx,2*vy,2*vz

					JoggDMC(vX = vx,vY = vy,vZ = vz)
					self.IsInMotion = 1
					return
			elif jogg == 0: # step
				self.IsInMotion = 1
				StepDMC(stepX = stx,stepY = sty,stepZ = stz)
				self.IsInMotion = 0
			return

			return





	def set_Jog_Step(self):
		if self.Jogg_Step == 1:
			 self.Jogg_Step = 0
		else:
			self.Jogg_Step = 1
		
		return




	# define KeyPress events (just stop for now)
	def keyPressEvent(self, event):
		
		if event.key() == Qt.Key_5:
			self.StopMotionClicker()
		if event.key() == Qt.Key_Space:
			self.StopMotionClicker()
		if self.IsInMotion == 1: 
			return

		if event.key() == Qt.Key_2:
			self.MoveDownScreenDMC()
		if event.key() == Qt.Key_8:
			self.MoveUpScreenDMC()
		if event.key() == Qt.Key_4:
			self.MoveBackDMC()
		if event.key() == Qt.Key_6:
			self.MoveForwardDMC()
		if event.key() == Qt.Key_Up:
			self.MoveUpDMC()
		if event.key() == Qt.Key_Down:
			self.MoveDownDMC()
		if event.key() == Qt.Key_9:
			self.MoveUpDMC()
		if event.key() == Qt.Key_3:
			self.MoveDownDMC()	
		if event.key() == Qt.Key_Q:
			self.GoToNextPosition(dN = 1)
		if event.key() == Qt.Key_Z:
			self.GoToNextPosition(dN = -1)
		if event.key() == Qt.Key_A:
			self.AcceptAndGoToNextPosition()
		if event.key() == Qt.Key_W:
			self.MultiPointGoForwardButtonClicked()
		if event.key() == Qt.Key_X:
			self.MultiPointGoBackButtonClicked()
		if event.key() == Qt.Key_S:
			self.MultiPointAlignAndGoButtonClicked()
		if event.key() == Qt.Key_Home:
			self.GoToN1Position()



	

	def FixN1Position(self):
		g = gclib.py()
		try:
		  g.GOpen('169.254.100.26 -s ALL') # at this point only opens fixed IP
		  c = g.GCommand #alias the command callable
		  # set positions internally in controller
		  c("posx=_TPA")
		  c("posy=_TPB")
		  c("posz=_TPC")
		  # read positions from the controller
		  self.posx = float(c("MG posx"))
		  self.posy = float(c("MG posy"))
		  self.posz = float(c("MG posz"))
		  self.CurrentMNLabel.setText("Current MN: "+"1")
		  self.AcceptAndGoToNextButton.setEnabled(True)
		  self.GoToNextButton.setEnabled(True)

		except gclib.GclibError as e:
			print('Unexpected GclibError:', e)
		finally:
		  g.GClose() #don't forget to close connections!
		return

	def GoToNextPosition(self,dN = 1):

		nextNeedle = self.currentN + dN
		if nextNeedle > 50:
			nextNeedle =  nextNeedle - 50
		if nextNeedle < 1:
			nextNeedle = nextNeedle + 50
		self.GoToNeedle(nextNeedle)

		return

	def AcceptAndGoToNextPosition(self):
		icur = self.currentN-1
		self.ManAlignArray[icur] = True
		# call current coordinates function
		try:
			xcur,ycur,zcur = CurrentLinearStagePosition()
			# set new positions if the return matches the tuple
			xnew = xcur + self.x[0] - self.posx
			ynew = ycur + self.y[0] - self.posy
			znew = zcur + self.z[0] - self.posx
		except Exception as e:
			print('No coordinates returned: ', e)
			self.ManAlignArray[icur] = False
			return

		self.x[icur] = xnew
		self.y[icur] = ynew
		self.z[icur] = znew

			
		if icur < 49:
			# correct y position based on current correction to minimize efforts
			if not self.ManAlignArray[icur+1]:
				self.y[icur+1] = self.y[icur]
			NextNeedleToAlign = icur + 2
		else:
			NextNeedleToAlign = 1
			
		self.GoToNeedle(NextNeedleToAlign)	
				
		return

	def GoToN1Position(self):
		self.currentN = 1
		self.CurrentMNLabel.setText("Current MN: "+str(self.currentN))
		LinearStageToPosition(self.posx,self.posy,self.posz)
		return

	def CoatNumberChanged(self):
				
		try:
		    # set positions internally in controller (numbers cycled like 1 .. 49 50 1)
			ncoat =  self.NumberOfCoatsSpinBox.value() 
			LinearStageSimpleCommand("cycleN=" + str(ncoat))

		except :
			print('UnExpected Linear Stage command')
		finally:
			return
		 
		return

	def DownloadCoordinates(self):
		now = datetime.now()
		dt_string = now.strftime("%m_%d_%Y_%H_%M__%S")
		filestring = "C:/py/coordinates/"+dt_string+".txt"
		f = open(filestring,"w+")
		print("DA*[]",file=f)
		print("DM X[51], Y[51], Z[51]",file=f)

		for i in range(50):
			print("X[" + str(i+1)+ "]=" + str(int(self.x[i])),file = f)
			print("Y[" + str(i+1)+ "]=" + str(int(self.y[i])),file = f)
			print("Z[" + str(i+1)+ "]=" + str(int(self.z[i])),file = f)
		f.close()

		try:
			LinearStageCodeExecute(filestring)
			self.FileRunButton.setEnabled(True)

		except :
			print('Download file execution error')
		finally:
			return
		return



	def GoToNeedle(self,nextNeedleToAlign):
		
		xabs = self.posx + self.x[nextNeedleToAlign-1] - self.x[0]
		yabs = self.posy + self.y[nextNeedleToAlign-1] - self.y[0]
		zabs = self.posz + self.z[nextNeedleToAlign-1] - self.z[0]
		try:
			LinearStageToPosition(xabs,yabs,zabs)
		
		except Exception as e:
			print('Needle :',str(nextNeedleToAlign),e)
			return

		self.currentN = nextNeedleToAlign
		self.CurrentMNLabel.setText("Current MN: "+str(self.currentN))	
		
		return	  


	def MultiPointAlignAndGoButtonClicked(self):
		# set current point as set
		self.JustAlignedMNLabel.setText("Just aligned :"+str(self.currentN)) 
		icur = self.currentN-1
		# call current coordinates function
		try:
			xabs,yabs,zabs = CurrentLinearStagePosition()
			# set new positions if the return matches the tuple
			xnew = xabs + self.x[0] - self.posx
			ynew = yabs + self.y[0] - self.posy
			znew = zabs + self.z[0] - self.posx
			self.ManAlignArray[icur] = True
		except Exception as e: # 
			print('Did not get coordinates for assignment :', e)
			return
			
		self.x[icur],self.y[icur],self.z[icur] = xnew,ynew,znew
				
		# find next position to adjust next True element of needToAlign or the first element
		
		if icur < 49:
			for i in range(icur+1,50):
				if self.NeedToAlignArray[i]:
					NextNeedleToAlign = i+1
					break
		else:
			NextNeedleToAlign = 1

		self.GoToNeedle(NextNeedleToAlign)
		return




		return

	def MultiPointGoBackButtonClicked(self):
		# set current point as set 
		icur = self.currentN-1
			
		# find prior position to go to next True element of needToAlign or the first element
		
		if icur >0:
			for i in range(icur-1,-1,-1):
				if self.NeedToAlignArray[i]:
					NextNeedleToAlign = i+1
					break
		else:
			NextNeedleToAlign = 50
		
		self.GoToNeedle(NextNeedleToAlign)
		return

	def MultiPointGoForwardButtonClicked(self):
		# set current point as set 
		icur = self.currentN-1
			
		# find next position to go to next True element of needToAlign or the first element
		
		if icur < 49:
			for i in range(icur+1,50):
				if self.NeedToAlignArray[i]:
					NextNeedleToAlign = i+1
					break
		else:
			NextNeedleToAlign = 1
		
		self.GoToNeedle(NextNeedleToAlign)
		return

	def CallAlignmentCalculator(self):
		AlignmentCalculator(self.x,self.y,self.z,self.ManAlignArray)
		return	

	def ToggleButton(self, boolStatus = True):
		self.UpScreenStepButton.setEnabled(boolStatus)
		self.DownScreenStepButton.setEnabled(boolStatus)
		self.ForwardStepButton.setEnabled(boolStatus)
		self.BackStepButton.setEnabled(boolStatus)
		self.UpStepButton.setEnabled(boolStatus)
		self.DownStepButton.setEnabled(boolStatus)
		
		self.ThisIsN1Button.setEnabled(boolStatus)
		self.GoToNextButton.setEnabled(boolStatus)
		self.AcceptAndGoToNextButton.setEnabled(boolStatus)
		self.GoToN1Button.setEnabled(boolStatus)
		self.CoordinatesDownloadButton.setEnabled(boolStatus)
		self.BigStepBackButton.setEnabled(boolStatus)
		if boolStatus == False:
			self.BigStepForwardButton.setEnabled(boolStatus)



	def FileRun(self):
		#self.label.setText("You Clicked The Button!")	
		# Open File Dialog
		fname = self.OpenedFilelabel.text()
		try:
			LinearStageCodeExecute(fname)
			# disable all keys which can change needle position
			self.ToggleButton(False)
			self.SecondsRunning = 0
			self.timer.start(1000)
			self.IsInMotion = 1

		except:
			print('Unexpected FileRunError')
		finally:
			return
		return

	def RegularUpdateTime(self):
		self.SecondsRunning += 1
		self.TimeLabel.setText(str(self.SecondsRunning))
		g = gclib.py()
		try:
			g.GOpen('169.254.100.26 -s ALL') # at this point only opens fixed IP
			cur_cycle = g.GCommand("MG cycle+1")
			cur_n = g.GCommand("MG n")
			
		except gclib.GclibError as e:
			print('Unexpected GclibError:', e)
		finally:
			g.GClose()
		self.CurrentCoatCycle.setText("Coat cycle :"+ cur_cycle)
		self.CurrentMNLabel.setText("Coating mn #: "+ cur_n)
		if float(cur_cycle) > self.NumberOfCoatsSpinBox.value():
			self.timer.stop()
			self.CurrentCoatCycle.setText("Program stopped after :"+ cur_cycle+ "cycles")
			self.ToggleButton()

		return

	def CloseProg(self):
		sys.exit()
		
           		

def main():
	# Initialize The App
	app = QApplication(sys.argv)
	UIWindow = UI()
	app.exec_()

main()