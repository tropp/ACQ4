"""
Low-level serial communication for Trinamic TMCM-140-42-SE controller
(used internally for the Thorlabs MFC1)
"""


import serial, struct, time, collections

try:
    # this is nicer because it provides deadlock debugging information
    from acq4.util.Mutex import RecursiveMutex as RLock
except ImportError:
    from threading import RLock

try:
    from ..SerialDevice import SerialDevice, TimeoutError, DataError
except ValueError:
    ## relative imports not allowed when running from command prompt, so
    ## we adjust sys.path when running the script for testing
    if __name__ == '__main__':
        import sys, os
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        from SerialDevice import SerialDevice, TimeoutError, DataError


def threadsafe(method):
    # decorator for automatic mutex lock/unlock
    def lockMutex(self, *args, **kwds):
        with self.lock:
            return method(self, *args, **kwds)
    return lockMutex



COMMANDS = {
    'rol': 2,
    'ror': 1,
    'mvp': 4,
    'mst': 3,
    'rfs': 13,
    'sco': 30,
    'cco': 32,
    'gco': 31,
    
    'sap': 5,
    'gap': 6,
    'stap': 7,
    'rsap': 8,
    'sgp': 9,
    'ggp': 10,
    'stgp': 11,
    'rsgp': 12,
    
    'sio': 14,
    'gio': 15,
    
    'calc': 19,
    'comp': 20,
    'jc': 21,
    'ja': 22,
    'csub': 23,
    'rsub': 24,
    'wait': 27,
    'stop': 28,
    'sco': 30,
    'gco': 31,
    'cco': 32,
    'calcx': 33,
    'aap': 34,
    'agp': 35,
    'aco': 39,
    
    'sac': 29,
    
    'stop_application': 128,
    'run_application': 129,
    'step_application': 130,
    'reset_application': 131,
    'start_download': 132,
    'stop_download': 133,
    'get_application_status': 135,
    'get_firmware_version': 136,
    'restore_factory_settings': 137,    
}



PARAMETERS = {    # negative values indicate read-only parameters
    'target_position': 0,
    'actual_position': 1,
    'target_speed': 2,
    'actual_speed': 3,
    'maximum_speed': 4,
    'maximum_acceleration': 5,
    'maximum_current': 6,
    'standby_current': 7,
    'target_pos_reached': 8,
    'ref_switch_status': 9,
    'right_limit_switch_status': 10,
    'left_limit_switch_status': 11,
    'right_limit_switch_disable': 12,
    'left_limit_switch_disable': 13,
    'minimum_speed': -130,
    'acceleration': -135,
    'ramp_mode': 138,
    'microstep_resolution': 140,
    'soft_stop_flag': 149,
    'ramp_divisor': 153,
    'pulse_divisor': 154,
    'referencing_mode': 193,
    'referencing_search_speed': 194,
    'referencing_switch_speed': 195,
    'distance_end_switches': 196,
    'mixed_decay_threshold': 203,
    'freewheeling': 204,
    'stall_detection_threshold': 205,
    'actual_load_value': 206,
    'driver_error_flags': -208,
    'encoder_position': 209,
    'encoder_prescaler': 210,
    'fullstep_threshold': 211,
    'maximum_encoder_deviation': 212,
    'power_down_delay': 214,
    'absolute_encoder_value': -215,
}


GLOBAL_PARAMETERS = {
    'eeprom_magic': 64,
    'baud_rate': 65,
    'serial_address': 66,
    'ascii_mode': 67,
    'eeprom_lock': 73,
    'auto_start_mode': 77,
    'tmcl_code_protection': 81,
    'coordinate_storage': 84,
    'tmcl_application_status': 128,
    'download_mode': 129,
    'tmcl_program_counter': 130,
    'tick_timer': 132,
    'random_number': -133,
}


OPERATORS = {
    'add': 0,
    'sub': 1,
    'mul': 2,
    'div': 3,
    'mod': 4,
    'and': 5,
    'or': 6,
    'xor': 7,
    'not': 8,
    'load': 9,
}


