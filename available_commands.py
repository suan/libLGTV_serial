# Shows all available commands for your TV 
#
from libLGTV_serial import LGTV

model = '42LK450'                    # Change this to your TV's model
tv = LGTV(model, 'dont_care')

# Example of adding a custom toggle command. Passing in '--toggleinput'
# will toggle between 'inputrgbpc' and 'inputdigitalcable'
tv.add_toggle('input', 'inputrgbpc', 'inputdigitalcable')

tv.available_commands()
input("Press Enter to continue...")
