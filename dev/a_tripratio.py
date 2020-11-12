jobs = ('left', 'right')


def synthesis():
	_, left = jobs.left.load()
	_, right = jobs.right.load()
	trend = list((ts, y / x or 0.1) for ((ts, x), (ts, y)) in zip(left, right))
	return trend