STATUS = {
    1: "Wrong checksum",
    2: "Invalid command",
    3: "Wrong type",
    4: "Invalid value",
    5: "Configuration EEPROM locked",
    6: "Command not available",
}


class TMCMError(Exception):
    def __init__(self, status):
        self.status = status
        msg = STATUS[status]
        
        Exception.__init__(msg)
        

class TMCM140(SerialDevice):

    def __init__(self, port, baudrate=9600, module_addr=1):
        """
        port: serial COM port (eg. COM3 or /dev/ttyACM0)
        baudrate: 9600 by default
        module_addr: 1 by default
        """
        self.lock = RLock()
        self.port = port
        assert isinstance(module_addr, int)
        assert module_addr > 0
        self.module_addr = module_addr
        self.module_str = chr(module_addr+64)
        self._waiting_for_reply = False
        SerialDevice.__init__(self, port=self.port, baudrate=baudrate)

    @threadsafe
    def command(self, cmd, type, motor, value):
        """Send a command to the controller and return the reply.
        
        If an error is returned from the controller then raise an exception.
        """
        self._send_cmd(cmd, type, motor, value)
        return self._get_reply()
   
    def rotate(self, velocity):
        """Begin rotating motor.
        
        velocity: -2047 to +2047
                  negative values turn left; positive values turn right.
        """
        assert isinstance(velocity, int)        
        assert -2047 <= velocity <= 2047
        if velocity < 0:
            direction = 'l'
            velocity = -velocity
        else:
            direction = 'r'
        self.command('ro'+direction, 0, 0, velocity)

    def stop(self):
        """Stop the motor.
        
        Note: does not stop currently running programs.
        """
        self.command('mst', 0, 0, 0)
        
    def move(self, pos, relative=False, velocity=None):
        """Rotate until reaching *pos*.
        
        pos: The target position
        relative: If True, then *pos* is interpreted as relative to the current 
                  position
        velocity: Optionally set the target velocity before moving 
        """
        assert isinstance(pos, int)
        assert -2**32 <= pos < 2**32
        if velocity is not None:
            assert isinstance(velocity, int) 
            assert 0 <= velocity < 2048
            raise NotImplementedError()
        
        type = 1 if relative else 0
        self.command('mvp', type, 0, pos)
        
    def get_param(self, param):
        pnum = abs(PARAMETERS[param])
        return self.command('gap', pnum, 0, 0)[4]
        
    def __getitem__(self, param):
        return self.get_param(param)
        
    def set_param(self, param, value, **kwds):
        pnum = PARAMETERS[param]
        if pnum < 0:
            raise TypeError("Parameter %s is read-only." % param)
        if pnum == PARAMETERS['maximum_current'] and value > 100:
            if kwds.get('force', False) is not True:
                raise Exception("Refusing to set max_current > 100 (this can damage the motor). "
                                "To override, use force=True.")
        self.command('sap', pnum, 0, value)

    @threadsafe
    def set_params(self, **kwds):
        """Set multiple parameters.
        
        The driver is thread-locked until all parameters are set.
        """
        for param, value in kwds.values():
            self.set_param(param, value)
        
    def __setitem__(self, param, value):
        return self.set_param(param, value)

    def get_global(self, param):
        pnum = abs(GLOBAL_PARAMETERS[param])
        return self.command('ggp', pnum, 0, 0)[4]
        
    def set_global(self, param, value):
        pnum = GLOBAL_PARAMETERS[param]
        if pnum < 0:
            raise TypeError("Parameter %s is read-only." % param)
        self.command('sgp', pnum, 0, value)
            
    def stop_program(self):
        """Stop the currently running TMCL program.
        """
        self.command('stop_application', 0, 0, 0)

    def start_program(self, address=None):
        """Start running TMCL program code from the given address (in bytes?), 
        or from the current address if None.
        """
        if address is None:
            self.command('run_application', 0, 0, 0)
        else:
            self.command('run_application', 1, 0, address)
        
    def start_download(self, address=0):
        """Begin loading TMCL commands into EEPROM .
        """
        self.command('start_download', 0, 0, address)
        
    def stop_download(self):
        """Finish loading TMCL commands into EEPROM.
        """
        self.command('stop_download', 0, 0, 0)
        
    def program_status(self):
        """Return current program status:
        
        0=stop, 1=run, 2=step, 3=reset
        """
        return self.command('get_application_status', 0, 0, 0)[4]
        
    def _send_cmd(self, cmd, type, motor, value):
        """Send a command to the controller.
        """
        if self._waiting_for_reply:
            raise Exception("Cannot send command; previous reply has not been "
                            "received yet.")
        cmd_num = COMMANDS[cmd]
        assert isinstance(type, int)
        assert isinstance(motor, int)
        
        # Try packing the value first as unsigned, then signed. (the overlapping
        # integer ranges have identical bit representation, so there is no 
        # ambiguity)
        try:
            cmd = struct.pack('>BBBBI', self.module_addr, cmd_num, type, motor, value)
        except struct.error:
            cmd = struct.pack('>BBBBi', self.module_addr, cmd_num, type, motor, value)
            
        chksum = sum(bytearray(cmd)) % 256
        self.write(cmd + struct.pack('B', chksum))
        self._waiting_for_reply = True
        
    def _get_reply(self):
        """Read and parse a reply from the controller.
        
        Raise an exception if an error was reported.
        """
        if not self._waiting_for_reply:
            raise Exception("No reply expected.")
        
        try:
            d = self.read(9)
        finally:
            self._waiting_for_reply = False
        d2 = self.readAll()
        if len(d2) > 0:
            raise Exception("Error: extra data while reading reply.")
        
        parts = struct.unpack('>BBBBiB', d)
        reply_addr, module_addr, status, cmd_num, value, chksum = parts
        
        if chksum != sum(bytearray(d[:-1])) % 256:
            raise Exception("Invalid checksum reading from controller.")
        
        if status < 100:
            raise TMCMError(status)        
        
        return parts
   
    
        
    
