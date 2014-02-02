"""
    urltomd
    ----------------

    A library to map url structures onto files with yaml metadata and a
    markdown body. Perfect for static file cmses, blogs and alike.

    Links
    `````

    * `source code <https://github.com/alexex/urltomd>`_
"""
from setuptools import setup


setup(
    name='urltomd',
    version='0.3',
    url='https://github.com/alexex/urltomd',
    license='MIT',
    author='Alexander Jung-Loddenkemper',
    author_email='alexander@julo.ch',
    description='A library for mapping urls on to markdown files with yaml metadata',
    long_description=__doc__,
    packages=['urltomd'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'pyyaml',
        'misaka'
    ],
)
