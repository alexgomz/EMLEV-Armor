'''
EMLEV Armor Raspberry Pi Code
Written by Alejandro Gomez

Uses a Raspberry Pi 3 running standard RaspianOS
Must have the Raspberry Camera attached
'''

import RPi.GPIO as IO
import time
import random
import os
import picamera
from datetime import datetime

#Pin Numberings
rConn = 7       #Riot Gear Connected
hConn = 11      #Gun Holster Connected
hSwitch = 13    #Gun Holster Switch
bSwitch = 15    #Baton Switch
fControl = 16   #Flahsligh Control
camControl = 40

#Global Variables
strobeValues = [0]
cameraRecordingBool = False

notPatrolMode = True
notRiotMode = True

patrolEvents = False
riotEvents = False
neutralEvents = False

gunCheckBool = False
emergencyGun = False
stopEmergencyGun = False

batonCheckBool = False
emergencyBaton = False
stopEmergencyBaton = False

EMERGENCY = False
cameraRecord = False
stopManualRecord = False
#state variable can have following states only: "NEUTRAL", "PATROL_MODE", "RIOT_MODE"
state = "NEUTRAL"

#Create objects
camera = picamera.PiCamera()
camera.resolution = '720p'
camera.rotation = 90
camera.framerate = 30

#Setup for GPIO pins
IO.setmode(IO.BOARD)
IO.setup(rConn, IO.IN, pull_up_down=IO.PUD_UP)
IO.setup(hConn, IO.IN, pull_up_down=IO.PUD_UP)
IO.setup(hSwitch, IO.IN, pull_up_down=IO.PUD_UP)
IO.setup(bSwitch, IO.IN, pull_up_down=IO.PUD_UP)
IO.setup(fControl, IO.OUT, initial=IO.LOW)
IO.setup(camControl, IO.IN, pull_up_down=IO.PUD_UP)

##################################################
#Main Connectors' Functions
def riotMode(rConn):
	global notRiotMode
	global state
	global patrolEvents
	notRiotMode = IO.input(rConn)
	if notRiotMode == False:
		state = "RIOT_MODE"
		riotEvents = True
		print("Riot Mode ON")
		patrolEvents = 1
	elif notRiotMode == True:
		state = "NEUTRAL"
		neutralEvents = True
		print("Riot Mode OFF")


def patrolMode(hConn):
	global notPatrolMode
	global state
	global patrolEvents
	global neutralEvents
	time.sleep(0.2)
	notPatrolMode = IO.input(hConn)
	#
	if state != "PATROL_MODE":
		if notPatrolMode == False:
			state = "PATROL_MODE"
			print("Patrol Mode ON")
			patrolEvents = True
	elif notPatrolMode == True:
		state = "NEUTRAL"
		neutralEvents = True
		print("Patrol Mode OFF")
		IO.output(fControl, IO.LOW)

##############################################################################
#Gun Holster Functions
def gunCheck(hSwitch):	
	global gunCheckBool
	global emergencyGun
	global stopEmergencyGun
	global EMERGENCY
	time.sleep(0.3)
	gunCheckBool = IO.input(hSwitch)
	print("hSwitch = %d" % gunCheckBool)
	if gunCheckBool == False:	#Gun deployed
		emergencyGun = True
		EMERGENCY = True
	elif gunCheckBool == True:
		stopEmergencyGun = True
		EMERGENCY = False


def gunOut():
	global camera
	global cameraRecordingBool
	timeStamp = datetime.now()
	fileName = "{0:%Y}-{0:%m}-{0:%d}--{0:%H}:{0:%M}:{0:%S}.h264".format(timeStamp)
	try:
		if cameraRecordingBool == False:
			print("recording started")
			IO.output(fControl, IO.HIGH)
			camera.start_recording("/media/camStorage/" + fileName)
			cameraRecordinBool = True
			return camera
		else:
			IO.output(fControl, IO.HIGH)
	except Exception:
		print("recording start (Exception)")
		camera.stop_recording()
		camera.start_recording("/media/camStorage/" + fileName)
		IO.output(fControl, IO.HIGH)

def gunIn():
	global camera
	try:
		camera.stop_recording()
		IO.output(fControl, IO.LOW)
		cameraRecordingBool = False
		print("recording stopped")
	except Exception:
		print("No recording in progress")


##############################################################################
#Baton Holster Functions

def batonCheck(bSwitch):
	global batonCheckBool
	global emergencyBaton
	global stopEmergencyBaton
	time.sleep(0.3)
	batonCheckBool = IO.input(bSwitch)
	print("bSwitch = %d" % batonCheckBool)
	if batonCheckBool == False:	#Baton deployed
		emergencyBaton = True
		EMERGENCY = True
	elif batonCheckBool == True:
		stopEmergencyBaton = True
		EMERGENCY = False


def batonOut():
	global camera
	global cameraRecordingBool
	timeStamp = datetime.now()
	fileName = "{0:%Y}-{0:%m}-{0:%d}--{0:%H}:{0:%M}:{0:%S}.h264".format(timeStamp)
	try:
		if cameraRecordingBool == False:
			print("recording started")
			camera.start_recording("/media/camStorage/" + fileName)
			cameraRecordingBool = True
			#strobeLight()
	except Exception:
		print("recording start (Exception)")
		camera.stop_recording()
		camera.start_recording("/media/camStorage/" + fileName)
	if state == "RIOT_MODE":
		os.system('play  "|rec --buffer 1024 -d pitch -300 echos 0.6 0.66 0.4 1 band 1.2k 1.5k"')
		
	
