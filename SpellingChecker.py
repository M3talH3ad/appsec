from spellchecker import SpellChecker
from textblob import TextBlob
from textblob import Word

class SpellingChecker(object):
	"""docstring for SpellingChecker"""
	def __init__(self):
		self.spell = SpellChecker()
		

	def find_unknown(self, line=['something', 'is', 'hapenning', 'here']):
		if not isinstance(line, list): return {'error_code':1, "message": 'line is not an array'}
		misspelled = self.spell.unknown(line)
		_temp = {}
		for word in misspelled:
			res = self.spell.candidates(word)
			if isinstance(res, set): _temp[word] = res
		return _temp

	def read_file(self, filepath):
		f = open(filepath, 'r')
		line = f.readline()
		index = 1
		_temp = {}
		while line:
			print(line)
			words = self.toekenize(line)
			errors = self.find_unknown(words)
			if len(errors) > 0: _temp[index] = errors
			line = f.readline()
			index += 1
		return _temp
		f.close()

	def toekenize(self, line):
		return list(TextBlob(line).words)

a = SpellingChecker()
print(a.read_file('a.txt'))