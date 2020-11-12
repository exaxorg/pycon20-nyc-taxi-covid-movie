datasets = ('source',)


def synthesis(job):
	d = {}
	agg = 0
	for dt, x in datasets.source.iterate('roundrobin', ('DATE_OF_INTEREST', 'CASE_COUNT')):
		agg += x
		d[dt] = agg
	return d
