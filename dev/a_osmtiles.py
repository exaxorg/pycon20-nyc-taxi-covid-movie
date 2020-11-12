import math
from PIL import Image
from PIL.ImageEnhance import Brightness
from accelerator.subjobs import build

options = dict(lat=0.0, lon=0.0, deltalat=0.0, deltalon=0.0, zoom=0, crop=((0, 0, 0, 0)), resize=(0, 0))


# Based on code found here:
# https://stackoverflow.com/questions/28476117/easy-openstreetmap-tile-displaying-for-python


def deg2num(lat_deg, lon_deg, zoom):
	lat_rad = math.radians(lat_deg)
	n = 2.0 ** zoom
	xtile = int((lon_deg + 180.0) / 360.0 * n)
	ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
	return (xtile, ytile)


def num2deg(xtile, ytile, zoom):
	n = 2.0 ** zoom
	lon_deg = xtile / n * 360.0 - 180.0
	lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
	lat_deg = math.degrees(lat_rad)
	return (lat_deg, lon_deg)


def getImageCluster(lat_deg, lon_deg, delta_lat, delta_long, zoom):
	xmin, ymax = deg2num(lat_deg, lon_deg, zoom)
	xmax, ymin = deg2num(lat_deg + delta_lat, lon_deg + delta_long, zoom)
	size = ((xmax - xmin + 1) * 256 - 1, (ymax - ymin + 1) * 256 - 1)
	cluster = Image.new('RGB', size)
	for xtile in range(xmin, xmax + 1):
		for ytile in range(ymin, ymax + 1):
			t = build('tile', zoom=zoom, xtile=xtile, ytile=ytile)
			tile = Image.open(t.filename('tile.png'))
			cluster.paste(tile, box=((xtile - xmin) * 256, (ytile - ymin) * 255))
	return cluster, size, num2deg(xmin, ymin, zoom), num2deg(xmax + 1, ymax + 1, zoom)


def crop(im, size, topleft, bottomright, cropbox, resize):
	"""
	Input:
	  im          : image
	  size        : image (width, height) in pixels
	  topleft     : top left corner of image in GPS coordinates
	  bottomright : bottom right corner of image in GPS coordinates
	  cropbox     : (x1, y1, x2, y2) (in pixels) to crop from image
	  resize      : (width, height) in pixels of output image (resize of crop)
	"""
	im = im.crop(cropbox)
	width, height = size
	x1, y1, x2, y2 = cropbox
	lat1, lon1 = topleft
	lat2, lon2 = bottomright
	topleft = (lat2 - lat1) / height * y1 + lat1, (lon2 - lon1) / width * x1 + lon1
	bottomright = (lat2 - lat1) / height * y2 + lat1, (lon2 - lon1) / width * x2 + lon1
	im.thumbnail(resize, Image.ANTIALIAS)
	return im, resize, topleft, bottomright


def synthesis(job):
	im, size, topleft, bottomright = getImageCluster(options.lat, options.lon, options.deltalat, options.deltalon, options.zoom)
	filename = 'map.png'
	im.save(filename)
	job.register_file(filename)
	cropim, size, topleft, bottomright = crop(im, size, topleft, bottomright, options.crop, resize=options.resize)
	cropim = cropim.convert('LA').convert('RGB')
	cropim = Brightness(cropim).enhance(0.5)
	filename = 'crop.png'
	cropim.save(filename)
	job.register_file(filename)
	return size, topleft, bottomright
