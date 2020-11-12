from collections import Counter, deque

jobs = ('source',)

options = dict(Nbins=15, source_column='routedmap')


class MovingSum:
	# N-tap moving sum
	def __init__(self, typ, n):
		self.bins = deque(typ() for x in range(n))
		self.val = typ()

	def update(self, new):
		self.val += new
		self.val -= self.bins.popleft()
		self.bins.append(new)
		return self.val


def synthesis():
	ma = MovingSum(Counter, options.Nbins)
	ma2 = MovingSum(float, 6 * 24)
	items = jobs.source.load()
	v = []
	s = []
	for ts, data in sorted(items):
		y = Counter({key: val / options.Nbins for key, val in ma.update(data).items()})
		v.append((ts, y))
		s.append((ts, float(ma2.update(sum(data.values())))))
	return v, s