def batonIn():
	global camera
	try:
		camera.stop_recording()
		IO.output(fControl, IO.LOW)
		print("recording stopped")
		cameraRecordingBool = False
	except Exception:
		print("No recording in progress")
	
	if state == "RIOT_MODE":
		os.system("^C")

##############################################################################

def strobeLight():
	global strobeValues
	for x in range(0, len(strobeValues)):
		IO.output(fControl, IO.HIGH)
		time.sleep(strobeValues[x])
		IO.output(fControl, IO.LOW)
		time.sleep(strobeValues[x])


	IO.output(fControl, IO.LOW)

##############################################################################

def cameraControl(camControl):
	global camera
	global cameraRecord
	global EMERGENCY
	global stopManualRecord
	time.sleep(0.2)
	if EMERGENCY == False:
		cameraRecord =  IO.input(camControl)
		if cameraRecord == 1:
			stopManualRecord = False
		else:
			stopManualRecord = True
	
	
def manualRecord():
	global cameraRecordingBool
	global stopManualRecord
	global camera
	timeStamp = datetime.now()
	fileName = "MANUAL {0:%Y}-{0:%m}-{0:%d}--{0:%H}:{0:%M}:{0:%S}.h264".format(timeStamp)

	if cameraRecord:
		try:
			camera.start_recording("/media/camStorage/" + fileName)
			print("Recording")
			stopManualRecord = False
		except picamera.exc.PiCameraAlreadyRecording:
			print("Camera already recording. Continuing recording")
			
	elif cameraRecord == False:
		try:
			stopManualRecord = True
			camera.stop_recording()
			print("Recording stopped")
		except picamera.exc.PiCameraNotRecording:
			print("Camera not recording already")
	
		
	



#Connectors event detection(Always on, from the start)
IO.add_event_detect(hConn, IO.BOTH, callback=patrolMode, bouncetime=800)
IO.add_event_detect(rConn, IO.BOTH, callback=riotMode, bouncetime=800)
IO.add_event_detect(camControl, IO.BOTH, callback=cameraControl, bouncetime=800)

#Main Body of the Program
strobeValues = [0.1, 0.05, 0.1, 0.05, 0.1, 0.05, 0.05, 0.1, 0.08, 0.1, 0.08, 0.1, 0.05, 0.1, 0.1, 0.05, 0.1, 0.1, 0.05, 0.1, 0.08, 0.1]

try:
	while True:
		
		if state == "PATROL_MODE":
			while state == "PATROL_MODE":
				if patrolEvents == True:
					IO.remove_event_detect(hSwitch)
					IO.remove_event_detect(bSwitch)
					IO.add_event_detect(hSwitch, IO.BOTH, callback=gunCheck, bouncetime=800)
					IO.add_event_detect(bSwitch, IO.BOTH, callback=batonCheck, bouncetime=800)
					print("patrol events added")
					patrolEvents = False
				elif emergencyGun:
					IO.remove_event_detect(camControl)
					IO.remove_event_detect(bSwitch)
					emergencyGun = False
					gunOut()
					while stopEmergencyGun == False:
						try:
							camera.wait_recording(2)
						except Exception:
							print("No recording in progress")
							camera.start_recording("/media/camStorage/Exception Recording 1.h264")
					gunIn()
					stopEmergencyGun = False
					IO.add_event_detect(camControl, IO.BOTH, callback=cameraControl, bouncetime=800)
					IO.add_event_detect(bSwitch, IO.BOTH, callback=batonCheck, bouncetime=800)
				elif emergencyBaton:
					IO.remove_event_detect(camControl)
					emergencyBaton = False
					batonOut()
					strobeLight()
					while stopEmergencyBaton == False:
						try:
							camera.wait_recording(2)
						except Exception:
							print("No recording in progress")
							camera.start_recording("/media/camStorage/Exception Recording 2.h264")
					batonIn()
					stopEmergencyBaton = False
					IO.add_event_detect(camControl, IO.BOTH, callback=cameraControl, bouncetime=800)
				elif cameraRecord:
					manualRecord()
					while EMERGENCY == False and stopManualRecord == False:					
						camera.wait_recording(2)
					manualRecord()
					

		elif state == "NEUTRAL":
			while state == "NEUTRAL":
				if neutralEvents:
					neutralEvents = False
					IO.remove_event_detect(hSwitch)
					IO.remove_event_detect(bSwitch)
				elif cameraRecord:
					manualRecord()
					while EMERGENCY == False and stopManualRecord == False:
						camera.wait_recording(2)
						print("REC")
					manualRecord()
					
		elif state == "RIOT_MODE":
			while state == "RIOT_MODE":
				if riotEvents == True:
					riotEvents = False
					IO.add_event_detect(bSwitch, IO.BOTH, callback=batonCheck, bouncetime=800)
				elif emergencyBaton:
					IO.remove_event_detect(camControl)
					emergencyBaton = False
					batonOut()
					while stopEmergencyBaton == False:
						try:
							camera.wait_recording(2)
						except Exception:
							print("No recording in progress")
							camera.start_recording("/media/camStorage/Exception Recording 2.h264")
					batonIn()
					stopEmergencyBaton = False
					IO.add_event_detect(camControl, IO.BOTH, callback=cameraControl, bouncetime=800)					
				

except KeyboardInterrupt:
	IO.cleanup()
	camera.close()










