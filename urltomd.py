import os
import yaml
import misaka
from exceptions import IOError

class Content(object):

	def __init__(self, root, path):
		self.root = root
		self.path = path
		self.body = None
		self._meta = {}
		if os.path.exists(self.full_path()):
			self.read()

	def __repr__(self):
		if self.meta.get('Title'):
			return "<Content object '%s' at '%s.md'>" % \
				(self.meta.get('Title'), self.path)
		return "<Content object at '%s.md'>" % self.path

	def read(self):
		"""Load the current state on the disk. If you use `read`
		before you saved eventual changes with `write` they will
		be lost."""
		with open(self._full_path()) as f:
			content = f.read().decode('utf8')
		content = content.split(u'\n\n')
		meta = self.load_meta(content[0])
		if not isinstance(meta, dict):
			meta = {}
		self._meta = meta
		self.body = '\n\n'.join(content[1:])

	def write(self):
		"""Write the current state to the file."""
		with open(self.full_path(), 'w') as f:
			f.write(self.dump_meta(self.meta))
			f.write(u'\n')
			f.write(self.body.encode('utf8'))

	def full_path(self):
		return self.root + self.path + '.md'

	def _url(self):
		"""This one can be overwritten by subclasses, if they want
		to manually pretend to have a different url."""
		return '/' + self.path + '/'

	def load_meta(self, meta):
		return yaml.safe_load(meta)

	def dump_meta(self, meta):
		return yaml.safe_dump(self._meta,
			default_flow_style=False).encode('utf8')

	def render(self, body):
		return misaka.html(body)

	@property
	def url(self):
		return self.url()

	@property
	def meta(self):
		return self._meta

	def __getitem__(self, item):
		return self.meta[item]

	@property
	def html(self):
		return self.render(self.body)

	def __html__(self):
		return self.html

	def save(self):
		self.write()

	def reload(self):
		self.read()

class Mapper(object):

	def __init__(self, path=None, contentclass=Content):
		self.contentclass = contentclass
		if path:
			self.init_path(path)

	def init_path(self, path):
		if not os.path.isdir(path):
			raise IOError('%s does not exist or is not a directory.'
				% path)
		if not path.endswith('/'):
			path += '/'
		self.path = path

	def exists(self, path):
		path = path.strip('/')
		return os.path.exists(self.path + path + '.md')

	def get(self, path):
		path = path.strip('/')
		if not self.exists(path):
			return None
		return self.contentclass(self.path, path)

	def create(self, path):
		path = path.strip('/')
		if self.exists(path):
			return False
		directory = '/'.join(path.split('/')[:-1])
		if len(directory) > 0 and not os.path.exists(self.path + directory):
			os.makedirs(self.path + path)
		return self._get(path)

	def delete(self, path):
		path = path.strip('/')
		if not os.path.exists(self.path + path + '.md'):
			return False
		os.remove(self.path + path + '.md')
		return True

	def _list(self, subdirectory=None):
		def _walk(directory, path_prefix=()):
			for name in os.listdir(directory):
				fullname = os.path.join(directory, name)
				if os.path.isdir(fullname):
					_walk(fullname, path_prefix + (name,))
				elif name.endswith('.md'):
					path = u'/'.join(path_prefix + (name[:-3],))
					if subdirectory:
						path = u'/'.join([subdirectory, path])
					element = self._get(path)
					elements[element.url] = element
		elements = {}
		if subdirectory:
			_walk(self.path + subdirectory)
		else:
			_walk(self.path)
		return elements

	@property
	def contents(self):
		"""This property will return a full list of all contents
		with their path paths. As this has to index the whole
		directory every time it is run, it can be very slow on
		bigger collections and should be used carefully."""
		return self._list()

	def subcontents(self, path):
		path = path.strip('/')
		"""Get all contents that start with the given path. This
		will only work is the path is the full part before a
		slash, which means all contents will be stored in one
		directory and its subdirectories."""
		if not os.path.isdir(self.path + path):
			return None
		return self._list(path)