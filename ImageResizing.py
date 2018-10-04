from PIL import Image
from resizeimage import resizeimage
import os

class ImageResizing(object):
	"""docstring for ImageResizing"""
	# def __init__(self, dimensions):
	# 	# super(ImageResizing, self).__init__()
	# 	self.dimensions = dimensions		

	def image_resize(self, image_path, save_image_name, dimensions=[]):
		if not isinstance(dimensions, list): return {'message': 'It should be an array', 'code': 1, 'success': True}
		with open(image_path,'r+b') as f:
			with Image.open(f) as image:
				cover = resizeimage.resize_cover(image, [200, 200])
				cover.save(save_image_name, image.format, validate=False)

	def run(self):
		image_path = input('Enter the image path:\n')
		dimensions = input('Enter the dimensions:\n')
		dimensions = dimensions.split(',')
		save_path = input('Enter the path to where image is to be saved, with its name:\n')
		print(self.image_resize(image_path, save_path, dimensions))

ImageResizing().run()