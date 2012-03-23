# -*- coding: utf-8 -*-

import serial
import os
import time
import tempfile 
from filelock import FileLock
from pprint import pprint


actual_codes = {}
common_codes = {
    'aspect43'      : b"kc 00 01",
    'aspect169'     : b"kc 00 02",
    'poweroff'      : b"ka 00 00",
    'poweron'       : b"ka 00 01",
    'volumelevel'   : b"kf 00 ff",
    'mute'          : b"ke 00 00",
    'unmute'        : b"ke 00 01"
}
actual_codes['LK450_etc'] = common_codes.copy()
actual_codes['LK450_etc'].update({
    'inputdigitalantenna'   : b"xb 00 00",
    'inputdigitalcable'     : b"xb 00 01",
    'inputanalogantenna'    : b"xb 00 10",
    'inputanalogcable'      : b"xb 00 11",
    'inputav1'              : b"xb 00 20",
    'inputav2'              : b"xb 00 21",
    'inputcomp1'            : b"xb 00 40",
    'inputcomp2'            : b"xb 00 41",
    'inputrgbpc'            : b"xb 00 60",
    'inputhdmi1'            : b"xb 00 90",
    'inputhdmi2'            : b"xb 00 91",
    'inputhdmi3'            : b"xb 00 92",
    'inputhdmi4'            : b"xb 00 93"
})
actual_codes['LE5300_etc'] = common_codes.copy()
actual_codes['LE5300_etc'].update({
    'inputdtv'              : b"xb 00 00",
    'inputanalogantenna'    : b"xb 00 10",
    'inputanalogcable'      : b"xb 00 11",
    'inputav1'              : b"xb 00 20",
    'inputav2'              : b"xb 00 21",
    'inputcomp'             : b"xb 00 40",
    'inputrgbpc'            : b"xb 00 60",
    'inputhdmi1'            : b"xb 00 90",
    'inputhdmi2'            : b"xb 00 91",
    'inputhdmi3'            : b"xb 00 92",
    'inputhdmi4'            : b"xb 00 93"
})
actual_codes['LC7D_etc'] = common_codes.copy()
actual_codes['LC7D_etc'].update({
    'inputdtvantenna'       : b"xb 00 00",
    'inputdtvcable'         : b"xb 00 01",
    'inputanalogantenna'    : b"xb 00 10",
    'inputanalogcable'      : b"xb 00 11",
    'inputav1'              : b"xb 00 20",
    'inputav2'              : b"xb 00 21",
    'inputcomp1'            : b"xb 00 40",
    'inputcomp2'            : b"xb 00 41",
    'inputrgbpc'            : b"xb 00 60",
    'inputhdmi1'            : b"xb 00 90",
    'inputhdmi2'            : b"xb 00 91"
})
actual_codes['01C_etc'] = common_codes.copy()
actual_codes['01C_etc'].update({
    'inputav'       : b"kb 00 02",
    'inputcomp1'    : b"kb 00 04",
    'inputcomp2'    : b"kb 00 05",
    'inputrgbdtv'   : b"kb 00 06",
    'inputrgbpc'    : b"kb 00 07",
    'inputhdmidtv'  : b"kb 00 08",
    'inputhdmipc'   : b"kb 00 09"
})
actual_codes['02C_etc'] = common_codes.copy()
actual_codes['02C_etc'].update({
    'inputav'       : b"kb 00 02",
    'inputcomp1'    : b"kb 00 04",
    'inputcomp2'    : b"kb 00 05",
    'inputrgbpc'    : b"kb 00 07",
    'inputhdmidtv'  : b"kb 00 08",
    'inputhdmipc'   : b"kb 00 09"
})
reverse_code_map = {
    'LK450_etc': ('LV2500', 'LV2520', 'LV3500', 'LV3520', 'LK330', 'LK430', 'LK450',
                    'LK520', 'PW340', 'PW350', 'PW350U', 'PW350R', 'LH20', 'LH200C',
                    'LH30', 'LF11', 'LF21', 'LU55', 'CL10', 'CL20', 'CL11', 'PZ200'),
    'LC7D_etc': ('LC7D', 'LC7DC', 'PC5D', 'PC5DC'),
    'LE5300_etc': ('LE5300', 'LE5500', 'LE7300', 'LE530C', 'LD420', 'LD450', 'LD450C',
                    'LD520', 'LD520C', 'LD630', 'LW5600', 'LW5700', 'LW6500', 'LW9800',
                    'LV3700', 'LV5400', 'LV5500', 'LV9500', 'LK530', 'LK550', 'PZ750',
                    'PZ950', 'PZ950U'),
    '01C_etc': ('01C', '01C-BA'),
    '02C_etc': ('02C', '02C-BA', '02C-BH')
}
all_codes = {}
# populate model suffix lookup hash
for suffix_codes, suffixes in reverse_code_map.items():
    for suffix in suffixes:
        all_codes[suffix] = actual_codes[suffix_codes]


