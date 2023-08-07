###############################################################################
# PyRigCat_icom.py
# Author: Tom Kerr AB3GY
#
# A python Computer Aided Tranceiver (CAT) module for amateur radio use.
# Implements a base class for CAT control of Icom transceivers.
# Reference: IC-7000 Operating Manual (used to develop this class)
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
    PttMethod, OperatingMode

##############################################################################
# IcomAddr class.
##############################################################################
class IcomAddr(object):
    """
    Icom radio hex addresses.
    """
    NONE   = 0x00
    IC703  = 0x68
    IC706  = 0x48
    IC706MKII = 0x4E
    IC718  = 0x5E
    IC725  = 0x28
    IC728  = 0x38
    IC729  = 0x3A
    IC735  = 0x04
    IC736  = 0x40
    IC737  = 0x3C
    IC738  = 0x44
    IC746  = 0x56
    IC746PRO = 0x66
    IC751  = 0x1C
    IC765  = 0x2C
    IC775  = 0x46
    IC781  = 0x26
    IC7000 = 0x70
    IC7100 = 0x88
    IC7200 = 0x76
    IC7300 = 0x94
    IC7600 = 0x7A
    IC7610 = 0x98
    IC7700 = 0x74
    IC7800 = 0x6A
    
##############################################################################
# PyRigCat_icom class.
##############################################################################
class PyRigCat_icom(PyRigCat):
    """
    CAT control class for the Icom transceivers.
    This is a subclass of the PyRigCat base class.
    """
    
    # ------------------------------------------------------------------------
    def __init__(self):
        """
        Class constructor.
        """
        super().__init__()        # Call the base class constructor
        self.NAME = 'Icom'        # Set transceiver name
        self.addr = IcomAddr.NONE # Icom transceiver hex address
        self._echo = True         # Commands are echoed
        self._vfo = 'A'           # The currently selected VFO (may not be accurate)
        self._split = 'OFF'       # The current split mode (may not be accurate)
    
    # ------------------------------------------------------------------------
    def _print_hex(self, buf):
        """
        Print a buffer of bytes as formatted hex characters
        """
        for b in buf:
            print(('%02X ' % b), end='')
        print()
    
    # ------------------------------------------------------------------------
    def __del__(self):
        """
        Class destructor.
        """
        super().__del__()  # Call the base class destructor

    # ------------------------------------------------------------------------
    def maxbyte_to_pct(self, val):
        """
        Convert a value in the range 0-255 to a percentage (0-100).
        """
        pct = int(round(100.0 * val / 255.0))
        return pct
    
    # ------------------------------------------------------------------------
    def pct_to_maxbyte(self, pct):
        """
        Convert a percentage in the range 0-100 to a byte value in the range 0-255.
        """
        val = int(round(pct * 255.0 / 100.0))
        return val

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
        # Try to parse the Icom transceiver command here.

        # Get/set the transceiver date.
        if (cmd_str == 'DATE'):
            date_str = ''
            if (len(arg_list) > 0): date_str = str(arg_list[0]).upper().strip()
            resp = self.date_cmd(date_str)

        # Get/set the currently selected VFO frequency.
        if (cmd_str == 'FREQ'):
            freq_hz = ''
            if (len(arg_list) > 0): freq_hz = str(arg_list[0]).strip()
            resp = self.frequency_cmd(freq_hz, '')

        # Get/set the VFO-A frequency.
        elif (cmd_str == 'FREQA'):
            freq_hz = ''
            if (len(arg_list) > 0): freq_hz = str(arg_list[0]).strip()
            resp = self.frequency_cmd(freq_hz, 'A')
        
        # Get/set the VFO-B frequency.
        elif (cmd_str == 'FREQB'):
            freq_hz = ''
            if (len(arg_list) > 0): freq_hz = str(arg_list[0]).strip()
            resp = self.frequency_cmd(freq_hz, 'B')
        
        # Get/set the current operating mode.
        elif (cmd_str == 'MODE'):
            mode_str = ''
            if (len(arg_list) > 0): mode_str = str(arg_list[0]).upper().strip()
            resp = self.mode_cmd(mode_str, '')
        
        # Get/set the operating mode associated with VFO-A.
        elif (cmd_str == 'MODEA'):
            mode_str = ''
            if (len(arg_list) > 0): mode_str = str(arg_list[0]).upper().strip()
            resp = self.mode_cmd(mode_str, 'A')
        
        # Get/set the operating mode associated with VFO-B.
        elif (cmd_str == 'MODEB'):
            mode_str = ''
            if (len(arg_list) > 0): mode_str = str(arg_list[0]).upper().strip()
            resp = self.mode_cmd(mode_str, 'B')
        
        # Get/set the monitor level.
        elif (cmd_str == 'MONITOR'):
            onoff = ''
            level = ''
            if (len(arg_list) > 0): onoff = str(arg_list[0]).upper().strip()
            if (len(arg_list) > 1): level = str(arg_list[1]).upper().strip()
            resp = self.monitor_level_cmd(onoff, level)
            
        # Get/set the noise blanker state.
        elif (cmd_str == 'NB'):
            onoff = ''
            if (len(arg_list) > 0): onoff = str(arg_list[0]).upper().strip()
            resp = self.noise_blanker_cmd(onoff)
        
        # Get/set the noise reduction state.
        elif (cmd_str == 'NR'):
            onoff = ''
            if (len(arg_list) > 0): onoff = str(arg_list[0]).upper().strip()
            resp = self.noise_reduction_cmd(onoff)
            
        # Get/set the RF power level.
        elif (cmd_str == 'POWER'):
            pwr_level = ''
            if (len(arg_list) > 0): pwr_level = str(arg_list[0]).strip()
            resp = self.power_level_cmd(pwr_level)

        # Get/set the preamp state.
        elif (cmd_str == 'PREAMP'):
            onoff = ''
            if (len(arg_list) > 0): onoff = str(arg_list[0]).upper().strip()
            resp = self.preamp_cmd(onoff)

        # Set the repeater offset in Hz.
        # Frequency can be positive or negative.
        # Zero sets simplex mode.
        elif (cmd_str == 'RPT-OFFSET'):
            freq = ''
            if (len(arg_list) > 0): freq = str(arg_list[0]).upper().strip()
            resp = self.rpt_offset_cmd(freq)

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
            resp = PyRigCat.ERROR
            split_onoff = ''
            if (len(arg_list) > 0): split_onoff = str(arg_list[0]).upper().strip()
            if (len(split_onoff) > 0):
                if (split_onoff == 'OFF'): split = False
                elif (split_onoff == 'ON'): split = True
                else: return resp
                resp = self.set_split(split)
            else:
                resp = self.get_split()

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
        
        # Get/set the current VFO in use (A/B).
        # Note that this does not set the frequency.
        elif (cmd_str == 'VFO'):
            vfo = ''
            if (len(arg_list) > 0): vfo = str(arg_list[0]).upper().strip()
            if (vfo == ''):
                resp = self.get_vfo()
            else:
                if (self.set_vfo(vfo)):
                    resp = PyRigCat.OK
                else:
                    resp = PyRigCat.ERROR
        
        # Set VFO or memory mode.
        elif (cmd_str == 'VFOMEM'):
            mode = ''
            if (len(arg_list) > 0): mode = str(arg_list[0]).upper().strip()
            resp = self.vfomem_cmd(mode)

        return resp

    # ------------------------------------------------------------------------
    def xcvr_cmd(self, cmd, scmd=None, scmd_list=[], data=[], max_data=100000):
        """
        Common method to send a CAT command to the transceiver and receive a response.
        
        Parameters
        ----------
        cmd : byte or int
            The binary command byte.
        scmd : byte or int
            The binary subcommand byte.
        scmd_list : list of ints
            List of subcommand bytes. Used when the subcommand is larger than one
            byte. This is typically mutually exclusive with the scmd parameter.
        data : list of bytes
            Command-specific additional data.
        max_data : int
            The maximum number of data bytes to read after sending the command.
            Includes only the data area of the command to return to the caller, but
            might also include subcommand echo depending on the command.
            Excludes command echo, preamble, addresses, command and end of message code.
        
        Returns
        -------
        (status, response)
        status : bool
            True if command completed successfully, False otherwise.
        response : list of ints
            The data area portion of response as a list of integers.
        """
        status = False
        resp = bytes()
        
        # Build the command array.
        # Note that there are 7 overhead bytes in addition to the data array.
        cmd_list = [0xFE, 0xFE, self.addr, 0xE0, cmd]
        if scmd is not None:
            cmd_list.append(scmd)
        for s in scmd_list:
            cmd_list.append(s)
        for d in data:
            cmd_list.append(d)
        cmd_list.append(0xFD)
        send_buf = bytearray(cmd_list)
        send_len = len(send_buf)
        
        #print('send: ', end='')
        #self._print_hex(send_buf)

        # Send the command.
        sent = self._serial_write(send_buf)
        if (sent == send_len):
            # Get the response.
            # Expecting 6 overhead bytes.
            ovhd = 6
            if self._echo: ovhd += send_len 
            max_read = max_data + ovhd
            resp_buf = self._serial_read(max_read) # Get response
            resp_len = len(resp_buf)
            #print('resp: ', end='')
            #self._print_hex(resp_buf)
            if (resp_len > ovhd):
                # Extract data portion of response.
                idx = ovhd-1
                resp = resp_buf[idx:idx+max_data]

            # See if we got the whole response.
            if (resp_len >= max_read) and (resp_buf[-1] == 0xFD):
                status = True
        return (status, list(resp))

    # ------------------------------------------------------------------------
    def date_cmd(self, date_str):
        """
        Get/set the system date.
        date_str is the date in YYYYMMDD format.
        """
        resp = PyRigCat.ERROR
        bcd = [0, 0, 0, 0, 0, 0, 0, 0]
        send_data = [0, 0]
        scmd_year = [0x05, 0x00, 0x39]
        scmd_date = [0x05, 0x00, 0x40]
        if (len(date_str) >= 8):
            # Convert date to integers.
            for i in range(8):
                bcd[i] = int(date_str[i])
            # Set the year.
            send_data[0] = (bcd[0] * 16) + bcd[1]
            send_data[1] = (bcd[2] * 16) + bcd[3]
            (ok, rcv_data) = self.xcvr_cmd(cmd=0x1A, scmd_list=scmd_year, data=send_data, max_data=0)
            if ok:
                # Set the date.
                send_data[0] = (bcd[4] * 16) + bcd[5]
                send_data[1] = (bcd[6] * 16) + bcd[7]
                (ok, rcv_data) = self.xcvr_cmd(cmd=0x1A, scmd_list=scmd_date, data=send_data, max_data=0)
                if ok: resp = PyRigCat.OK
        else:
            (ok, rcv_data) = self.xcvr_cmd(cmd=0x1A, scmd_list=scmd_year, max_data=5)
            if ok:
                bcd[0] = (rcv_data[3] & 0xF0) >> 4
                bcd[1] = (rcv_data[3] & 0x0F)
                bcd[2] = (rcv_data[4] & 0xF0) >> 4
                bcd[3] = (rcv_data[4] & 0x0F)
                (ok, rcv_data) = self.xcvr_cmd(cmd=0x1A, scmd_list=scmd_date, max_data=5)
                if ok:
                    bcd[4] = (rcv_data[3] & 0xF0) >> 4
                    bcd[5] = (rcv_data[3] & 0x0F)
                    bcd[6] = (rcv_data[4] & 0xF0) >> 4
                    bcd[7] = (rcv_data[4] & 0x0F)
                    resp = ''
                    for i in range(len(bcd)):
                        resp += str(bcd[i])
        return resp

    # ------------------------------------------------------------------------
    def frequency_cmd(self, freq_hz_str, vfo):
        """
        Get/set the transceiver frequency from/to the specified VFO (A/B).
        """
        resp = PyRigCat.ERROR
        
        freq_hz = 0
        if (len(freq_hz_str) > 0):
            if freq_hz_str.isnumeric():
                freq_hz = int(freq_hz_str)
            else:
                return resp

        # Set the VFO.
        vfo_ok = True
        saved_vfo = self.get_vfo()
        if (vfo == 'A') and (saved_vfo == 'B'):
            vfo_ok = self.set_vfo('A')
        elif (vfo == 'B') and (saved_vfo == 'A'):
            vfo_ok = self.set_vfo('B')
        
        if vfo_ok:
            if (freq_hz > 0):
                # Set the VFO frequency.
                freq_ok = self.set_frequency_hz(freq_hz)
                if freq_ok: resp = PyRigCat.OK
            else:
                # Get the VFO frequency.
                freq_hz = self.get_frequency_hz()
                if (freq_hz > 0):
                    resp = str(freq_hz).zfill(9)                

        # Reset the VFO.
        if vfo_ok:
            if (len(vfo) > 0) and (vfo != saved_vfo):
                self.set_vfo(saved_vfo)

        return resp

    # ------------------------------------------------------------------------
    def get_frequency_hz(self):
        """
        Return the rig frequency as an integer in Hz.
        """
        freq_hz = 0
        mult = 1
            
        # Get the VFO frequency.
        (ok, data) = self.xcvr_cmd(cmd=0x03, max_data=5)
        if ok:
            # Format the frequency.
            for i in range(len(data)):
                bcd = (data[i] & 0x0F)
                freq_hz += bcd * mult
                mult *= 10
                bcd = (data[i] & 0xF0) >> 4
                freq_hz += bcd * mult
                mult *= 10
        return freq_hz

    # ------------------------------------------------------------------------
    def set_frequency_hz(self, freq):
        """
        Set the rig frequency in Hz.
        Returns True if successful, False otherwise.
        """
        ok = False
        digits = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        freq = int(freq)
        
        # Range check the frequency.
        if (freq < 100000) or (freq > 450000000): return False
        
        # Break frequency into individual BCD digits.
        div = 1000000000
        for i in range(len(digits)):
            d = int(freq / div)
            freq -= d * div
            digits[i] = d
            div /= 10

        # Construct the command data from the BCD digits.
        data = [0, 0, 0, 0, 0]
        i = len(digits) - 1
        while (i > 0):
            d = digits[i]
            i -= 1
            d += digits[i] * 16
            data[i//2] = d
            i -= 1
        
        # Send the command.
        (ok, data) = self.xcvr_cmd(cmd=0x05, data=reversed(data), max_data=0)
        return ok

    # ------------------------------------------------------------------------
    def mode_cmd(self, mode_str, vfo):
        """
        Get/set the operating mode associated with the specified VFO (A/B).
        """
        resp = PyRigCat.ERROR
        saved_vfo = ''
        
        # Check the mode string.
        if (len(mode_str) > 0):
            if not OperatingMode.is_valid(mode_str): return resp
        
        # Check the VFO.
        if (len(vfo) > 0):
            if (vfo == 'A') or (vfo == 'B'):
                saved_vfo = self._vfo
            else:
                return resp # Invalid VFO
        
            # Change to the specified VFO.
            ok = self.set_vfo(vfo)
            if not ok: return resp # Command error
        
        # Get/set the operating mode.
        if (len(mode_str) > 0):
            # Set the operating mode.
            ok = self.set_mode(mode_str)
            if ok: resp = PyRigCat.OK
        else:
            # Get the operating mode.
            mode = self.get_mode()
            if (mode != OperatingMode.UNKNOWN):
                resp = mode

        # Restore the original VFO.
        if (len(saved_vfo) > 0):
            ok = self.set_vfo(saved_vfo)
            if not ok: resp = PyRigCat.ERROR

        return resp

    # ------------------------------------------------------------------------
    def get_mode(self):
        """
        Return the rig operating mode as an OperatingMode attribute.
        """
        mode = OperatingMode.UNKNOWN
        (ok, data) = self.xcvr_cmd(cmd=0x04, max_data=2)
        if ok:
            mode_val = data[0]
            if (mode_val == 0): mode = OperatingMode.LSB
            elif (mode_val == 1): mode = OperatingMode.USB
            elif (mode_val == 2): mode = OperatingMode.AM
            elif (mode_val == 3): mode = OperatingMode.CW
            elif (mode_val == 4): mode = OperatingMode.RTTY
            elif (mode_val == 5): mode = OperatingMode.FM
            elif (mode_val == 7): mode = OperatingMode.CW_R
            elif (mode_val == 8): mode = OperatingMode.RTTY_R
        return mode

    # ------------------------------------------------------------------------
    def set_mode(self, mode):
        """
        Set the rig mode.
        The mode is passed as an OperatingMode attribute.
        Returns True if successful, False otherwise.
        """
        mode_ok = False
        scmd = 0
        if mode == OperatingMode.LSB:
            scmd = 0
            mode_ok = True
        elif mode == OperatingMode.USB:
            scmd = 1
            mode_ok = True
        elif mode == OperatingMode.AM:
            scmd = 2
            mode_ok = True
        elif mode == OperatingMode.CW:
            scmd = 3
            mode_ok = True
        elif mode == OperatingMode.RTTY:
            scmd = 4
            mode_ok = True
        elif mode == OperatingMode.FM:
            scmd = 5
            mode_ok = True
        elif mode == OperatingMode.CW_R:
            scmd = 7
            mode_ok = True
        elif mode == OperatingMode.RTTY_R:
            scmd = 8
            mode_ok = True
        elif mode == OperatingMode.DATA_LSB:
            if not self._has_data_modes:
                scmd = 0
                mode_ok = True
        elif mode == OperatingMode.DATA_USB:
            if not self._has_data_modes:
                scmd = 1
                mode_ok = True
        elif mode == OperatingMode.DATA_FM:
            if not self._has_data_modes:
                scmd = 5
                mode_ok = True
        
        ok = False
        if mode_ok:
            (ok, data) = self.xcvr_cmd(cmd=0x06, scmd=scmd, max_data=0)
        return ok

    # ------------------------------------------------------------------------
    def monitor_level_cmd(self, onoff, level_str):
        """
        Get/set the monitor level (0-100).
        onoff (if supplied) turns the monitor 'OFF' or 'ON'.
        level_str (if supplied) is the monitor level string (0 - 100).
        Returns 'OK', 'ERROR', or 'ON/OFF' + level
        """
        resp = PyRigCat.ERROR
        resp_onoff = PyRigCat.ERROR
        resp_level = PyRigCat.ERROR
        
        # Sanity check the monitor level.
        level_pct = 0
        if (len(level_str) > 0):
            if level_str.isnumeric(): 
                level_pct = int(level_str)
                if (level_pct < 0) or (level_pct > 100):
                    return resp  # Invalid monitor level

        if (onoff == ''):
            resp_onoff = self.get_monitor_onoff()
            resp_level = self.get_monitor_level()

        elif (onoff == 'OFF'):
            ok = self.set_monitor_onoff(onoff)
            if ok:
                resp_onoff = PyRigCat.OK
                resp_level = PyRigCat.OK

        elif (onoff == 'ON'):
            ok = self.set_monitor_onoff(onoff)
            if ok:
                resp_onoff = PyRigCat.OK
                ok = self.set_monitor_level(level_pct)
            if ok:
                resp_level = PyRigCat.OK
        else:
            return resp  # Invalid onoff parameter

        resp = resp_onoff + ':' + resp_level
        return resp

    # ------------------------------------------------------------------------
    def get_monitor_onoff(self):
        """
        Get the monitor state (OFF/ON/ERROR)
        """
        resp = PyRigCat.ERROR
        (ok, data) = self.xcvr_cmd(cmd=0x1A, scmd_list=[0x05, 0x00, 0x45], max_data=4)
        if ok:
            if (data[3] == 0): resp = 'OFF'
            elif (data[3] == 1): resp = 'ON'
        return resp
    
    # ------------------------------------------------------------------------
    def set_monitor_onoff(self, onoff):
        """
        Set the monitor state (OFF/ON)
        """
        enable = 0
        if (onoff == 'OFF'):
            enable = 0
        elif (onoff == 'ON'):
            enable = 1
        else:
            return False # Invalid parameter
        (ok, data) = self.xcvr_cmd(cmd=0x1A, scmd_list=[0x05, 0x00, 0x45, enable], max_data=0)
        return ok

    # ------------------------------------------------------------------------
    def get_monitor_level(self):
        """
        Get the monitor level as a percentage (0 - 100)
        """
        level_pct = 0
        (ok, data) = self.xcvr_cmd(cmd=0x1A, scmd_list=[0x05, 0x00, 0x46], max_data=5)
        if ok:
            # Convert BCD digits to monitor level percent.
            mon_lvl =  ((data[3] & 0x0F) * 100)
            mon_lvl += ((data[4] & 0xF0) >> 4) * 10
            mon_lvl += (data[4] & 0x0F)
            level_pct = self.maxbyte_to_pct(mon_lvl)
        return str(level_pct)
    
    # ------------------------------------------------------------------------
    def set_monitor_level(self, level_pct):
        """
        Set the monitor level.
        """
        # Break monitor level into individual BCD digits.
        mon_lvl = self.pct_to_maxbyte(level_pct)
        digits = self.int_to_bcd(mon_lvl, 255)
        # Create the monitor level data for the command.
        scmd_list = [0x05, 0x00, 0x46, 0, 0]
        scmd_list[3] = digits[0]
        scmd_list[4] = (digits[1] * 16) + digits[2]
        # Set the monitor level.
        (ok, data) = self.xcvr_cmd(cmd=0x1A, scmd_list=scmd_list, max_data=0)
        return ok

    # ------------------------------------------------------------------------
    def noise_blanker_cmd(self, onoff):
        """
        Get/set the noise blanker state.
        """
        resp = PyRigCat.ERROR
        
        if (onoff == ''):
            (ok, data) = self.xcvr_cmd(cmd=0x16, scmd=0x22, max_data=2)
            if ok:
                if (data[1] == 0): resp = 'OFF'
                elif (data[1] == 1): resp = 'ON'
        elif (onoff == 'OFF'):
            (ok, data) = self.xcvr_cmd(cmd=0x16, scmd=0x22, data=[0], max_data=0)
            if ok: resp = PyRigCat.OK
        elif (onoff == 'ON'):
            (ok, data) = self.xcvr_cmd(cmd=0x16, scmd=0x22, data=[1], max_data=0)
            if ok: resp = PyRigCat.OK
        else:
            return resp  # Invalid ONOFF parameter
        
        return resp
    
    # ------------------------------------------------------------------------
    def noise_reduction_cmd(self, onoff):
        """
        Get/set the noise reduction state.
        """
        resp = PyRigCat.ERROR
        
        if (onoff == ''):
            (ok, data) = self.xcvr_cmd(cmd=0x16, scmd=0x40, max_data=2)
            if ok:
                if (data[1] == 0): resp = 'OFF'
                elif (data[1] == 1): resp = 'ON'
        elif (onoff == 'OFF'):
            (ok, data) = self.xcvr_cmd(cmd=0x16, scmd=0x40, data=[0], max_data=0)
            if ok: resp = PyRigCat.OK
        elif (onoff == 'ON'):
            (ok, data) = self.xcvr_cmd(cmd=0x16, scmd=0x40, data=[1], max_data=0)
            if ok: resp = PyRigCat.OK
        else:
            return resp  # Invalid ONOFF parameter
        
        return resp

    # ------------------------------------------------------------------------
    def power_level_cmd(self, level_str):
        """
        Get/set the RF power level.
        
        Parameters
        ----------
        level_str : str
            The RF power level as a percentage of full power (0 - 100)
        
        Returns
        -------
        resp : str
            The RF power level (0-100) as a string if getting the RF power level
            PyRigCat.OK or PyRigCat.ERROR if setting the power level
        """
        resp = PyRigCat.ERROR
        level_pct = 0

        # Sanity check the RF power level argument.
        if (len(level_str) > 0):
            if level_str.isnumeric(): 
                level_pct = int(level_str)
                if (level_pct < 0) or (level_pct > 100):
                    resp = PyRigCat.ERROR
                else:
                    ok = self.set_power_level(level_pct)
                    if ok: resp = PyRigCat.OK
            else:
                resp = PyRigCat.ERROR
        else:
            # Get the RF power level.
            lvl_pct = self.get_power_level()
            resp = str(lvl_pct)
        return resp

   # ------------------------------------------------------------------------
    def get_power_level(self):
        """
        Get the RF power level as a percentage (0 - 100)
        """
        level_pct = 0
        (ok, data) = self.xcvr_cmd(cmd=0x14, scmd=0x0A, max_data=3)
        if ok:
            # Convert BCD digits to power level percent.
            pwr_lvl =  ((data[1] & 0x0F) * 100)
            pwr_lvl += ((data[2] & 0xF0) >> 4) * 10
            pwr_lvl += (data[2] & 0x0F)
            level_pct = self.maxbyte_to_pct(pwr_lvl)
        return level_pct

   # ------------------------------------------------------------------------
    def set_power_level(self, level_pct):
        """
        Set the RF power level.
        """
        pwr_lvl = self.pct_to_maxbyte(level_pct)
        # Break power level into individual BCD digits.
        digits = self.int_to_bcd(pwr_lvl, 255)
        scmd_list = [0x0A, 0, 0]
        scmd_list[1] = digits[0]
        scmd_list[2] = (digits[1] * 16) + digits[2]
        # Set the power level.
        (ok, data) = self.xcvr_cmd(cmd=0x14, scmd_list=scmd_list, max_data=0)
        return ok

    # ------------------------------------------------------------------------
    def preamp_cmd(self, onoff):
        """
        Get/set the preamp state.
        """
        resp = PyRigCat.ERROR
        
        if (onoff == ''):
            (ok, data) = self.xcvr_cmd(cmd=0x16, scmd=0x02, max_data=2)
            if ok:
                if (data[1] == 0): resp = 'OFF'
                elif (data[1] == 1): resp = 'ON'
        elif (onoff == 'OFF'):
            (ok, data) = self.xcvr_cmd(cmd=0x16, scmd=0x02, data=[0], max_data=0)
            if ok: resp = PyRigCat.OK
        elif (onoff == 'ON'):
            (ok, data) = self.xcvr_cmd(cmd=0x16, scmd=0x02, data=[1], max_data=0)
            if ok: resp = PyRigCat.OK
        else:
            return resp  # Invalid ONOFF parameter
        
        return resp

    # ------------------------------------------------------------------------
    def speech_processor_cmd(self, onoff, level_str):
        """
        Get/set the speech processor level (0-100).
        onoff (if supplied) turns the speech processor 'OFF' or 'ON'.
        level_str (if supplied) is the speech processor level string (0 - 100).
        Returns 'OK', 'ERROR', or 'ON/OFF' + level
        """
        resp = PyRigCat.ERROR
        resp_onoff = PyRigCat.ERROR
        resp_level = PyRigCat.ERROR
        
        # Sanity check the speech level.
        level_pct = 0
        if (len(level_str) > 0):
            if level_str.isnumeric(): 
                level_pct = int(level_str)
                if (level_pct < 0) or (level_pct > 100):
                    return resp  # Invalid speech level

        if (onoff == ''):
            resp_onoff = self.get_speech_onoff()
            resp_level = self.get_speech_level()

        elif (onoff == 'OFF'):
            ok = self.set_speech_onoff(onoff)
            if ok:
                resp_onoff = PyRigCat.OK
                resp_level = PyRigCat.OK

        elif (onoff == 'ON'):
            ok = self.set_speech_onoff(onoff)
            if ok:
                resp_onoff = PyRigCat.OK
                ok = self.set_speech_level(level_pct)
            if ok:
                resp_level = PyRigCat.OK
        else:
            return resp  # Invalid onoff parameter

        resp = resp_onoff + ':' + resp_level
        
        return resp

    # ------------------------------------------------------------------------
    def get_speech_onoff(self):
        """
        Get the speech processor state (OFF/ON/ERROR)
        """
        resp = PyRigCat.ERROR
        (ok, data) = self.xcvr_cmd(cmd=0x16, scmd=0x44, max_data=2)
        if ok:
            if (data[1] == 0): resp = 'OFF'
            elif (data[1] == 1): resp = 'ON'
        return resp
    
    # ------------------------------------------------------------------------
    def set_speech_onoff(self, onoff):
        """
        Set the speech processor state (OFF/ON)
        """
        enable = 0
        if (onoff == 'OFF'):
            enable = 0
        elif (onoff == 'ON'):
            enable = 1
        else:
            return False # Invalid parameter
        (ok, data) = self.xcvr_cmd(cmd=0x16, scmd=0x44, data=[enable], max_data=0)
        return ok

    # ------------------------------------------------------------------------
    def get_speech_level(self):
        """
        Get the speech processor level as a percentage (0 - 100)
        """
        level_pct = 0
        (ok, data) = self.xcvr_cmd(cmd=0x1A, scmd_list=[0x05, 0x00, 0x94], max_data=4)
        if ok:
            print(data)
            if (data[3] >= 0x10): 
                level_pct = 100
            else:
                level_pct = data[3] * 10
        return str(level_pct)
    
    # ------------------------------------------------------------------------
    def set_speech_level(self, level_pct):
        """
        Set the speech processor level.
        """
        # Convert speech level from 0 - 100 to 0 - 10.
        spch_lvl = int(level_pct / 10)
        if (spch_lvl >= 10): spch_lvl = 0x10
        scmd_list = [0x05, 0x00, 0x94, spch_lvl]
        # Set the power level.
        (ok, data) = self.xcvr_cmd(cmd=0x1A, scmd_list=scmd_list, max_data=0)
        return ok

    # ------------------------------------------------------------------------
    def get_split(self):
        """
        Return the split mode status.
        True = split mode on, False = split mode off
        """
        # Icom transceivers have no command to read the split mode directly.
        # This may not be accurate unless split mode was explicitly set/unset.
        return self._split

    # ------------------------------------------------------------------------
    def set_split(self, split=False):
        """
        Turn split mode on/off.
        
        Parameters
        ----------
        split : bool
            True = split mode on, False = split mode off
        
        Returns
        -------
        resp : str
            PyRigCat.OK if successful, PyRigCat.ERROR otherwise
        """
        resp = PyRigCat.ERROR
        scmd = 0x00 # Initialize to split OFF
        if split: scmd = 0x01 # Split ON
        (ok, data) = self.xcvr_cmd(cmd=0x0F, scmd=scmd, max_data=0)
        if ok: resp = PyRigCat.OK
        return resp
    
    # ------------------------------------------------------------------------
    def get_vfo(self):
        """
        Return the currently selected VFO.  Returns 'A' for VFO-A, 'B' for VFO-B.
        """
        # Icom transceivers have no command to read the VFO directly.
        # This may not be accurate unless VFO was explicitly set.
        return self._vfo

    # ------------------------------------------------------------------------
    def set_vfo(self, vfo):
        """
        Set the VFO in use.  Argument is 'A' for VFO-A, 'B' for VFO-B.
        """
        ok = False
        scmd = 0x00
        if (vfo == 'A'):
            scmd = 0x00
        elif (vfo == 'B'):
            scmd = 0x01
        else:
            return False  # Invalid VFO
        
        (ok, data) = self.xcvr_cmd(cmd=0x07, scmd=scmd, max_data=0)
        if ok:
            if (vfo == 'A'): self._vfo = 'A'
            else: self._vfo = 'B'
        return ok

    # ------------------------------------------------------------------------
    def rpt_shift_cmd(self, shift):
        """
        Set the repeater shift.
        
        Parameters
        ----------
        shift : str
            The repeater shift.  
            Should be one of the following: '-', '+', or '0'
        """
        resp = PyRigCat.ERROR
        scmd = 0x10
        if (shift == '-'):
            scmd = 0x11     # Negative shift (-DUP)
        elif (shift == '+'):
            scmd = 0x12     # Positive shift (+DUP)
        elif (shift == '0'):
            scmd = 0x10     # Simplex mode
        else:
            return resp     # Invalid shift argument
        
        (ok, data) = self.xcvr_cmd(cmd=0x0F, scmd=scmd, max_data=0)
        if ok: resp = PyRigCat.OK
        return resp
    
    # ------------------------------------------------------------------------
    def rpt_offset_cmd(self, freq):
        """
        Set the repeater offset in Hz.
        
        Standard offsets are -500 KHz on 6 meters, +/- 600 KHz on 2 meters,
        -1.6 MHz on 1.25 meters and +/- 5 MHz on 70cm.
        
        Parameters
        ----------
        freq : str
            The repeater offset frequency in Hz.  Can be positive or negative.
            Maximum offset is +/- 10MHz.
            Zero sets simplex mode.
            
        """
        resp = PyRigCat.ERROR
        shift = '+'
        
        # Check the offset frequency.
        freq_ok = False
        ifreq = 0
        try:
            ifreq = int(freq)
            if (ifreq >= -9999999) and (ifreq <= 9999999):
                freq_ok = True
        except Exception:
            pass
        if not freq_ok: return resp
        
        # Get current VFO frequency.
        freq_hz = self.get_frequency_hz()
        if (freq_hz == 0): return resp
        
        # Check for simplex mode.
        if (ifreq == 0):
            resp = self.rpt_shift_cmd('0')
            return resp
        
        # Check for negative shift.
        if (ifreq < 0):
            shift = '-'
            ifreq = abs(ifreq)
        
        # Set the repeater shift.
        shift_ok = (self.rpt_shift_cmd(shift) == PyRigCat.OK)
        if not shift_ok: return resp
        
        # Create the offset subcommand based on the VFO frequency.
        scmd_list = [0x05, 0x00, 0x00]
        if (freq_hz < 50000000):    # HF
            scmd_list[2] = 0x55
        elif (freq_hz < 144000000): # 50 MHz
            scmd_list[2] = 0x56
        elif (freq_hz < 430000000): # 144 MHz
            scmd_list[2] = 0x57
        else:                       # 430 MHz
            scmd_list[2] = 0x58

        # Construct the offset data structure from BCD digits.
        digits = self.int_to_bcd((ifreq / 100), 999999)
        offset = [0, 0, 0, 0]
        if (shift == '-'): offset[3] = 0x01
        offset[0] = (digits[4] * 16) + digits[5]
        offset[1] = (digits[2] * 16) + digits[3]
        offset[2] = (digits[0] * 16) + digits[1]
        
        (ok, data) = self.xcvr_cmd(cmd=0x1A, scmd_list=scmd_list, data=offset, max_data=0)
        if ok: resp = PyRigCat.OK
        return resp

    # ------------------------------------------------------------------------
    def time_cmd(self, time_str):
        """
        Get/set the system UTC time.
        time_str is the UTC time in HHMM or HHMMSS format (seconds are ignored).
        """
        resp = PyRigCat.ERROR
        
        bcd = [0, 0, 0, 0]
        send_data = [0, 0]
        scmd_time = [0x05, 0x00, 0x41]
        if (len(time_str) >= 4):
            # Convert date to integers.
            for i in range(4):
                bcd[i] = int(time_str[i])
            # Set the time.
            send_data[0] = (bcd[0] * 16) + bcd[1]
            send_data[1] = (bcd[2] * 16) + bcd[3]
            (ok, rcv_data) = self.xcvr_cmd(cmd=0x1A, scmd_list=scmd_time, data=send_data, max_data=0)
            if ok: resp = PyRigCat.OK
        else:
            (ok, rcv_data) = self.xcvr_cmd(cmd=0x1A, scmd_list=scmd_time, max_data=5)
            if ok:
                bcd[0] = (rcv_data[3] & 0xF0) >> 4
                bcd[1] = (rcv_data[3] & 0x0F)
                bcd[2] = (rcv_data[4] & 0xF0) >> 4
                bcd[3] = (rcv_data[4] & 0x0F)
                resp = ''
                for i in range(len(bcd)):
                    resp += str(bcd[i])
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
        
        enc_freq_ok = True
        dec_freq_ok = True
        mode_ok = self.tone_mode_cmd(mode)
        if mode_ok:
            if (mode == 'ENC'):
                enc_freq_ok = self.tone_freq_cmd(0, freq)
            elif (mode == 'DEC'):
                enc_freq_ok = self.tone_freq_cmd(0, freq)
                dec_freq_ok = self.tone_freq_cmd(1, freq)
                
        if mode_ok and enc_freq_ok and dec_freq_ok:
            resp = PyRigCat.OK
        return resp

    # ------------------------------------------------------------------------
    def tone_freq_cmd(self, type, freq):
        """
        Set the CTCSS encode/decode tone frequency.
        
        Parameters
        ----------
        type : int
            Set to 0 for tone on transmit
            Set to 1 for tone on receive
            
        freq : str
            The CTCSS tone frequency in Hz * 10.
            e.g., 1318 = 131.8 Hz.
        """
        # Check the tone frequency.
        freq_ok = False
        ifreq = 0
        try:
            ifreq = int(freq)
            if (ifreq >= 670) and (ifreq <= 2541):
                freq_ok = True
        except Exception:
            pass
        if not freq_ok: return False
        
        # Break frequency into individual BCD digits.
        digits = self.int_to_bcd(ifreq, 2541)
        #print(digits)

        # Construct the tone frequency data from the BCD digits.
        tone_data = [0, 0, 0]
        tone_data[1] = (digits[0] * 16) + digits[1]
        tone_data[2] = (digits[2] * 16) + digits[3]
        
        # Send the tone frequency command.
        (ok, data) = self.xcvr_cmd(cmd=0x1B, scmd=type, data=tone_data, max_data=0)
        return ok

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
        tone_enable = 0
        tsql_enable = 0
        if (mode == 'OFF'):
            # Encoder/decoder off: no tone
            tone_enable = 0
            tsql_enable = 0
        elif (mode == 'ENC'):    
            # Encoder on: tone on transmit
            tone_enable = 1
            tsql_enable = 0
        elif (mode == 'DEC'):   
            # Decoder on: tone on transmit and receive
            tone_enable = 1
            tsql_enable = 1
        else:
            return False  # Invalid argument
        (tone_ok, data) = self.xcvr_cmd(cmd=0x16, scmd=0x42, data=[tone_enable], max_data=0)
        (tsql_ok, data) = self.xcvr_cmd(cmd=0x16, scmd=0x43, data=[tsql_enable], max_data=0)
        return (tone_ok and tsql_ok)

    # ------------------------------------------------------------------------
    def vfomem_cmd(self, mode):
        """
        Set VFO or memory mode.
        """
        resp = PyRigCat.ERROR
        cmd = 0x07
        if (mode == 'VFO'):
            cmd = 0x07
        elif (mode == 'MEM'):
            cmd = 0x08
        else:
            return resp # Invalid parameter
        (ok, data) = self.xcvr_cmd(cmd=cmd, max_data=0)
        if ok: resp = PyRigCat.OK
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
        data = []
        max_data = 2
        if (ptt_arg == 'OFF'): 
            data = [0]
            max_data = 0
        elif (ptt_arg == 'ON'): 
            data = [1]
            max_data = 0
        elif (ptt_arg != ''): 
            return resp  # Invalid ptt_arg
        
        (ok, data) = self.xcvr_cmd(cmd=0x1C, scmd=0x00, data=data, max_data=max_data)
        if ok:
            if (ptt_arg == ''):
                if (data[1] == 0): resp = 'OFF'
                elif (data[1] == 1): resp = 'ON'
            else:
                resp = PyRigCat.OK
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
        
        # Select VFO B.
        ok = self.set_vfo('B')
        if not ok: return PyRigCat.ERROR
        
        # Set VFO-B frequency.
        if (vfob_hz > 0):
            ok = self.set_frequency_hz(vfob_hz)
            if not ok: return PyRigCat.ERROR
        
        # Set VFO-B mode.
        if OperatingMode.is_valid(modeb):
            ok = self.set_mode(modeb)
            if not ok: return PyRigCat.ERROR
        
        # Select VFO A.
        ok = self.set_vfo('A')
        if not ok: return PyRigCat.ERROR
        
        # Set VFO-A frequency.
        if (vfoa_hz > 0):
            ok = self.set_frequency_hz(vfoa_hz)
            if not ok: return PyRigCat.ERROR
            
        # Set VFO-A mode.
        if OperatingMode.is_valid(modea):
            ok = self.set_mode(modea)
            if not ok: return PyRigCat.ERROR
        
        # Enable/disable split operation.
        resp = self.set_split(split)
        return resp


##############################################################################
# Functions.
############################################################################## 


##############################################################################
# Main program.
############################################################################## 
if __name__ == "__main__":
    print('PyRigCat_icom main program not implemented.')
