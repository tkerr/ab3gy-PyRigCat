###############################################################################
# PyRigCat_ft991.py
# Author: Tom Kerr AB3GY
#
# A python Computer Aided Tranceiver (CAT) module for amateur radio use.
# Implements CAT control for the Yaesu FT-991 and FT-991A transceiver.
# Reference: Yeesu FT-991A CAT Operation Reference Manual (1612-C)
#
# Designed for personal use by the author, but available to anyone under the
# license terms below.
###############################################################################

###############################################################################
# License
# Copyright (c) 2022 Tom Kerr AB3GY (ab3gy@arrl.net).
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice,   
# this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice,  
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.
# 
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without 
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.
###############################################################################

# System level packages.

# Local packages.
from PyRigCat.PyRigCat import PyRigCat, Datasize, Parity, Stopbits, Flow, \
    PttMethod, OperatingMode, RigName

##############################################################################
# Globals.
##############################################################################

# CTCSS tone codes.
CTCSS_TONES = { 
     '670':'000',  '693':'001',  '719':'003',  '744':'004',  '770':'005', 
     '825':'006',  '854':'007',  '885':'008',  '915':'009',  '948':'010',
     '974':'011', '1000':'012', '1035':'013', '1072':'014', '1109':'015',
    '1148':'016', '1188':'017', '1230':'018', '1273':'019', '1318':'020',
    '1365':'021', '1413':'022', '1462':'023', '1514':'024', '1567':'025',
    '1598':'026', '1622':'027', '1655':'028', '1679':'029', '1713':'030',
    '1738':'031', '1773':'032', '1799':'033', '1835':'034', '1862':'035',
    '1899':'036', '1928':'037', '1966':'038', '1995':'039', '2035':'040',
    '2065':'041', '2107':'042', '2181':'043', '2257':'044', '2291':'045',
    '2336':'046', '2418':'047', '2503':'048', '2541':'049'
    }

