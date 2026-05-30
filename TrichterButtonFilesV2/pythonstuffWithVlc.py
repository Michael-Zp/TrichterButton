import RPi.GPIO as GPIO
import datetime
import time
import vlc
import os

vlcPlayer = vlc.MediaPlayer("file:///home/michael/TrichterButtonFiles/Trichter.mp3")

pin = 10

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def execute_bluetooth_command(command):
	specified_command = "bluetoothctl <<< $'menu player\\n{}\\n'".format(command)
	print("Running {}".format(specified_command))
	os.system(specified_command)
	# bluetoothctl <<< $'menu player\n{}\n', command

def play_trichter():
	print("DU BIST VERHAFTET UND ANGEKLAGT! TRICHTERN IST ANGESAGT!")
	os.system("/home/michael/TrichterButtonFiles/stop.sh > /dev/null")
	vlcPlayer.play()
	# Wait for the player to start fully
	while vlcPlayer.is_playing() == 0:
		time.sleep(0.01)

def restore_trash():
	print("Going back to trash!")
	vlcPlayer.pause()
	os.system("/home/michael/TrichterButtonFiles/start.sh > /dev/null")
	vlcPlayer.set_position(0.0)

lastState = False
thisState = False
trichtering = False
lastButtonDownTime = None
buttonLongPressEnabled = False

stopFilePath = "/home/michael/TrichterButtonFiles/stop.stop"

while True:
	if os.path.isfile(stopFilePath):
		os.remove(stopFilePath)
		break

	if vlcPlayer.is_playing() == 0 and trichtering:
		print("Song ended. Back to trash.")
		trichtering = False
		restore_trash()
		lastButtonDownTime = time.time()
		buttonLongPressEnabled = False

	if GPIO.input(pin) == GPIO.HIGH:
		thisState = True
	else:
		thisState = False

	if not lastState and thisState:
		print("Button was pressed")
		if not trichtering:
			play_trichter()
			trichtering = True
		else:
			lastButtonDownTime = time.time()
			buttonLongPressEnabled = True

	if lastState and not thisState:
		print("Button was released")

	if buttonLongPressEnabled:
		if lastState and thisState and trichtering:
			# Button is being held - don't print to prevent spam
			if (time.time() - lastButtonDownTime) > 3:
				print("Long press stopped trichtering.")
				restore_trash()
				trichtering = False
				buttonLongPressEnabled = False



	lastState = thisState

	time.sleep(0.01)

GPIO.cleanup()

if trichtering:
	restore_trash()
