import subprocess

jobs = ('source',)

options = dict(framesname='images/frame_%5d.png', framerate=60)


def synthesis(job):
	print(jobs.source.filename(options.framesname), int(options.framerate))
	subprocess.run(['ffmpeg',
					'-f', 'image2',
					'-framerate', str(options.framerate),
					'-i', jobs.source.filename(options.framesname),
					'-c:v', 'libx264',
					'-preset', 'veryfast',
					'-profile:v', 'high',
					# '-bf', '2',
					# '-g', '30',
					# '-coder', '1',
					# '-crf', '27',
					# '-pix_fmt', 'yuv420p',
					'-cpu-used', '0',
					'out.mp4'])
	job.register_file('out.mp4')
