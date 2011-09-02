# -*- coding: utf-8 -*-

import serial
from filelock import FileLock
from pprint import pprint



class LGTV:
	common_codes = {
		'aspect43'		: b"kc 00 01",
		'aspect169'		: b"kc 00 02",
		'poweroff'		: b"ka 00 00",
		'poweron'			: b"ka 00 01",
		'volumelevel'	: b"kf 00 ff",
		'mute'				: b"ke 00 00",
		'unmute'			: b"ke 00 01"
	}
	LV_LK_PW_LH_LF_LU_CL_codes = common_codes.copy().update({
		'inputdigitalantenna'	: b"xb 00 00",
		'inputdigitalcable'		: b"xb 00 01",
		'inputanalogantenna'	: b"xb 00 10",
		'inputanalogcable'		: b"xb 00 11",
		'inputav1'						: b"xb 00 20",
		'inputav2'						: b"xb 00 21",
		'inputcomp1'					: b"xb 00 40",
		'inputcomp2'					: b"xb 00 41",
		'inputrgbpc'					: b"xb 00 60",
		'inputhdmi1'					: b"xb 00 90",
		'inputhdmi2'					: b"xb 00 91",
		'inputhdmi3'					: b"xb 00 92",
		'inputhdmi4'					: b"xb 00 93",
	})
	LE_LD_codes = common_codes.copy().update({
		'inputdtv'						: b"xb 00 00",
		'inputanalogantenna'	: b"xb 00 10",
		'inputanalogcable'		: b"xb 00 11",
		'inputav1'						: b"xb 00 20",
		'inputav2'						: b"xb 00 21",
		'inputcomp'						: b"xb 00 40",
		'inputrgbpc'					: b"xb 00 60",
		'inputhdmi1'					: b"xb 00 90",
		'inputhdmi2'					: b"xb 00 91",
		'inputhdmi3'					: b"xb 00 92",
		'inputhdmi4'					: b"xb 00 93"
	})
	LC_PC_codes = common_codes.copy().update({
		'inputdtv'		: b"xb 00 00",
		'inputav1'		: b"kb 00 02",
		'inputav2'		: b"kb 00 03",
		'inputcomp1'	: b"kb 00 04",
		'inputcomp2'	: b"kb 00 04",
		'inputrgbpc'	: b"kb 00 07",
		'inputdvi'		: b"kb 00 08",
		'inputhdmi1'	: b"kb 00 08",
		'inputhdmi2'	: b"kb 00 09"
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
	
	def __init__(self, model, port):
		self.model = model.replace('-', '').upper()
		self.codes = all_codes[model[2:4]]
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
			return serial.Serial(port, 9600, 8, serial.PARITY_NONE,
									serial.STOPBITS_ONE, xonxoff=0, rtscts=0, timeout=1)
									
	def get_port_ensured(self):
			ser = None
			while ser == None:
					try:
							ser = get_port()
					except serial.serialutil.SerialException:
							time.sleep(0.07)
			return ser
			
	def available_commands(self):
		print "Some features (such as a 4th HDMI port) might not be available for your TV model"
		pprint(codes)

	def add_toggle(self, command, state0, state1):
		toggles['toggle' + command] = (state0, state1)
		
	def debounce(self, command, wait_secs=0.5):
		debounces[command] = wait_secs
	
	def status(self, code):
		return code[:-2] + b'ff'

	def lookup(self, command):
		if command.startswith('toggle'):
			states = toggles[command.lstrip('toggle')]
			state_codes = (codes[state[0]], codes[state[1]])
			return toggle(status(state_codes[0]), state_codes)
		elif command.endswith('up'):
			key = command.rstrip('up') + 'level'
			return increment(status(codes[key]))
		elif command.endswith('down'):
			key = command.rstrip('down') + 'level'
			return decrement(status(codes[key]))
		else:
			return codes[command]

	def query(self, command):
			connection.write(command + b'\r')
			response = connection.read(10)
			return response[-3:-1]
			
	def send(self, command):
		if wait_secs = debounces[command]:
			self.connection = get_port()
			lock_path = os.path.join(LOCK_PATH, '.' + command + '_lock')
			with FileLock(lock_path, timeout=0) as lock:
				query(lookup(command))
				time.sleep(wait_secs)
		else:
			self.connection = get_port_ensured()
			query(lookup(command))
		connection.close()

	def hex_bytes_delta(self, hex_bytes, delta):
			return bytes(hex(int(hex_bytes, 16) + delta)[2:4], 'ascii')

	def delta(self, command, delta):
			level = query(command)
			return command[0:6] + hex_bytes_delta(level, delta)

	def increment(self, command):
			return delta(command, +1)

	def decrement(self, command):
			return delta(command, -1)

	def toggle(self, command, togglecommands):
			level = query(command)
			toggledata = (togglecommands[0][-2:], togglecommands[1][-2:])
			data = toggledata[0]
			if level == toggledata[0]:
					data = toggledata[1]
			return command[0:6] + data
			
# end class LGTV