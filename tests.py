import os
import tempfile
import shutil
import string
import random
from unittest import TestCase
from urltomd import Content, Mapper


class BaseTestCase(TestCase):

    """
        Will automatically create a random, empty directory so that the
        tests have a place to work with files. Will also clean and
        remove the directory afterwards.

        Additionally it defines some functions that are used in multiple
        tests.

        This is not actually running any tests but to be subclassed by
        the actual tests.
    """

    def setUp(self):
        self.path = tempfile.mkdtemp()

    def create_md_file(self):
        """
            Just a wrapper of `tempfile.mkstemp` that specifies a few
            default parameters like an `.md` suffix and the current
            test's path as dir.
        """
        return tempfile.mkstemp(suffix='.md', dir=self.path)

    def gen_rand_str(self, size=10,
                     chars=string.ascii_uppercase + string.digits):
        """
            Generate random strings for all purposes. Takes two optional
            parameters:

                :param size: How long is the string supposed to be (in 
                    chars). The default is 10.
                :param chars: The collection of chars to pick from. Per
                    default all uppercase letters from ascii and all
                    digits.

            Copied from http://stackoverflow.com/a/2257449/1743565
        """
        return ''.join(random.choice(chars) for x in range(size))

    def tearDown(self):
        shutil.rmtree(self.path)


class MapperTestCase(BaseTestCase):

    """
        Tests the content class.
    """

    def setUp(self):
        super(MapperTestCase, self).setUp()
        self.mapper = Mapper(self.path)

    def test_url2path(self):
        """
            Test whether urls are correctly converted.
        """
        urlpaths = {
            '/about/': 'about.md',
            'about': 'about.md',
            '/about': 'about.md',
            'about/': 'about.md',
        }
        for url, path in urlpaths.items():
            assert self.mapper.url2path(url) == os.path.join(self.path, path)
            assert self.mapper.url2path(url, relative=True) == path

    def test_exists(self):
        """
            Test whether file existence checks work.
        """
        url = self.gen_rand_str()
        assert self.mapper.exists(url) == False
        f = open(self.mapper.url2path(url), 'w')
        f.close()
        assert self.mapper.exists(url) == True

    def test_get(self):
        """
            Make sure that proper contentobjects are returned (of the
            custom class, if defined).
        """
        url = self.gen_rand_str()
        content = self.mapper.get(url)
        assert content == None

        f = open(self.mapper.url2path(url), 'w')
        f.close()
        content = self.mapper.get(url)
        assert content != None
        assert isinstance(content, Content)

        class CustomContent(Content):
            pass

        custommapper = Mapper(self.path, contentclass=CustomContent)
        content = custommapper.get(url)
        assert content != None
        assert isinstance(content, CustomContent)

    def test_create(self):
        """
            Create only non existing files but necessary directories.
        """
        url = self.gen_rand_str()
        f = open(self.mapper.url2path(url), 'w')
        f.close()

        content = self.mapper.create(url)
        assert content == False

        dirurl = self.gen_rand_str()
        deepurl = os.path.join(dirurl, url)
        content = self.mapper.create(deepurl)
        assert os.path.exists(os.path.join(self.path, dirurl))

        superdirurl = self.gen_rand_str()
        deepdeepurl = os.path.join(superdirurl, dirurl, url)
        content = self.mapper.create(deepdeepurl)
        assert os.path.exists(os.path.join(self.path, superdirurl, dirurl))

    def test_delete(self):
        """
            Make sure deletion works.
        """
        url = self.gen_rand_str()
        result = self.mapper.delete(url)
        assert result == False
        f = open(self.mapper.url2path(url), 'w')
        f.close()
        result = self.mapper.delete(url)
        assert result == True
        assert os.path.exists(self.mapper.url2path(url)) == False


class ContentTestCase(BaseTestCase):

    pass