##############################################################################
# PyRigCat_ft991 class.
##############################################################################
class PyRigCat_ft991(PyRigCat):
    """
    CAT control class for the Yaesu FT-991 and FT-991A transceivers.
    This is a subclass of the PyRigCat base class.
    """
    
    # ------------------------------------------------------------------------
    def __init__(self):
        """
        Class constructor.
        """
        super().__init__()   # Call the base class constructor
        self.NAME = RigName.FT991
        self._has_data_modes = True
        self.set_ptt_method(PttMethod.CAT)
    
    # ------------------------------------------------------------------------
    def __del__(self):
        """
        Class destructor.
        """
        super().__del__()  # Call the base class destructor

    ##########################################################################
    # Rig control commands.
    # These need to be implemented by subclasses for each specific transceiver.
    ##########################################################################
    
    # ------------------------------------------------------------------------
    def init_rig(self):
        """
        Attempt to place the transceiver in a known state.
        Assumes config_port() has been called successfully first.
        Overrides the base class.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        None.
        """
        self.set_ptt_method(PttMethod.CAT)

    # ------------------------------------------------------------------------
    def ascii_cmd(self, cmd_str, arg_list):
        """
        Parse an ASCII command into one or more CAT commands and send them
        to the transceiver.  Recive response(s) and convert to an ASCII 
        response to the user.  Overrides the base class.
        
        Parameters
        ----------
        cmd_str : str
            The ASCII command to parse
        arg_list : str list
            List of string arguments for the command.  May be an empty list.        
        
        Returns
        -------
        resp : str
            A formatted ASCII response based on the command.
            May be PyRigCat.OK, PyRigCat.ERROR, PyRigCat.NOTFOUND, or a 
            command-specific response.
        """
        cmd_str = cmd_str.upper()
        
        # Try to handle the command in the parent class first.
        resp = super().ascii_cmd(cmd_str, arg_list)
        if (resp != PyRigCat.NOTFOUND): return resp
        
        # Parent class returned PyRigCat.NOTFOUND.
        # Parse the command here.

        # Get/set the transceiver date.
        if (cmd_str == 'DATE'):
            date_str = ''
            if (len(arg_list) > 0): date_str = str(arg_list[0]).upper().strip()
            resp = self.date_cmd(date_str)

        # Get/set the VFO-A frequency.
        elif (cmd_str == 'FREQ') or (cmd_str == 'FREQA'):
            freq_hz = ''
            if (len(arg_list) > 0): freq_hz = str(arg_list[0]).strip()
            resp = self.frequency_cmd(freq_hz, 'A')

        # Get/set the VFO-B frequency.
        elif (cmd_str == 'FREQB'):
            freq_hz = ''
            if (len(arg_list) > 0): freq_hz = str(arg_list[0]).strip()
            resp = self.frequency_cmd(freq_hz, 'B')

        # Get/set the IF narrow/wide setting.
        elif (cmd_str == 'IF-NARROW'):
            narrow_onoff = ''
            if (len(arg_list) > 0): narrow_onoff = str(arg_list[0]).upper().strip()
            resp = self.if_narrow_cmd(narrow_onoff)

        # Get/set the IF shift.
        elif (cmd_str == 'IF-SHIFT'):
            shift_hz_str = ''
            if (len(arg_list) > 0): shift_hz_str = str(arg_list[0]).strip()
            resp = self.if_shift_cmd(shift_hz_str)

        # Get/set the IF width.
        elif (cmd_str == 'IF-WIDTH'):
            width_idx = ''
            if (len(arg_list) > 0): width_idx = str(arg_list[0]).strip()
            resp = self.if_width_cmd(width_idx)
        
        # Get/set the dial lock
        elif (cmd_str == 'LOCK'):
            lock_onoff = ''
            if (len(arg_list) > 0): lock_onoff = str(arg_list[0]).strip()
            resp = self.lock_cmd(lock_onoff)

        # Get/set the operating mode.
        elif (cmd_str == 'MODE'):
            mode_str = ''
            if (len(arg_list) > 0): mode_str = str(arg_list[0]).upper().strip()
            resp = self.op_mode_cmd(mode_str)
        
        # Get/set VFO-B operating mode.
        elif (cmd_str == 'MODEB'):
            mode_str = ''
            if (len(arg_list) > 0): mode_str = str(arg_list[0]).upper().strip()
            resp = self.op_modeb_cmd(mode_str)
        
        # Get/set the monitor level.
        elif (cmd_str == 'MONITOR'):
            onoff = ''
            level = ''
            if (len(arg_list) > 0): onoff = str(arg_list[0]).upper().strip()
            if (len(arg_list) > 1): level = str(arg_list[1]).upper().strip()
            resp = self.monitor_level_cmd(onoff, level)

        # Get/set the RF power level.
        elif (cmd_str == 'POWER'):
            pwr_level = ''
            if (len(arg_list) > 0): pwr_level = str(arg_list[0]).strip()
            resp = self.power_level_cmd(pwr_level)

        # Get/set the speech processor level.
        elif (cmd_str == 'SPEECH'):
            onoff = ''
            level = ''
            if (len(arg_list) > 0): onoff = str(arg_list[0]).upper().strip()
            if (len(arg_list) > 1): level = str(arg_list[1]).upper().strip()
            resp = self.speech_processor_cmd(onoff, level)

        # Get/set split operation.
        # Receive = VFO-A, Transmit = VFO-B
        elif (cmd_str == 'SPLIT'):
            split_onoff = ''
            if (len(arg_list) > 0): split_onoff = str(arg_list[0]).upper().strip()
            resp = self.split_cmd(split_onoff)
        
        # Swap VFO-A <--> VFO-B
        elif (cmd_str == 'SWAPVFO'):
            resp = self.swapvfo_cmd()

        # Get/set the transceiver time.
        elif (cmd_str == 'TIME'):
            time_str = ''
            if (len(arg_list) > 0): time_str = str(arg_list[0]).upper().strip()
            resp = self.time_cmd(time_str)
        
        # Set the CTCSS tone mode and frequency.
        # mode = OFF, ENC, DEC
        # freq = frequency in Hz * 10 (e.g., 1318 = 131.8 Hz)
        elif (cmd_str == 'TONE'):
            mode = ''
            freq = ''
            if (len(arg_list) > 0): mode = str(arg_list[0]).upper().strip()
            if (len(arg_list) > 1): freq = str(arg_list[1]).upper().strip()
            resp = self.tone_cmd(mode, freq)
        
        return resp

    # ------------------------------------------------------------------------
    def xcvr_cmd(self, cmd, max_read=100000):
        """
        Common method to send a CAT command to the transceiver and receive a response.
        
        Parameters
        ----------
        cmd : str
            The full FT-991 ASCII command string including the ; terminator.
        max_read : int
            The maximum number of bytes to read after sending the command.
            If zero, then no read operation is performed.
        
        Returns
        -------
        resp : str
            The formatted ASCII response.
        """
        resp = ''
        send_buf = cmd.encode('ascii')
        sent = self._serial_write(send_buf)
        if (sent == len(send_buf)):
            if (max_read > 0):
                read_buf = self._serial_read(max_read)
                try:
                    resp = read_buf.decode('ascii')
                except Exception as err:
                    self._print_msg(str(err))
                    resp = 'READ ERROR'
        else:
            resp = 'WRITE ERROR'
        return resp
    
    # ------------------------------------------------------------------------
    def date_cmd(self, date_str):
        """
        Get/set the system date.
        date_str is the date in YYYYMMDD format.
        """
        resp = ''
        if (len(date_str) > 0):
            cmd = 'DT0' + date_str + ';'
            resp = self.xcvr_cmd(cmd, 2)
        else:
            resp = self.xcvr_cmd('DT0;', 12)
        if (resp == ''): resp = PyRigCat.OK
        elif (resp == '?;'): resp = PyRigCat.ERROR
        elif resp.startswith('DT0'):
            resp = resp[3:11]
        return resp

    # ------------------------------------------------------------------------
    def frequency_cmd(self, freq_hz, vfo):
        """
        Get/set the transceiver frequency from/to the specified VFO (A/B).
        """
        cmd = 'FA'
        if (vfo == 'B'): cmd = 'FB'
        if (len(freq_hz) > 0):
            freq_hz = freq_hz.zfill(9) # Ensure 9 numeric characters
            cmd += freq_hz
        cmd += ';'
        resp = self.xcvr_cmd(cmd, 12)
        if (resp == ''): resp = PyRigCat.OK
        elif (resp == '?;'): resp = PyRigCat.ERROR
        elif resp.startswith('FA') or resp.startswith('FB'):
            resp = resp[2:11]
        return resp

    # ------------------------------------------------------------------------
    def if_narrow_cmd(self, narrow_onoff):
        """
        Get/set the IF narrow/wide setting.
        ON = IF narrow
        OFF = IF wide
        """
        cmd = ''
        resp = ''
        if (len(narrow_onoff) > 0):
            if (narrow_onoff == 'OFF'):
                cmd = 'NA00;'
            elif (narrow_onoff == 'ON'):
                cmd = 'NA01;'
            else:
                return PyRigCat.ERROR
            resp = self.xcvr_cmd(cmd, 2)
            if (resp == ''): resp = PyRigCat.OK
            elif (resp == '?;'): resp = PyRigCat.ERROR    
        else:
            resp = self.xcvr_cmd('NA0;', 5)
            if (resp == ''): resp = PyRigCat.OK
            elif (resp == '?;'): resp = PyRigCat.ERROR
            elif (resp == 'NA00;'): resp = 'OFF'
            elif (resp == 'NA01;'): resp = 'ON'
        return resp

    # ------------------------------------------------------------------------
    def if_shift_cmd(self, shift_hz_str):
        """
        Get/set the IF shift in Hz.
        shift_hz_str is the shift in Hz as a signed numeric string.
        Note that the FT-991 rounds down to the next 20Hz step.
        """
        resp = ''
        # Sanity check the shift.
        if (len(shift_hz_str) > 0):
            shift_hz = 0
            try:
                shift_hz = int(shift_hz_str)
                if (shift_hz < -1000) or (shift_hz > 1000):
                    resp = PyRigCat.ERROR
                else:
                    # Create and send the IF width command.
                    cmd = 'IS0' + ('%+d' % shift_hz).zfill(5) + ';'
                    #print(cmd)
                    resp = self.xcvr_cmd(cmd, 2)
                    if (resp == ''): resp = PyRigCat.OK
                    elif (resp == '?;'): resp = PyRigCat.ERROR
            except ValueError:
                resp = PyRigCat.ERROR
        else:
            # Get the IF shift.
            resp = self.xcvr_cmd('IS0;', 9)
            if (resp == ''): resp = PyRigCat.OK
            elif (resp == '?;'): resp = PyRigCat.ERROR
            elif resp.startswith('IS0'): resp = resp[3:8]
        return resp

    # ------------------------------------------------------------------------
    def lock_cmd(self, lock_onoff):
        """
        Get/set the dial lock status.
        ON = Dial lock ON
        OFF = Dial lock OFF
        """
        resp = ''
        if (len(lock_onoff) > 0):
            if (lock_onoff == 'OFF'):
                cmd = 'LK0;'
            elif (lock_onoff == 'ON'):
                cmd = 'LK1;'
            else:
                return PyRigCat.ERROR
        else:
            cmd = 'LK;'
        resp = self.xcvr_cmd(cmd, 100)
        if (resp == ''): resp = PyRigCat.OK
        elif (resp == '?;'): resp = PyRigCat.ERROR
        elif resp.startswith('LK'): 
            if (resp[2] == '0'): resp = 'OFF'
            if (resp[2] == '1'): resp = 'ON'
        return resp
    
    # ------------------------------------------------------------------------
    def if_width_cmd(self, width_idx_str):
        """
        Get/set the IF width (IF DSP bandwidth).
        width_idx_str is a table index (numeric string) that sets the width  
        depending on the operating mode.  See the CAT operation reference manual 
        for details.
        """
        resp = ''
        # Sanity check the width table index.
        if (len(width_idx_str) > 0):
            if width_idx_str.isnumeric(): 
                width_num = int(width_idx_str)
                if (width_num < 0) or (width_num > 21):
                    resp = PyRigCat.ERROR
                else:
                    # Create and send the IF width command.
                    cmd = 'SH0' + str(width_num).zfill(2) + ';'
                    resp = self.xcvr_cmd(cmd, 2)
                    if (resp == ''): resp = PyRigCat.OK
                    elif (resp == '?;'): resp = PyRigCat.ERROR
            else:
                resp = PyRigCat.ERROR
        else:
            # Get the IF width index.
            resp = self.xcvr_cmd('SH0;', 6)
            if (resp == ''): resp = PyRigCat.OK
            elif (resp == '?;'): resp = PyRigCat.ERROR
            elif resp.startswith('SH0'): resp = resp[3:5]
        return resp

    # ------------------------------------------------------------------------
    def monitor_level_cmd(self, onoff, level_str):
        """
        Get/set the monitor level (0-100).
        onoff (if supplied) turns the monitor 'OFF' or 'ON'.
        level_str (if supplied) is the monitor level string (0 - 100).
        Returns 'OK', 'ERROR', or 'ON/OFF' + level
        """
        resp = PyRigCat.OK
        resp_onoff = ''
        resp_level = ''
        
        # Sanity check the monitor level.
        if (len(level_str) > 0):
            if level_str.isnumeric(): 
                level_pct = int(level_str)
                if (level_pct < 0) or (level_pct > 100):
                    resp_level = PyRigCat.ERROR
                else:
                    # Reformat as a 3-digit numeric string.
                    level_str = str(level_pct).zfill(3)
            else:
                resp_level = PyRigCat.ERROR
            if (resp_level == PyRigCat.ERROR): return PyRigCat.ERROR

        if (onoff == ''):
            # Get the monitor ON/OFF status.
            resp_onoff = self.xcvr_cmd('ML0;', 7)
            if (resp_onoff == 'ML0000;'): resp_onoff = 'OFF'
            elif (resp_onoff == 'ML0001;'): resp_onoff = 'ON'
            elif (resp_onoff == '?;'): resp_onoff = PyRigCat.ERROR
            # Get the monitor level.
            resp_level = self.xcvr_cmd('ML1;', 7)
            if resp_level.startswith('ML1'): resp_level = resp_level[3:6]
            elif (resp_level == '?;'): resp_level = PyRigCat.ERROR

        elif (onoff == 'OFF'):
            # Turn the monitor off.
            resp_onoff = self.xcvr_cmd('ML0000;', 2)
            if (resp_onoff == ''): resp_onoff = PyRigCat.OK
            elif (resp_onoff == '?;'): resp_onoff = PyRigCat.ERROR

        elif (onoff == 'ON'):
            # Turn the monitor on.
            resp_onoff = self.xcvr_cmd('ML0001;', 2)
            if (resp_onoff == ''): resp_onoff = PyRigCat.OK
            elif (resp_onoff == '?;'): resp_onoff = PyRigCat.ERROR
        else:
            resp_onoff = PyRigCat.ERROR

        # Exit if an error occurred.
        if (resp_onoff == PyRigCat.ERROR): return PyRigCat.ERROR
        elif (resp_level == PyRigCat.ERROR): return PyRigCat.ERROR
        
        # Set the monitor level.
        if (len(level_str) > 0):
            cmd = 'ML1' + level_str + ';'
            #print(cmd)
            resp_level = self.xcvr_cmd(cmd, 2)
            if (resp_level == ''): resp_level = PyRigCat.OK
            elif (resp_level == '?;'): resp_level = PyRigCat.ERROR

        resp = resp_onoff + ':' + resp_level
        return resp
    
    # ------------------------------------------------------------------------
    def op_mode_cmd(self, mode_str):
        """
        Get/set the transceiver operating mode.
        """
        cmd = 'MD0'
        mode_num = ''
        if (len(mode_str) > 0):
            mode_num = 'X' # Init to invalid value
            if (mode_str == OperatingMode.LSB): mode_num = '1'
            elif (mode_str == OperatingMode.USB): mode_num = '2'
            elif (mode_str == OperatingMode.CW): mode_num = '3'
            elif (mode_str == OperatingMode.FM): mode_num = '4'
            elif (mode_str == OperatingMode.AM): mode_num = '5'
            elif (mode_str == OperatingMode.RTTY): mode_num = '6'
            elif (mode_str == OperatingMode.CW_R): mode_num = '7'
            elif (mode_str == OperatingMode.DATA_LSB): mode_num = '8'
            elif (mode_str == OperatingMode.RTTY_R): mode_num = '9'
            elif (mode_str == OperatingMode.DATA_FM): mode_num = 'A'
            elif (mode_str == OperatingMode.FM_N): mode_num = 'B'
            elif (mode_str == OperatingMode.DATA_USB): mode_num = 'C'
            elif (mode_str == OperatingMode.AM_N): mode_num = 'D'
            elif (mode_str == OperatingMode.C4FM): mode_num = 'E'
        cmd += mode_num
        cmd += ';'
        resp = self.xcvr_cmd(cmd, 5)
        if (resp == ''): resp = PyRigCat.OK
        elif (resp == '?;'): resp = PyRigCat.ERROR
        elif resp.startswith('MD0'):
            mode_num = resp[3]
            if (mode_num == '1'): resp = OperatingMode.LSB
            elif (mode_num == '2'): resp = OperatingMode.USB
            elif (mode_num == '3'): resp = OperatingMode.CW
            elif (mode_num == '4'): resp = OperatingMode.FM
            elif (mode_num == '5'): resp = OperatingMode.AM
            elif (mode_num == '6'): resp = OperatingMode.RTTY
            elif (mode_num == '7'): resp = OperatingMode.CW_R
            elif (mode_num == '8'): resp = OperatingMode.DATA_LSB
            elif (mode_num == '9'): resp = OperatingMode.RTTY_R
            elif (mode_num == 'A'): resp = OperatingMode.DATA_FM
            elif (mode_num == 'B'): resp = OperatingMode.FM_N
            elif (mode_num == 'C'): resp = OperatingMode.DATA_USB
            elif (mode_num == 'D'): resp = OperatingMode.AM_N
            elif (mode_num == 'E'): resp = OperatingMode.C4FM
        return resp

    # ------------------------------------------------------------------------
    def op_modeb_cmd(self, mode_str):
        """
        Get/set VFO-B operating mode.
        """
        resp = self.swapvfo_cmd()
        if (resp == PyRigCat.OK):
            resp = self.op_mode_cmd(mode_str)
            self.swapvfo_cmd()
        return resp
        
    # ------------------------------------------------------------------------
    def power_level_cmd(self, level_str):
        """
        Get/set the RF power level.  Must be in the range 5 - 100.
        """
        resp = ''
        
        # Sanity check the RF power level argument.
        if (len(level_str) > 0):
            if level_str.isnumeric(): 
                level_pct = int(level_str)
                if (level_pct < 5) or (level_pct > 100):
                    resp = PyRigCat.ERROR
                else:
                    # Create and send the RF power level command.
                    cmd = 'PC' + str(level_pct).zfill(3) + ';'
                    resp = self.xcvr_cmd(cmd, 2)
                    if (resp == ''): resp = PyRigCat.OK
                    elif (resp == '?;'): resp = PyRigCat.ERROR
            else:
                resp = PyRigCat.ERROR
        else:
            # Get the RF power level.
            resp = self.xcvr_cmd('PC;', 6)
            if (resp == ''): resp = PyRigCat.OK
            elif (resp == '?;'): resp = PyRigCat.ERROR
            elif resp.startswith('PC'): resp = resp[2:5]
        return resp
    
    # ------------------------------------------------------------------------
    def ptt_cat(self, ptt_arg):
        """
        Perform transceiver-specific PTT CAT control.
        Turns the PTT ON/OFF, or returns the PTT state.
        Overrides the base class.
        
        Parameters
        ----------
        ptt_arg : str
            Empty string ('') returns the PTT state ('OFF' or 'ON')
            'ON' turns PTT on.
            'OFF' turns PTT off.
            Everything else returns an error.
        
        Returns
        -------
        resp : str
            The PTT state ('OFF' or 'ON') if ptt_arg=''
            'OK' if PTT state was set successfully.
            'ERROR' otherwise.
        """
        resp = PyRigCat.ERROR
        if (ptt_arg == 'OFF'):
            resp = self.xcvr_cmd('TX0;', 2)
        elif (ptt_arg == 'ON'):
            resp = self.xcvr_cmd('TX1;', 2)
        elif (ptt_arg == ''):
            resp = self.xcvr_cmd('TX;', 4)
        if (resp == ''):
            if (ptt_arg == 'OFF'): self._ptt_is_on = False
            elif (ptt_arg == 'ON'): self._ptt_is_on = True
            resp = PyRigCat.OK
        elif (resp == '?;'): resp = PyRigCat.ERROR
        elif (resp == 'TX0;'):
            self._ptt_is_on = False
            resp = 'OFF'
        elif (resp == 'TX1;'):
            self._ptt_is_on = True
            resp = 'ON'
        elif (resp == 'TX2;'):
            self._ptt_is_on = True
            resp = 'ON'
        return resp

    # ------------------------------------------------------------------------
    def speech_processor_cmd(self, onoff, level_str):
        """
        Get/set the speech processor level (0-100).
        onoff (if supplied) turns the speech processor 'OFF' or 'ON'.
        level_str (if supplied) is the speech processor level string (0 - 100).
        Returns 'OK', 'ERROR', or 'ON/OFF' + level
        Note that the operating mode must be SSB or AM.
        """
        resp = ''
        resp_onoff = ''
        resp_level = ''
        
        # Sanity check the monitor level.
        if (len(level_str) > 0):
            if level_str.isnumeric(): 
                level_pct = int(level_str)
                if (level_pct < 0) or (level_pct > 100):
                    resp_level = PyRigCat.ERROR
                else:
                    # Reformat as a 3-digit numeric string.
                    level_str = str(level_pct).zfill(3)
            else:
                resp_level = PyRigCat.ERROR
            if (resp_level == PyRigCat.ERROR): return PyRigCat.ERROR
        
        if (onoff == ''):
            # Get the speech processor ON/OFF status.
            resp_onoff = self.xcvr_cmd('PR0;', 5)
            if (resp_onoff == 'PR00;'): resp_onoff = 'OFF'
            elif (resp_onoff == 'PR01;'): resp_onoff = 'ON'
            elif (resp_onoff == '?;'): resp_onoff = PyRigCat.ERROR
            # Get the speech processor level.
            resp_level = self.xcvr_cmd('PL;', 6)
            if resp_level.startswith('PL'): resp_level = resp_level[2:5]
            elif (resp_level == '?;'): resp_level = PyRigCat.ERROR

        elif (onoff == 'OFF'):
            # Turn the speech processor off.
            resp_onoff = self.xcvr_cmd('PR00;', 2)
            if (resp_onoff == ''): resp_onoff = PyRigCat.OK
            elif (resp_onoff == '?;'): resp_onoff = PyRigCat.ERROR

        elif (onoff == 'ON'):
            # Turn the speech processor on.
            resp_onoff = self.xcvr_cmd('PR01;', 2)
            if (resp_onoff == ''): resp_onoff = PyRigCat.OK
            elif (resp_onoff == '?;'): resp_onoff = PyRigCat.ERROR
        else:
            resp_onoff = PyRigCat.ERROR

        # Exit if an error occurred.
        if (resp_onoff == PyRigCat.ERROR): return PyRigCat.ERROR
        elif (resp_level == PyRigCat.ERROR): return PyRigCat.ERROR
        
        # Set the speech processor level.
        if (len(level_str) > 0):
            cmd = 'PL' + level_str + ';'
            #print(cmd)
            resp_level = self.xcvr_cmd(cmd, 2)
            if (resp_level == ''): resp_level = PyRigCat.OK
            elif (resp_level == '?;'): resp_level = PyRigCat.ERROR
            
        resp = resp_onoff + ':' + resp_level
        return resp

    # ------------------------------------------------------------------------
    def split_cmd(self, split_onoff):
        """
        Get/set split operation.
        Assumes receive = VFO-A, transmit = VFO-B when split is on.
        split_onoff is an optional 'OFF' or 'ON' string.
        """
        resp = ''
        if (len(split_onoff) > 0):
            if (split_onoff == 'OFF'):  cmd = 'FT2;' # TX uses VFO-A
            elif (split_onoff == 'ON'): cmd = 'FT3;' # TX uses VFO-B
            else: return PyRigCat.ERROR
            resp = self.xcvr_cmd(cmd, 2)
        else:
            resp = self.xcvr_cmd('FT;', 4)
        if (resp == ''): resp = PyRigCat.OK
        elif (resp == '?;'): resp = PyRigCat.ERROR
        elif (resp == 'FT0;'): resp = 'OFF'
        elif (resp == 'FT1;'): resp = 'ON'
        return resp

    # ------------------------------------------------------------------------
    def swapvfo_cmd(self):
        """
        Swap VFO-A <--> VFO-B.
        """
        resp = self.xcvr_cmd('SV;', 2)
        if (resp == ''): resp = PyRigCat.OK
        elif (resp == '?;'): resp = PyRigCat.ERROR
        return resp
        
    # ------------------------------------------------------------------------
    def time_cmd(self, time_str):
        """
        Get/set the system UTC time.
        time_str is the UTC time in HHMMSS format.
        """
        resp = ''
        if (len(time_str) > 0):
            cmd = 'DT1' + time_str + ';'
            resp = self.xcvr_cmd(cmd, 2)
        else:
            resp = self.xcvr_cmd('DT1;', 10)
        if (resp == ''): resp = PyRigCat.OK
        elif (resp == '?;'): resp = PyRigCat.ERROR
        elif resp.startswith('DT1'):
            resp = resp[3:9]
        return resp

    # ------------------------------------------------------------------------
    def tone_cmd(self, mode, freq):
        """
        Set the repeater tone encoder/decoder mode and frequency.
        
        Parameters
        ----------
        mode : str
            The tone encoder/decoder mode:
            OFF = Encoder/decoder is off: no tone on transmit or receive
            ENC = Encoder on: send tone on transmit
            DEC = Decoder on: send tone on transmit; open squelch only when tone is received

        freq : str
            The CTCSS tone frequency in Hz * 10.
            e.g., 1318 = 131.8 Hz.
            Required if mode = ENC or DEC.
        """
        resp = PyRigCat.ERROR

        # Sanity check the mode.
        if (mode == 'OFF') or (mode == 'ENC') or (mode == 'DEC'):
            pass
        else:
            return resp # Invalid mode

        if (mode != 'OFF'):
            if not freq.isnumeric():
                return resp # Frequency must be supplied for ENC/DEC
                
        resp = self.tone_mode_cmd(mode)
        if (resp == PyRigCat.OK):
            if (mode == 'ENC') or (mode == 'DEC'):
                resp = self.tone_freq_cmd(freq)
        return resp
    
    # ------------------------------------------------------------------------
    def tone_freq_cmd(self, freq):
        """
        Set the CTCSS encode/decode tone frequency.
        
        Parameters
        ----------            
        freq : str
            The CTCSS tone frequency in Hz * 10.
            e.g., 1318 = 131.8 Hz.
        """
        global CTCSS_TONES
        
        if freq not in CTCSS_TONES.keys():
            return pyRigCat.ERROR
        
        cmd = 'CN00' + CTCSS_TONES[freq] + ';'
        resp = self.xcvr_cmd(cmd, 2)
        if (resp == ''): resp = PyRigCat.OK
        elif (resp == '?;'): resp = PyRigCat.ERROR
        #print('tone freq resp: "{}"'.format(resp))
        return resp

    # ------------------------------------------------------------------------
    def tone_mode_cmd(self, mode):
        """
        Set the repeater tone encoder/decoder mode.
        
        Parameters
        ----------
        mode : str
            The tone encoder/decoder mode:
            OFF = Encoder/decoder is off: no tone on transmit or receive
            ENC = Encoder on: send tone on transmit
            DEC = Decoder on: send tone on transmit; open squelch only when tone is received
        """
        cmd = 'CT0'
        if (mode == 'OFF'):
            # Encoder/decoder off: no tone
            cmd += '0;'
        elif (mode == 'ENC'):
            cmd += '2;'
        elif (mode == 'DEC'):
            cmd += '1;'
        else:
            return PyRigCat.ERROR 
        resp = self.xcvr_cmd(cmd, 2)
        if (resp == ''): resp = PyRigCat.OK
        elif (resp == '?;'): resp = PyRigCat.ERROR
        #print('tone mode resp: "{}"'.format(resp))
        return resp

    # ------------------------------------------------------------------------
    def setup_split(self, vfoa_hz, modea, split=False, vfob_hz=0, modeb=OperatingMode.UNKNOWN):
        """
        Perform transceiver-specific split operation setup.
        Transceivers can vary widely in the way they need to be setup for split operation.
        This provides a single method for setting up split operation so that applications 
        don't have to provide different combinations of individual CAT commands for different 
        transceivers.
        
        Parameters
        ----------
        vfoa_hz : int
            VFO-A frequency in Hz.
        modea : OperatingMode constant
            VFO-A operating mode.
        split : bool
            True if split operation is enabled, False if disabled.
        vfob_hz : int
            VFO-B frequency in Hz. Usually only needed if split=True.
        modeb : OperatingMode constant
            VFO-B operating mode. Usually only needed if split=True.
        
        Returns
        -------
        resp : str
            'OK' if split setup was successful.
            'ERROR' otherwise.
        """
        resp = PyRigCat.ERROR
        
        if split:
            # Split operation enabled.
            # Set VFO-B parameters into VFO-A.
            if OperatingMode.is_valid(modeb):
                resp = self.op_mode_cmd(modeb)
                if (resp != PyRigCat.OK): return resp
            if (vfob_hz > 0):
                resp = self.frequency_cmd(str(vfob_hz), vfo='A')
                if (resp != PyRigCat.OK): return resp
                
            # Swap VFO-A and VFO-B.
            # This allows the proper operating mode to be set for VFO-B.
            resp = self.swapvfo_cmd()
            if (resp != PyRigCat.OK): return resp
            
            # Set VFO-A parameters.
            if OperatingMode.is_valid(modea):
                resp = self.op_mode_cmd(modea)
                if (resp != PyRigCat.OK): return resp
            if (vfoa_hz > 0):
                resp = self.frequency_cmd(str(vfoa_hz), vfo='A')
                if (resp != PyRigCat.OK): return resp
                
            # Turn split operation on.
            resp = self.split_cmd('ON')

        else:
            # Split operation disabled.
            resp = self.split_cmd('OFF')
            if OperatingMode.is_valid(modea):
                self.op_mode_cmd(modea)
            if (vfoa_hz > 0):
                self.frequency_cmd(str(vfoa_hz), vfo='A')
        return resp
        
##############################################################################
# Functions.
############################################################################## 


##############################################################################
# Main program.
############################################################################## 
if __name__ == "__main__":
    print('PyRigCat_ft991 main program not implemented.')
