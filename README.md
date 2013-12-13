# URLtoMD

URLtoMD is a simple tool to map url like structured content onto your filesystem. It manages your content with yaml and markdown in plaintext files and directories, so you can easily manage it by hand.

They body will be handled as markdown and metadata will be saved as yaml. Metadata will always come first separated from the markdown body by an empty line.

## How does it work?

```python
import urltomd
# create an instance of the mapper that manages
# a directory of your choice
mapper = urltomd.Mapper('.')
# yes, relative directories will work! 

# create new content in the directory
blogpost = mapper.create('urltomd')
blogpost.meta['title'] = 'Today I discoved urltomd'
blogpost.meta['author'] = 'Me'
blogpost.meta['type'] = 'post'
blogpost.body = 'It is a really cool tool to manage content in a human readable way.'
blogpost.save()

# mapper.contents will show you all the contents
# in your directory
mapper.contents
```

## How can I get it?
Just install it via pip!

    pip install urltomd

You can then import the relevant classes (only `Mapper` is necessary) from `urltomd`:

```python
import urltomd

mapper = urltomd.Mapper('.')
```

## This is too low level for me.
I can totally understand that. I am currently working on [flare](https://github.com/alexex/flare), which is basically a a highly customizable static file content management system built upon urltomd. Why don't you have a look at it?