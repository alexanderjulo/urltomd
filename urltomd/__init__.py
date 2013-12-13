import os
import yaml
import misaka
from exceptions import IOError


class Content(object):

    def __init__(self, root, url, path):
        self.root = root
        self._url = url
        self.path = path
        self.body = None
        self._meta = {}
        if os.path.exists(self.full_path()):
            self.read()

    def __repr__(self):
        if self.meta.get('Title'):
            return "<Content object '%s' at '%s'>" % \
                (self.meta.get('Title'), self.path)
        return "<Content object at '%s'>" % self.path

    def read(self):
        """Load the current state on the disk. If you use `read`
        before you saved eventual changes with `write` they will
        be lost."""
        with open(self.full_path()) as f:
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
        return os.path.join(self.root, self.path)

    def load_meta(self, meta):
        return yaml.safe_load(meta)

    def dump_meta(self, meta):
        return yaml.safe_dump(
            self._meta,
            default_flow_style=False
        ).encode('utf8')

    def render(self, body):
        return misaka.html(body)

    @property
    def url(self):
        """
            Make all urls nice and shiny, slashes in the end and
            beginning. This way links work much better.
        """
        return '/' + self._url + '/'

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

    """
        The main interaction object with the api. Will map urls onto
        markdown files. Takes to optional arguments when initiated:

            :param path: The place where the files are on which the urls
            should be mapped
            :param contentclass: In case you want to overwrite the class
            that is used for content objects you can pass it on here and
            the `Mapper` class will use it.

        As this library was designed to be used with flask and with app
        factories you can pass the `path` later using `init_path`. If
        you pass the `path` on init it will automatically be called.

        Please note that the path has to exist and be a directory, it
        does not have to have any content though.
    """

    def __init__(self, path=None, contentclass=Content):
        self.contentclass = contentclass
        if path:
            self.init_path(path)

    def init_path(self, path):
        """
            Checks whether the given path exists and is a directory.
            Cleans the path and saves it to the instance.

                :param path: The path in which urltomd should search for
                files.
        """
        if not os.path.isdir(path):
            raise IOError('%s does not exist or is not a directory.'
                          % path)
        if not path.endswith('/'):
            path += '/'
        self.path = path

    def url2path(self, url, relative=False):
        """
            Converts the given url to the path of the corresponding
            local markdown file.

                :param url: the url to convert.
                :param relative: Is `False` per default, if it is `True`
                the function will return the path without the mapper
                root.
        """
        if relative:
            return url.strip('/') + '.md'
        return self.path + url.strip('/') + '.md'

    def exists(self, url):
        """
            Checks whether a markdown file exists in the given path that
            matches the given url.

            :param url: The path to check
        """
        path = self.url2path(url)
        return os.path.exists(path)

    def get(self, url):
        """
            Returns a content object to an url. It will be either an
            instance of `Content` or of the given `contentclass`.

                :param url: The url of the file to return.
        """
        if not self.exists(url):
            return None
        return self.contentclass(
            self.path,
            url,
            self.url2path(url, relative=True)
        )

    def create(self, url):
        """
            Creates a new content object corresponding to the given url.

                :param url: The url of the object.

            It will make sure that all necessary directories are created
            and the actual object can be successfully saved on the file
            system. It will NOT create the object itself, because there
            is no data yet. If the object exists already it will return
            `False`, otherwise it will return a content object (like
            `get`) that has to be saved to be created on the filesystem. 
        """
        path = self.url2path(url, relative=True)
        if self.exists(url):
            return False
        directory = '/'.join(path.split('/')[:-1])
        if len(directory) > 0 and not os.path.exists(self.path + directory):
            os.makedirs(self.path + path)
        return self.get(path)

    def delete(self, url):
        """
            Will try to remove the corresponding content object to the
            given url from the file system.

                :param url: The url of the object to remove.

            Returns `True` if the object existed and was removed and
            `False` if it does not exist.
        """
        if not self.exists(url):
            return False
        os.remove(self.url2path(url))
        return True

    def _list(self, subdirectory=None, _return='list'):
        def _walk(directory, path_prefix=()):
            for name in os.listdir(directory):
                fullname = os.path.join(directory, name)
                if os.path.isdir(fullname):
                    _walk(fullname, path_prefix + (name,))
                elif name.endswith('.md'):
                    path = u'/'.join(path_prefix + (name[:-3],))
                    if subdirectory:
                        path = u'/'.join([subdirectory, path])
                    element = self.get(path)

                    if _return == 'list':
                        elements.append(element)
                    elif _return == 'dict':
                        elements[element.url] = element

        if _return == 'list':
            elements = []
        elif _return == 'dict':
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
