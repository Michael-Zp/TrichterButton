import RPi.GPIO as GPIO
import datetime
import time
import simpleaudio
import os
import subprocess

#sound_file = "/home/michael/TrichterButtonFiles/Trichter.wav"
sound_file = "/home/michael/TrichterButtonFiles/EscapeRoomSongsMixed.wav"
sound_object = simpleaudio.WaveObject.from_wave_file(sound_file)
global play_object
play_object = None

trichter_button_pin = 10
volume_up_pin = 11
volume_down_pin = 12
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(trichter_button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(volume_up_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(volume_down_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def execute_bluetooth_command(command):
	return # DELETE ONLY FOR ESCAPE ROOM
	specified_command = "bluetoothctl <<< $'menu player\\n{}\\n'".format(command)
	print("Running {}".format(specified_command))
	os.system(specified_command)
	# bluetoothctl <<< $'menu player\n{}\n', command

def play_trichter():
	print("DU BIST VERHAFTET UND ANGEKLAGT! TRICHTERN IST ANGESAGT!")
	#os.system("/home/michael/TrichterButtonFiles/stop.sh > /dev/null")
	global play_object
	play_object = sound_object.play()
	# Wait for the player to start fully
	while play_object.is_playing() == False:
		time.sleep(0.01)

MAX_VOLUME = 150
MIN_VOLUME = 0
DEFAULT_VOLUME = 100

def get_volume():
	result = subprocess.check_output("pactl -- get-sink-volume 0", shell=True, text=True)
	splits = result.split('/')
	if len(splits) > 3:
		percentage = splits[3]
	else:
		print("Error in splitting volume console output")
		print(result)
		return None

	numberStr = percentage.split('%')[0]

	numberStr = numberStr.strip()

	try:
		volume = int(numberStr)
		print("Volume is currently {}%".format(volume))
		return volume
	except:
		print("Error in int conversion.")
		return None

def increase_volume():
	print("Trying to increase volume by 10%")
	volume = get_volume()
	if volume == None:
		print("Volume invalid")
		return

	if volume < MAX_VOLUME:
		if volume + 10 > MAX_VOLUME:
			volume = MAX_VOLUME
		else:
			volume = volume + 10
		os.system("pactl -- set-sink-volume 0 {}%".format(volume))
		print("Increasing volume to {}%".format(volume))
	else:
		print("Volume already at max. Not increasing")

def decrease_volume():
	print("Trying to decrease volume by 10%")
	volume = get_volume()
	if volume == None:
		print("Volume invalid")
		return

	if volume > MIN_VOLUME:
		if volume - 10 < MIN_VOLUME:
			volume = MIN_VOLUME
		else:
			volume = volume - 10
		os.system("pactl -- set-sink-volume 0 {}%".format(volume))
		print("Decreasing volume to {}%".format(volume))
	else:
		print("Volume already at min. Not decreasing")

def restore_trash():
	print("Going back to trash!")
	global play_object
	play_object.stop()
	play_object = None
	return # DELETE, ONLY FOR ESAPE ROOM
	os.system("/home/michael/TrichterButtonFiles/start.sh > /dev/null")

lastTrichterState = False
thisTrichterState = False
trichtering = False
lastButtonDownTime = None
buttonLongPressEnabled = False

lastVolumeUpState = False
thisVolumeUpState = False

lastVolumeDownState = False
thisVolumeDownState = False

stopFilePath = "/home/michael/TrichterButtonFiles/stop.stop"

while True:
	if os.path.isfile(stopFilePath):
		os.remove(stopFilePath)
		break

	if play_object != None and play_object.is_playing() == False and trichtering:
		print("Song ended. Back to trash.")
		trichtering = False
		restore_trash()
		lastButtonDownTime = time.time()
		buttonLongPressEnabled = False

	thisTrichterState = GPIO.input(trichter_button_pin) == GPIO.HIGH

	if not lastTrichterState and thisTrichterState:
		print("Button was pressed")
		# import ipdb; ipdb.set_trace();
		if not trichtering:
			play_trichter()
			trichtering = True
		else:
			lastButtonDownTime = time.time()
			buttonLongPressEnabled = True

	if lastTrichterState and not thisTrichterState:
		print("Button was released")

	if buttonLongPressEnabled:
		if lastTrichterState and thisTrichterState and trichtering:
			# Button is being held - don't print to prevent spam
			if (time.time() - lastButtonDownTime) > 3:
				print("Long press stopped trichtering.")
				restore_trash()
				trichtering = False
				buttonLongPressEnabled = False


	thisVolumeUpState = GPIO.input(volume_up_pin) == GPIO.HIGH
	thisVolumeDownState = GPIO.input(volume_down_pin) == GPIO.HIGH

	if not lastVolumeUpState and thisVolumeUpState:
		print("VolumeUp was pressed")
		increase_volume()

	if not lastVolumeDownState and thisVolumeDownState:
		print("VolumeDown was pressed")
		decrease_volume()

	lastVolumeUpState = thisVolumeUpState
	lastVolumeDownState = thisVolumeDownState

	lastTrichterState = thisTrichterState

	time.sleep(0.01)

GPIO.cleanup()

if trichtering:
	restore_trash()
