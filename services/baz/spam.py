import urllib2
import time
import random
import string

reqs = 0
timeacc = 0

while True:
	ts = time.time()

	url = 'http://localhost:4280/memorize?name=' + ''.join([random.choice(string.ascii_uppercase) for _ in range(5)]) + '&what=Bourbon'
	print(url)
	response = urllib2.urlopen(url)
	html = response.read()
	if not 'S' in html:
		raise Exception("FUCK BAD RESPONSE");

	delta = time.time() - ts

	reqs += 1
	timeacc += delta

	if reqs % 1000 == 0:
		avg = timeacc / reqs
		rate = 1 / avg
		print("avg: %.2fs, rate: %.2f/sec" % (avg, rate))