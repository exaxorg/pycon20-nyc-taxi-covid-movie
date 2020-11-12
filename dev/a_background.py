from os.path import join
import PIL.Image as Image
from PIL.ImageEnhance import Brightness

options = dict(filename='', size=(1024,1024))


def synthesis(job):
	image = Image.new('RGB', options.size)
	bg = Image.open(join(job.input_directory, options.filename)).convert('LA').convert('RGB')
	bg = Brightness(bg).enhance(0.5)
	image.paste(bg)
	return image
