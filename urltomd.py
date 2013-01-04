import os
import yaml
import markdown

def trim_url(url):
	if url.startswith('/'):
		url = url[1:]
	if url.endswith('/'):
		url = url[:-1]
	return url

class Mapper(object):

	def __init__(self, path):
		if not os.path.isdir(path):
			return None
		if not path.endswith('/'):
			path += '/'
		self.path = path

	def exists(self, url):
		url = trim_url(url)
		return os.path.exists(self.path + url + '.md')

	def get(self, url):
		url = trim_url(url)
		if not self.exists(url):
			return None
		return Content(self, url)

	def create(self, url):
		url = trim_url(url)
		if self.exists(url):
			return False
		path = '/'.join(url.split('/')[:-1])
		if len(path) > 0 and not os.path.exists(self.path + path):
			os.makedirs(self.path + path)
		return Content(self, url)

class Content(object):

	def __init__(self, mapper, url):
		self.mapper = mapper
		self.url = url
		self.body = None
		self._meta = {}
		if os.path.exists(self._path()):
			self._read()

	def _read(self):
		"""Load the current state on the disk. If you use `_read`
		before you saved eventual changes with `_write` they will
		be lost."""
		with open(self._path()) as f:
			content = f.read().decode('utf8')
		content = content.split(u'\n\n')
		self._meta = yaml.load(content[0])
		self.body = '\n\n'.join(content[1:])

	def _write(self):
		"""Write the current state to the file."""
		with open(self._path(), 'w') as f:
			f.write(yaml.dump(self._meta, default_flow_style=False).encode('utf8'))
			f.write(u'\n')
			f.write(self.body.encode('utf8'))

	def _path(self):
		return self.mapper.path + self.url + '.md'

	@property
	def meta(self):
		return self._meta

	def __getitem__(self, item):
		return self.meta[item]

	@property
	def html(self):
		return markdown.markdown(self.body)

	def __html__(self):
		return self.html

	def save(self):
		self._write()

	def reload(self):
		self._read()