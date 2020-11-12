from datetime import datetime

# How many days the video should cover.  1 <= days <= 28,
# unless more files are downloaded.
days = 1


def main(urd):

	# Load background map from OpenStreetMap
	tiles = urd.build('osmtiles',
		lat=40.564, lon=-74.013,
		deltalat=0.30, deltalon=0.20, zoom=12,
		crop=((162, 103, 962, 1183)),
		resize=(667, 900),
	)
	tiles.link_result('map.png')

	# Import NYC COVID-19 statistics
	cases = urd.build('csvimport', filename='case-hosp-death.csv')
	cases = urd.build('dataset_type', source=cases, column2type=dict(
		DATE_OF_INTEREST='date:%m/%d/%Y',
		CASE_COUNT='number',
	))
	cases = urd.build('covidcases', source=cases)

	# Import and process zone polygons
	zones = urd.build('taxizones', filename='zones.json', tiles=tiles)

	# Create moving average for previous and current year
	ma = []
	for name, mindate, maxdate in (
			# offset in 2019/2020 dates since we want to compare mondays to mondays etc
			('previous', datetime(2019, 3, 3), datetime(2019, 3, 3 + days)),
			('current', datetime(2020, 3, 1), datetime(2020, 3, 1 + days))):
		impo = urd.peek('nyc', mindate.strftime('%Y-%m')).joblist.get(-1)
		print('Input dataset is "%s"' % (impo,))
		imp = urd.build('dataset_filter_columns', keep_columns=('stopdate10m', 'DOLocationID'), source=impo)
		imp = urd.build('dataset_hashpart', hashlabel='stopdate10m', source=imp, length=1)
		imp = urd.build('aggregate', source=imp, mindate=mindate, maxdate=maxdate)
		job = urd.build('movingaverage', source=imp, Nbins=6, name=name + '_ma')
		ma.append(job)
	jl = urd.joblist
	trend = urd.build('tripratio', left=jl.get('previous_ma'), right=jl.get('current_ma'))
	# render all this data into images and then into a movie
	job = urd.build('render', trend=trend, cases=cases, zones=zones, map_bg=tiles, ma=ma)
	job = urd.build('frames2mp4', source=job, framesname='frames_inorder/frame_%05d.jpg', framerate=60)
	job.link_result('out.mp4')

	# print(jl.print_exectimes())
