from os.path import join
from itertools import groupby

options = dict(filename='',)
jobs = ('tiles',)


description = """
Read zone definitions and convert to polygons.

Polygons match the pixel coordinate system from the "tiles" input job.
"""


class GPS2pix:
	def __init__(self, size, topleft, bottomright):
		"""
		Input image width and height in pixles + corresponding top left
		and bottom right corners in (lat, lon) GPS coordinates.
		"""
		lat0, lon0 = topleft
		lat1, lon1 = bottomright
		self.xmag = size[0] / (lon1 - lon0)
		self.ymag = size[1] / (lat1 - lat0)
		self.lat = lat0
		self.lon = lon0

	def convert(self, lat, lon):
		return (lon - self.lon) * self.xmag, (lat - self.lat) * self.ymag


def synthesis(job):
	data = job.json_load(join(job.input_directory, options.filename))
	g = GPS2pix(*jobs.tiles.load())
	convert = g.convert
	ret = {}
	for ix, item in enumerate(data.features):
		objid = int(item.properties.objectid)
		coords = item.geometry.coordinates[0][0]
		# GPS coords -> pixel coords
		coords = tuple(convert(x[1], x[0]) for x in coords)
		# Remove overlapping consecutive polygon nodes
		coords = tuple(x[0] for x in groupby(coords))
		ret[objid] = coords
	return ret
