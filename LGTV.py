# Sample Windows script which uses the library
# script --poweroff
#
import sys
from libLGTV-serial import LGTV

model = '19LV2500'					# Change this to your TV's model

# Change this to the serial port you're using
# On Linux it might look like '/dev/ttyS0'
# On a Mac it might look like '/dev/tty.usbmodemfa2321'
serial_port = "\\.\COM4"

if len(sys.argv) != 2: 
  print 'Usage: {0} <command>'.format(sys.argv[0])
	print 'Example: {0} --togglepower'.format(sys.argv[0])
  sys.exit(1)

tv = LGTV(model, serial_port)

# Example of adding a custom toggle command. Passing in '--toggleinput'
# will toggle between 'inputpc' and 'inputtv'
tv.add_toggle('input', 'inputpc', 'inputtv')

# tv.add_dial('brightness', b'00 xx ff')

# Sometimes a single remote button press is detected as many. By debouncing a
# command, we make sure its only called once per button press.
tv.debounce('togglepower')

tv.send(sys.argv[1].lstrip("--"))