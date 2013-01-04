# URLtoMD

URLtoMD is a simple tool to map url like structured content onto your filesystem. It manages your content with yaml and markdown in plaintext files and directories, so you can easily manage it by hand.

They body will be handled as markdown and metadata will be saved as yaml. Metadata will always come first separated from the markdown body by an empty line.

## How it works

    ```python
    import urltomd
    # create an instance of the mapper that manages a directory of your choice
    mapper = urltomd.Mapper('your directory') 

    # create new content in the directory
    blogpost = mapper.create('urltomd')
    blogpost.meta['title'] = 'Today I discoved urltomd'
    blogpost.meta['author'] = 'Me'
    blogpost.type['type'] = 'post'
    blogpost.body = 'It is a really cool tool to manage content in a human readable way.'
    blogpost.save()

# How can I get it?
Just download the `urltomd.py` file and import it to your project.

The requirements can be checked in the `requirements.txt` file, which are basically yaml and markdown.