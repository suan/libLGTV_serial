# -*- coding: utf-8 -*-

import serial
import os
import time
from filelock import FileLock
from pprint import pprint


common_codes = {
    'aspect43'      : b"kc 00 01",
    'aspect169'     : b"kc 00 02",
    'poweroff'      : b"ka 00 00",
    'poweron'       : b"ka 00 01",
    'volumelevel'   : b"kf 00 ff",
    'mute'          : b"ke 00 00",
    'unmute'        : b"ke 00 01"
}
LV_LK_PW_LH_LF_LU_CL_codes = common_codes.copy()
LV_LK_PW_LH_LF_LU_CL_codes.update({
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
LE_LD_codes = common_codes.copy()
LE_LD_codes.update({
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
LC_PC_codes = common_codes.copy()
LC_PC_codes.update({
    'inputdtv'      : b"xb 00 00",
    'inputav1'      : b"kb 00 02",
    'inputav2'      : b"kb 00 03",
    'inputcomp1'    : b"kb 00 04",
    'inputcomp2'    : b"kb 00 04",
    'inputrgbpc'    : b"kb 00 07",
    'inputdvi'      : b"kb 00 08",
    'inputhdmi1'    : b"kb 00 08",
    'inputhdmi2'    : b"kb 00 09"
})
all_codes = {
    'LV': LV_LK_PW_LH_LF_LU_CL_codes,
    'LK': LV_LK_PW_LH_LF_LU_CL_codes,
    'PW': LV_LK_PW_LH_LF_LU_CL_codes,
    'LF': LV_LK_PW_LH_LF_LU_CL_codes,
    'LU': LV_LK_PW_LH_LF_LU_CL_codes,
    'CL': LV_LK_PW_LH_LF_LU_CL_codes,
    'LC': LC_PC_codes,
    'PC': LC_PC_codes,
    'LE': LE_LD_codes,
    'LD': LE_LD_codes
}

LOCK_PATH = os.path.join(os.getcwd(), 'locks')


class LGTV:    
    def __init__(self, model, port):
        self.model = model.replace('-', '').upper()
        self.codes = all_codes[self.model[2:4]]
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
        commands = self.toggles.copy()
        commands.update(self.codes)
        pprint(commands)

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
            key = command.rstrip('up') + 'level'
            return self.increment(self.status(self.codes[key]))
        elif command.endswith('down'):
            key = command.rstrip('down') + 'level'
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
            self.connection = self.get_port()
            lock_path = os.path.join(LOCK_PATH, '.' + command + '_lock')
            with FileLock(lock_path, timeout=0) as lock:
                self.query(self.lookup(command))
                time.sleep(wait_secs)
        else:
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
