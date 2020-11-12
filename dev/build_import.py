import re
from glob import glob
from os.path import join, basename

column2type = {
	'VendorID':              'int32_10',
	'tpep_pickup_datetime':  'datetime:%Y-%m-%d %H:%M:%S',
	'tpep_dropoff_datetime': 'datetime:%Y-%m-%d %H:%M:%S',
	'passenger_count':       'int32_10',
	'trip_distance':         'float32',
	'RatecodeID':            'int32_10',
	'store_and_fwd_flag':    'unicode:utf8',
	'PULocationID':          'int32_10',
	'DOLocationID':          'int32_10',
	'payment_type':          'int32_10',
	'fare_amount':           'float32',
	'extra':                 'float32',
	'mta_tax':               'float32',
	'tip_amount':            'float32',
	'tolls_amount':          'float32',
	'improvement_surcharge': 'float32',
	'total_amount':          'float32',
	'congestion_surcharge':  'float32',  # from 2020-01
}


def main(urd):
	urd.truncate('nyc', 0)

	files = glob(join(urd.info.input_directory, 'yellow_tripdata_*.csv'))

	last_imported = urd.peek_latest('nyc').timestamp
	for filename in sorted(map(basename, files)):
		ts = re.search(r'\d\d\d\d-\d\d', filename).group(0)
		if ts < '2016-07':
			continue  # In this project, we want the latest files only
		print('%s  \"%s\"' % (ts, filename,))
		if ts > last_imported:
			urd.begin('nyc', ts)
			prev = urd.latest('nyc').joblist
			imp = urd.build('csvimport',
				filename=filename,
				separator=',',
				skip_empty_lines=True,
				allow_extra_empty=True,
				previous=prev.get('csvimport'),
				allow_bad=False,
			)
			imp = urd.build('dataset_type', source=imp,
				column2type={key: column2type[key] for key in imp.dataset().columns.keys()},
				previous=prev.get('dataset_type'),
			)
			imp = urd.build('quant_timestamps', source=imp,
				previous=prev.get('quant_timestamps'),
			)
			urd.finish('nyc')
