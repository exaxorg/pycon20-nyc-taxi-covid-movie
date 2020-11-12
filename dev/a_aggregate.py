from collections import defaultdict, Counter
from datetime import datetime, timedelta

datasets = ('source',)

options = dict(mindate=datetime, maxdate=datetime)


def analysis(sliceno):
	mindate, maxdate = options.mindate, options.maxdate  # local var faster
	p = defaultdict(Counter)
	labels = ('stopdate10m', 'DOLocationID')
	for pt, pz in datasets.source.iterate_chain(sliceno, labels, hashlabel=labels[0]):
		if pt and mindate <= pt < maxdate:
			p[pt][pz] += 1
	return p


def synthesis(analysis_res):
	p = analysis_res.merge_auto()

	# Here, we fill in any missing timestamps
	p = sorted(p.items())
	item = p.pop(0)
	v = [item,]
	prev_ts = item[0]
	delta = timedelta(minutes=10)
	for ts, data in p:
		while ts - prev_ts > delta:
			prev_ts += delta
			v.append((prev_ts, {}))
		v.append((ts, data))
		prev_ts = ts
	return v
