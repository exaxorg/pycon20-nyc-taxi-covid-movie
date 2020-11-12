from datetime import datetime, timedelta

description = '''
Clean and quantise timestamps to 10m/20m/1h/24h bins.

Create two new time columns per quantisation, "startdateQUANT" and
"stopdateQUANT", that are cleaned and quantised versions of
"pickup_datetime" and "dropoff_datetime", respectively.
Dates that do not make sense are written as "None".
'''


datasets = ('source', 'previous')


def prepare(job):
	dw = job.datasetwriter(previous=datasets.previous, parent=datasets.source)
	dw.add('startdate10m', 'datetime', none_support=True)
	dw.add('stopdate10m', 'datetime', none_support=True)
	return dw


def analysis(sliceno, prepare_res):
	dw = prepare_res
	mindate = datetime(2016, 7, 1)
	maxdate = datetime(2020, 12, 31)
	a_reasonable_duration = timedelta(hours=8)
	for tstart, tstop in datasets.source.iterate(sliceno, ('tpep_pickup_datetime', 'tpep_dropoff_datetime')):
		if maxdate >= tstop > tstart >= mindate and (tstop - tstart < a_reasonable_duration):
			dw.write(
				tstart.replace(second=0, minute=10 * (tstart.minute // 10)),
				tstop.replace(second=0, minute=10 * (tstop.minute // 10)),
			)
		else:
			dw.write(None, None)