class LGTV:    
    def __init__(self, model, port):
        self.model = model.upper()

        # Ignore digits which indicate the TV's screen size
        if model.startswith('M'):
            self.codes = all_codes[self.model[3:]]  # Ignore the leading 'M' too
        else:
            self.codes = all_codes[self.model[2:]]

        self.port = port
        self.connection = None
        self.toggles = {
            'togglepower': ('poweron', 'poweroff'),
            'togglemute': ('mute', 'unmute'),
        }
        self.debounces = {}

    #this next line sets up the serial port to allow for communication
    #and opens the serial port you may need to change
    #ttyS0 to S1, S2, ect. The rest shouldn't need to change.
    def get_port(self):
        return serial.Serial(self.port, 9600, 8, serial.PARITY_NONE,
                serial.STOPBITS_ONE, xonxoff=0, rtscts=0, timeout=1)
                                    
    def get_port_ensured(self):
        ser = None
        while ser == None:
            try:
                ser = self.get_port()
            except serial.serialutil.SerialException:
                time.sleep(0.07)
        return ser
            
    def available_commands(self):
        print("Some features (such as a 4th HDMI port) might not be available for your TV model")
        commands = self.codes.copy()
        commands.update(self.toggles)
        for command in commands.keys():
            code = commands[command]
            if command.endswith('level'):
                print("%s : %s" % (command[:-5] + 'up', code[:-2] + b'??'))
                print("%s : %s" % (command[:-5] + 'down', code[:-2] + b'??'))
            else:
                print("{0} : {1}".format(command, code))

    def add_toggle(self, command, state0, state1):
        self.toggles['toggle' + command] = (state0, state1)
        
    def debounce(self, command, wait_secs=0.5):
        self.debounces[command] = wait_secs
    
    def status(self, code):
        return code[:-2] + b'ff'

    def lookup(self, command):
        if command.startswith('toggle'):
            states = self.toggles.get(command)
            state_codes = (self.codes[states[0]], self.codes[states[1]])
            return self.toggle(self.status(state_codes[0]), state_codes)
        elif command.endswith('up'):
            key = command[:-2] + 'level'
            return self.increment(self.status(self.codes[key]))
        elif command.endswith('down'):
            key = command[:-4] + 'level'
            return self.decrement(self.status(self.codes[key]))
        else:
            return self.codes[command]

    def query(self, command):
        self.connection.write(command + b'\r')
        response = self.connection.read(10)
        return response

    def query_data(self, command):
        return self.query(command)[-3:-1]
       
    def send(self, command):
        if command in self.debounces:
            wait_secs = self.debounces[command]
            if self.connection == None:
                self.connection = self.get_port()
            lock_path = os.path.join(tempfile.gettempdir(), '.' + command + '_lock')
            with FileLock(lock_path, timeout=0) as lock:
                self.query(self.lookup(command))
                time.sleep(wait_secs)
        else:
            if self.connection == None:
                self.connection = self.get_port_ensured()
            self.query(self.lookup(command))
        self.connection.close()

    def hex_bytes_delta(self, hex_bytes, delta):
        return bytes(hex(int(hex_bytes, 16) + delta)[2:4], 'ascii')

    def delta(self, command, delta):
        level = self.query_data(command)
        pprint(level)
        pprint(command)
        return command[0:6] + self.hex_bytes_delta(level, delta)

    def increment(self, command):
        return self.delta(command, +1)

    def decrement(self, command):
        return self.delta(command, -1)

    def toggle(self, command, togglecommands):
        level = self.query_data(command)
        toggledata = (togglecommands[0][-2:], togglecommands[1][-2:])
        data = toggledata[0]
        if level == toggledata[0]:
            data = toggledata[1]
        return command[0:6] + data
            
# end class LGTV