if __name__ == '__main__':
    import time
    import pyqtgraph as pg
    s = TMCM140(port='/dev/ttyACM0', baudrate=9600)
    
    s['maximum_current'] = 50
    s.stop()
    s['encoder_position'] = 0
    s['actual_position'] = 0
    
    def step_curve(decay_threshold=-1):
        """Measure encoder following single steps at all microstep resolutions.
        """
        s['mixed_decay_threshold'] = decay_threshold
        s['stall_detection_threshold'] = 0
        plt = pg.plot()
        for res in range(7):
            x = []
            s['microstep_resolution'] = res
            #s['encoder_prescaler'] = int(2**res * 100)
            s['encoder_prescaler'] = 6400
            for i in range(150):
                s.move(1, relative=True)
                while s['target_pos_reached'] == 0:
                    pass
                x.append(s['encoder_position'])
                x.append(s['encoder_position'])
                x.append(s['encoder_position'])
                print i, x[-1]
            plt.plot(x, symbol='o')
            pg.QtGui.QApplication.processEvents()

    def test_stall(threshold=7, ustep=3, speed=800):
        s['microstep_resolution'] = ustep
        s['mixed_decay_threshold'] = 2047
        s['stall_detection_threshold'] = threshold
        while True:
            s.rotate(speed)
            time.sleep(0.5)
            s.stop()
            time.sleep(0.2)

    def test_seek():
        global x, t
        ures = 6
        s.stop()
        s['microstep_resolution'] = ures
        s['encoder_prescaler'] = 8192
        s['encoder_position'] = 0
        s['standby_current'] = 0
        s['maximum_speed'] = 50
        s['power_down_delay'] = 1200
        #s['freewheeling'] = 1000
        #s['actual_position'] = 0
        
        s.move(600, relative=True)
        start = time.time()
        t = []
        x = []
        while True:
            now = time.time()
            if now - start > 3:
                print "QUIT"
                break
            t.append(now-start)
            x.append(s['encoder_position'])
            
        pg.plot(t, x)
        
    def test_encoder():
        plt = pg.plot()
        data = []
        while True:
            data.append(s['encoder_position'])
            if len(data) > 100:
                data.pop(0)
            plt.plot(data, clear=True)
            pg.QtGui.QApplication.processEvents()

        
    #step_curve()
    #test_seek()

        