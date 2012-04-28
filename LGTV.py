# Sample Windows script which uses the libLGTV_serial library
# Can be called, for example by doing "python LGTV.py --poweroff"
#
import sys
from libLGTV_serial import LGTV

model = '42LK450'                    # Change this to your TV's model

# Change this to the serial port you're using
# On Linux it might look like '/dev/ttyS0'
# On a Mac it might look like '/dev/tty.usbmodemfa2321'
serial_port = "\\.\COM4"

# Verify passed command
if len(sys.argv) != 2: 
    print('Usage: {0} <command>'.format(sys.argv[0]))
    print('Example: {0} --togglepower'.format(sys.argv[0]))
    sys.exit(1)

tv = LGTV(model, serial_port)

# Example of adding a custom toggle command. Passing in '--toggleinput'
# will toggle between 'inputrgbpc' and 'inputdigitalcable'
tv.add_toggle('input', 'inputrgbpc', 'inputdigitalcable')

# Sometimes a single remote button press is detected as many. By debouncing a
# command, we make sure its only called once per button press.
tv.debounce('togglepower')

# Finally, send the command
# .send() Returns nothing on failure, 2-digit bytecode for status commands,
# and True for other commands
print(tv.send(sys.argv[1].lstrip("--")))
