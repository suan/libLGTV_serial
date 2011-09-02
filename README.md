# libLGTV-serial #
libLGTV-serial is a Python library to control LG TVs via their serial (RS232) port. It aims to reduce the legwork needed to use this functionality on your TV - simply enter your TV model number and you're good to go!

## dada ##
A full list of currently supported models can be found on [the wiki](dada). Don't worry if your device isn't listed there, it should be relatively easy to look up the codes from the Owner's Manual on the included CD-ROM or from [LG's Support Website]().
Make sure you have pyserial installed
Windows: http://pypi.python.org/pypi/pyserial
Debian/Ubuntu Linux: sudo apt-get install python-serial
Set your model name...
Currently I'm using the library in a script which is invoked everytime certain buttons are pressed on my HDTV remote, but there's no reason it can't be used in other ways, such as in a client-server configuration.

## Supported... ##
This was written in Python 3.2 and tested on Windows. 

## Credits ##
[Jon Smith's blog post](http://www.thelazysysadmin.net/2009/05/rs232-control-lg-lcd-tv-mythtv/) which is the core of the library
[Evan Fosmark](http://www.evanfosmark.com/2009/01/cross-platform-file-locking-support-in-python/) for filelock.py

#### Underscores
this should have _emphasis_
this_should_not
_nor_should_this

#### Autolinking
a non-markdown link: http://github.com/blog
this one is [a markdown link](http://github.com/blog)
Email test: support@github.com

#### Commit links
c4149e7bac80fcd1295060125670e78d3f15bf2e
tekkub@c4149e7bac80fcd1295060125670e78d3f15bf2e
mojombo/god@c4149e7bac80fcd1295060125670e78d3f15bf2e

#### Issue links
issue #1
tekkub#1
mojombo/god#1