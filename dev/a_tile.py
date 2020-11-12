import requests

options = dict(zoom=0, xtile=0, ytile=0)


def synthesis(job):
	headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
	smurl = r"http://a.tile.openstreetmap.org/{zoom}/{xtile}/{ytile}.png"
	imgurl = smurl.format(**options)
	print("Opening: " + imgurl)
	imgstr = requests.get(imgurl, headers=headers)
	with job.open('tile.png', 'wb') as fh:
		fh.write(imgstr.content)
