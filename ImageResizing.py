from PIL import Image
from resizeimage import resizeimage
import os
import argparse

""" Usage python3 ImageResizing.py 
		--image_path h.png 
		--save_path x.png 
		--dimensions 200,200"""

class ImageResizing(object):
	"""docstring for ImageResizing"""
	def __init__(self):
		self.return_message ={'success':True, 'message': '', 'error': False, 'code': 0} 

	def image_resize(self, image_path, save_image_name, dimensions=[]):
		if not isinstance(dimensions, list): return {'message': 'It should be an array', 'code': 1, 'success': True}
		try:
			with open(image_path,'r+b') as f:
				with Image.open(f) as image:
					cover = resizeimage.resize_cover(image, dimensions)
					cover.save(save_image_name, image.format, validate=False)
			self.return_message['message'] = 'Image with name '+save_image_name+' has been saved.'
			return self.return_message['message']
		except Exception as e:
			self.return_message['message'] = 'Error has occured.'
			self.return_message['success'] = False
			self.return_message['error'] = True
			self.return_message['code'] = 2
			return self.return_message['message']

	def run(self):
		parser = argparse.ArgumentParser(description="Image resizing.")
		parser.add_argument("--image_path", help="Image of the name which is to be resized.")
		parser.add_argument("--dimensions", help="These are the dimensions, to which you need to resize it to.")
		parser.add_argument("--save_path", help="This the name of the file.")
		args = parser.parse_args()
		# print(args.image_path, args.save_path, args.dimensions, type(args.dimensions), type(args))
		if None in [args.image_path, args.save_path, args.dimensions]: 
			print('We cannot work on None values. Please provide us the values we are asking for. I think its not too much tp ask for.')
			return 0
		args.dimensions = list(map(int, args.dimensions.split(',')))
		print(self.image_resize(args.image_path, args.save_path, args.dimensions))

if __name__ == '__main__':
		ImageResizing().run()
