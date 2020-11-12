from PIL import Image, ImageFont
from PIL.ImageDraw import Draw
from os import mkdir
from accelerator import status

jobs = ('trend', 'cases', 'zones', 'map_bg', ['ma'])


def render_one(zone2poly, ddata, size):
	image = Image.new('RGBA', size=size)
	draw = Draw(image)
	for zoneix in ddata:
		if zoneix in zone2poly:
			dcount = ddata.get(zoneix, 0)
			intensity = round(2 * dcount)
			draw.polygon(zone2poly[zoneix], fill=(64, 255, 192, min(intensity, 150)))
	return image


SPACING = 20
BOX_WIDTH = 298


def prepare():
	mkdir('frames_inorder')
	trend = jobs.trend.load()

	map_bg = Image.open(jobs.map_bg.filename('crop.png'))
	map_size = map_bg.size

	# create background image
	total_width = (map_size[0] + SPACING) * 2 + SPACING * 2 + BOX_WIDTH
	bg = Image.new('RGB', (total_width, 1080), color=(40, 40, 40))
	draw = Draw(bg)
	gray64 = (64, 64, 64)
	gray192 = (192, 192, 192)
	fonts = {}
	def text(pos, msg, size, center=None):
		if size not in fonts:
			fonts[size] = ImageFont.truetype('DejaVuSans', size)
		if center:
			pos = ((center - draw.textsize(msg, font=fonts[size])[0]) // 2 + pos[0], pos[1])
		draw.text(pos, msg, font=fonts[size], fill=gray192, stroke_fill=gray64, stroke_width=1)
	text((SPACING, 90), "2019", size=60, center=map_size[0])
	text((SPACING + map_size[0] + SPACING, 90), "2020", size=60, center=map_size[0])
	x_start = (SPACING + map_size[0]) * 2 + SPACING
	y_start = 160
	def box(height, txt, txt2=None, size=None):
		nonlocal y_start
		draw.rectangle((x_start, y_start, x_start + BOX_WIDTH, y_start + height), fill=(100, 100, 100))
		text((x_start, y_start + (14 if size else 20)), txt, size=size or 40, center=BOX_WIDTH)
		if txt2:
			text((x_start, y_start + height - 40), txt2, size=size or 20, center=BOX_WIDTH)
		y_start += height + SPACING
	box(230, "DATE")
	box(180, "TIME")
	box(240, "DECREASE", "Num trips 2020/2019")
	box(190, "Confirmed Cases", "COVID-19 in NYC", size=30)
	text((SPACING, 0), "exax.org               New York City Yellow Cab COVID-19 Comparison", size=40)
	cases = jobs.cases.load()
	bg.paste(map_bg, (SPACING, 160))
	bg.paste(map_bg, (SPACING + map_size[0] + SPACING, 160))
	zone2poly = jobs.zones.load()
	ts2zone2cnts = [j.load()[0] for j in jobs.ma]
	assert {len(trend)} == set(len(v) for v in ts2zone2cnts)
	return trend, bg, cases, zone2poly, ts2zone2cnts, map_size


def analysis(sliceno, prepare_res, slices, job):
	trend, bg, cases, zone2poly, ts2zone2cnts, map_size = prepare_res
	ts2zone2cnts = [v[sliceno::slices] for v in ts2zone2cnts]
	fonts = {
		90: ImageFont.truetype('DejaVuSerif', 90),
	}
	gray64 = (64, 64, 64)
	gray192 = (192, 192, 192)
	x_start = (SPACING + map_size[0]) * 2 + SPACING
	def text(y_pos, msg, size=90, fill=gray192):
		if size not in fonts:
			fonts[size] = ImageFont.truetype('DejaVuSans', size)
		pos = ((BOX_WIDTH - draw.textsize(msg, font=fonts[size])[0]) // 2 + x_start, y_pos)
		draw.text(pos, msg, font=fonts[size], fill=fill, stroke_fill=gray64, stroke_width=1)
	ix = sliceno
	with status('rendering') as update:
		for (ts, am), (ts_l, left), (ts_r, right) in zip(trend[sliceno::slices], *ts2zone2cnts):
			assert ts == ts_r  # ts_l is ~1y earlier, not verified
			im1 = render_one(zone2poly, left, map_size)
			im2 = render_one(zone2poly, right, map_size)
			im = bg.copy()  # Image.new('RGB', (1920,1080))
			im.paste(im1, (20, 160), mask=im1)
			im.paste(im2, (20 + 667 + 20, 160), mask=im2)
			draw = Draw(im)

			date = ts
			text(610 + 80, "%2d%%" % (100 - round(100 * am),), fill=(255, 128, 64))
			text(410 + 70, date.strftime("%H:%M"))
			text(160 + 80, date.strftime("%a"), size=60)
			text(160 + 160, date.strftime("%B %d"), size=50)
			text(870 + 50, "%d" % (cases.get(date.date(), 1),), fill=(100, 160, 255))

			filename = 'frames_inorder/frame_%05d.jpg' % (ix,)
			im.save(filename)
			job.register_file(filename)
			ix += slices
			update('Rendered %d/%d frames.' % (ix // slices, len(ts2zone2cnts[0])))
