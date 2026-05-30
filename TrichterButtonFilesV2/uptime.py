import time
import datetime

start = datetime.datetime.now()

outFile = datetime.datetime.now().strftime("./upTime_%y-%m-%dT%H_%M_%S.log")

while True:
	file = open(outFile, "a")
	seconds = (datetime.datetime.now() - start).seconds
	output = "Still running after {} seconds\n".format(seconds)
	file.write("output")
	file.close()
	print(output)
	time.sleep(5)
