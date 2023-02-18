###############################################################################
# PyRigCat_ft817.py
# Author: Tom Kerr AB3GY
#
# A python Computer Aided Tranceiver (CAT) module for amateur radio use.
# Implements CAT control for the Yaesu FT-817 transceiver.
# Reference: Yaesu FT-817 Operating Manual
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
# PyRigCat_ft817 class.
##############################################################################
class PyRigCat_ft817(PyRigCat):
    """
    CAT control class for the Yaesu FT-817 transceiver.
    This is a subclass of the PyRigCat base class.
    """
    
    # ------------------------------------------------------------------------
    def __init__(self):
        """
        Class constructor.
        """
        super().__init__()   # Call the base class constructor
        self.NAME = 'FT-817' # Set transceiver name
    
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
        # Parse the trasceiver-specific command here.
        
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

        # Turn RIT (clarifier) on/off.
        elif (cmd_str == 'RIT') or (cmd_str == 'CLAR'):
            rit_onoff = ''
            if (len(arg_list) > 0): rit_onoff = str(arg_list[0]).upper().strip()
            resp = self.rit_cmd(rit_onoff)
        
        # Set the RIT (clarifier) frequency.
        elif (cmd_str == 'RIT-FREQ') or (cmd_str == 'CLAR-FREQ'):
            freq = ''
            if (len(arg_list) > 0): freq = str(arg_list[0]).strip()
            resp = self.rit_freq_cmd(freq)
        
        # Get the Rx status.
        elif (cmd_str == 'RX-STATUS'):
            resp = self.get_rx_status()
        
        # Get the Tx status.
        elif (cmd_str == 'TX-STATUS'):
            resp = self.get_tx_status()
        
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
                
        # Set the repeater offset in Hz.
        # Frequency can be positive or negative.
        # Zero sets simplex mode.
        elif (cmd_str == 'RPT-OFFSET'):
            freq = ''
            if (len(arg_list) > 0): freq = str(arg_list[0]).upper().strip()
            resp = self.rpt_offset_cmd(freq)
        
        # Set the CTCSS tone mode and frequency.
        # mode = OFF, ENC, DEC
        # freq = frequency in Hz * 10 (e.g., 1318 = 131.8 Hz)
        elif (cmd_str == 'TONE'):
            mode = ''
            freq = ''
            if (len(arg_list) > 0): mode = str(arg_list[0]).upper().strip()
            if (len(arg_list) > 1): freq = str(arg_list[1]).upper().strip()
            resp = self.tone_cmd(mode, freq)
        
        # UNDOCUMENTED command to read EEPROM memory.
        elif (cmd_str == 'EEPROM-READ'):
            addr = ''
            if (len(arg_list) > 0): addr = str(arg_list[0]).upper().strip()
            (status, d1, d2) = self.eeprom_read_cmd(addr)
            resp = status + (' %02X %02X' % (d1, d2))
            
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
        if (saved_vfo == PyRigCat.ERROR): return resp
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
        if vfo_ok and (vfo != saved_vfo):
            self.set_vfo(saved_vfo)

        return resp

    # ------------------------------------------------------------------------
    def get_frequency_hz(self):
        """
        Return the rig frequency in Hz.
        """
        freq = 0
        hz = 10
        cmd = [0, 0, 0, 0, 0x03]
        send_buf = bytearray(cmd)
        sent = self._serial_write(send_buf)
        if (sent == len(send_buf)):
            rcv_data = self._serial_read(num_bytes=5)
            rcvd = len(rcv_data)
            if (rcvd == 5):
                for i in reversed(range(rcvd-1)):
                    data = rcv_data[i]
                    freq += (data & 0x0F) * hz
                    hz *= 10
                    freq += ((data & 0xF0) >> 4) * hz
                    hz *= 10
        return freq

    # ------------------------------------------------------------------------
    def set_frequency_hz(self, freq):
        """
        Set the rig frequency in Hz.
        Returns True if successful, False otherwise.
        """
        ok = False
        cmd = [0, 0, 0, 0, 0x01]
        digits = [0, 0, 0, 0, 0, 0, 0, 0]
        div = 100000000
        freq = int(freq)
        
        # Range check the frequency.
        if (freq < 100000) or (freq > 450000000): return False
        
        # Break frequency into individual BCD digits.
        for i in range(len(digits)):
            d = int(freq / div)
            freq -= d * div
            digits[i] = d
            div /= 10

        # Construct the CAT command from the BCD digits.
        for i in range(0, len(digits), 2):
            d = (digits[i] * 16) + digits[i+1]
            cmd[i // 2] = d
        
        # Send the command.
        send_buf = bytearray(cmd)
        sent = self._serial_write(send_buf)
        if (sent == len(send_buf)):
            rcv_data = self._serial_read(num_bytes=1)
            rcvd = len(rcv_data)
            if (rcvd == 1):
                if (rcv_data[0] == 0): ok = True
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
                # Get the current VFO.
                saved_vfo = self.get_vfo()
                if (saved_vfo != 'A') and (saved_vfo != 'B'): 
                    return resp # Command error
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
        cmd = [0, 0, 0, 0, 0x03]
        send_buf = bytearray(cmd)
        sent = self._serial_write(send_buf)
        if (sent == len(send_buf)):
            rcv_data = self._serial_read(num_bytes=5)
            rcvd = len(rcv_data)
            if (rcvd == 5):
                mode_val = rcv_data[4]
                if (mode_val == 0): mode = OperatingMode.LSB
                elif (mode_val == 1): mode = OperatingMode.USB
                elif (mode_val == 2): mode = OperatingMode.CW
                elif (mode_val == 3): mode = OperatingMode.CWR
                elif (mode_val == 4): mode = OperatingMode.AM
                elif (mode_val == 6): mode = OperatingMode.WFM
                elif (mode_val == 8): mode = OperatingMode.FM
                elif (mode_val == 10): mode = OperatingMode.DIGI
                elif (mode_val == 12): mode = OperatingMode.PKT
        return mode

    # ------------------------------------------------------------------------
    def set_mode(self, mode):
        """
        Set the rig mode.
        The mode is passed as an OperatingMode attribute.
        Returns True if successful, False otherwise.
        """
        cmd_ok = False
        mode_ok = False
        cmd = [0, 0, 0, 0, 0x07]
        if mode == OperatingMode.LSB:
            cmd[0] = 0
            mode_ok = True
        elif mode == OperatingMode.USB:
            cmd[0] = 1
            mode_ok = True
        elif mode == OperatingMode.CW:
            cmd[0] = 2
            mode_ok = True
        elif mode == OperatingMode.CW_R:
            cmd[0] = 3
            mode_ok = True
        elif mode == OperatingMode.AM:
            cmd[0] = 4
            mode_ok = True
        elif mode == OperatingMode.FM:
            cmd[0] = 8
            mode_ok = True
        elif mode == OperatingMode.DIGI:
            cmd[0] = 10
            mode_ok = True
        elif mode == OperatingMode.PKT:
            cmd[0] = 12
            mode_ok = True
        
        if mode_ok:
            send_buf = bytearray(cmd)
            sent = self._serial_write(send_buf)
            if (sent == len(send_buf)):
                rcv_data = self._serial_read(num_bytes=1)
                rcvd = len(rcv_data)
                if (rcvd == 1): cmd_ok = True
        return cmd_ok

    # ------------------------------------------------------------------------
    def get_split(self):
        """
        Return the split mode status.
        True = split mode on, False = split mode off
        """
        # NOTE: This uses an undocumented command, so accuracy is not guaranteed.
        resp = PyRigCat.ERROR
        (resp, d1, d2) = self.eeprom_read_cmd(0x7A)
        if (resp == PyRigCat.OK):
            if ((d1 & 0x80) > 0): 
                resp = 'ON'
            else: 
                resp = 'OFF'
        return resp

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
        cmd = [0, 0, 0, 0, 0x82]  # Default is split mode off
        if split: cmd[4] = 0x02   # Turn split on
        send_buf = bytearray(cmd)
        self._serial_write(send_buf)
        rcv_data = self._serial_read(num_bytes=1)
        rcvd = len(rcv_data)
        if (rcvd == 1):
            resp = PyRigCat.OK
        return resp

    # ------------------------------------------------------------------------
    def get_vfo(self):
        """
        Return the currently selected VFO.  Returns 'A' for VFO-A, 'B' for VFO-B.
        """
        # NOTE: This uses an undocumented command, so accuracy is not guaranteed.
        (resp, d1, d2) = self.eeprom_read_cmd(0x55)
        if (resp == PyRigCat.OK):
            if ((d1 & 0x01) > 0): resp = 'B'
            else: resp = 'A'
        return resp

    # ------------------------------------------------------------------------
    def set_vfo(self, vfo):
        """
        Set the VFO in use.  Argument is 'A' for VFO-A, 'B' for VFO-B.
        """
        ok = False
        vfo_now = self.get_vfo()
        if (vfo_now != 'A') and (vfo_now != 'B'): return False
        
        if (vfo == 'A') or (vfo == 'B'):
            if (vfo != vfo_now):
                cmd = [0, 0, 0, 0, 0x81] # Toggle VFO
                send_buf = bytearray(cmd)
                self._serial_write(send_buf)
                rcv_data = self._serial_read(num_bytes=1)
                rcvd = len(rcv_data)
                if (rcvd == 1):
                    if (rcv_data[0] == 0):
                        ok = True
            else:
                ok = True
        return ok

    # ------------------------------------------------------------------------
    def rit_cmd(self, rit_onoff):
        """
        Turn receiver incremental tuning (RIT, aka clarifier) on/off.
        """
        resp = PyRigCat.ERROR
        cmd = [0, 0, 0, 0, 0x85] # Default is OFF
        if (rit_onoff == 'ON'): cmd[4] = 0x05
        send_buf = bytearray(cmd)
        sent = self._serial_write(send_buf)
        if (sent == len(send_buf)):
            rcv_data = self._serial_read(num_bytes=1)
            rcvd = len(rcv_data)
            if (rcvd == 1):
                resp = PyRigCat.OK
        return resp
    
    # ------------------------------------------------------------------------
    def rit_freq_cmd(self, freq):
        """
        Set the RIT (clarifier) frequency.
        
        Parameters
        ----------
        freq : str
            frequency in Hz. This will get truncated down to the next lowest
            10Hz multiple. (9876 => 9870 Hz or 9.87 KHz)
            Range is +/- 9.99 KHz.
        """
        resp = PyRigCat.ERROR
        
        # Check the clarifier frequency.
        freq_ok = False
        ifreq = 0
        try:
            ifreq = int(freq)
            ifreq = int(ifreq / 10) # Truncate to 10Hz resolution
            if (ifreq >= -999) and (ifreq <= 999):
                freq_ok = True
        except Exception:
            pass
        if not freq_ok: return resp
        
        cmd = [0, 0, 0, 0, 0xF5]
        if (ifreq < 0): cmd[0] = 0x01 # Negative offset
        ifreq = abs(ifreq)
        
        # Break frequency into individual BCD digits.
        digits = [0, 0, 0, 0]
        div = 1000
        for i in range(len(digits)):
            d = int(ifreq / div)
            ifreq -= d * div
            digits[i] = d
            div /= 10

        # Construct the CAT command from the BCD digits.
        for i in range(0, len(digits), 2):
            d = (digits[i] * 16) + digits[i+1]
            cmd[2 + (i // 2)] = d
        
        # Send the command.
        send_buf = bytearray(cmd)
        sent = self._serial_write(send_buf)
        if (sent == len(send_buf)):
            rcv_data = self._serial_read(num_bytes=1)
            rcvd = len(rcv_data)
            if (rcvd == 1):
                if (rcv_data[0] == 0): resp = PyRigCat.OK
        return resp
    
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
        cmd = [0, 0, 0, 0, 0x09]
        if (shift == '-'):
            cmd[0] = 0x09     # Negative shift
        elif (shift == '+'):
            cmd[0] = 0x49     # Positive shift
        elif (shift == '0'):
            cmd[0] = 0x89     # Simplex mode
        else:
            return resp       # Invalid shift argument
        
        send_buf = bytearray(cmd)
        self._serial_write(send_buf)
        rcv_data = self._serial_read(num_bytes=1)
        rcvd = len(rcv_data)
        if (rcvd == 1):
            if (rcv_data[0] == 0): resp = PyRigCat.OK
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
        
        # Break frequency into individual BCD digits.
        digits = [0, 0, 0, 0, 0, 0, 0, 0]
        div = 10000000
        for i in range(len(digits)):
            d = int(ifreq / div)
            ifreq -= d * div
            digits[i] = d
            div /= 10

        # Construct the CAT command from the BCD digits.
        cmd = [0, 0, 0, 0, 0xF9]
        for i in range(0, len(digits), 2):
            d = (digits[i] * 16) + digits[i+1]
            cmd[i // 2] = d

        # Send the repeater offset command.
        send_buf = bytearray(cmd)
        self._serial_write(send_buf)
        rcv_data = self._serial_read(num_bytes=1)
        rcvd = len(rcv_data)
        if (rcvd == 1):
            if (rcv_data[0] == 0): resp = PyRigCat.OK
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
        
        if (mode != 'OFF'):
            if not freq.isnumeric():
                return resp # Frequency must be supplied for ENC/DEC
        
        freq_ok = True
        mode_ok = self.tone_mode_cmd(mode)
        if mode_ok:
            if (mode != 'OFF'):
                freq_ok = self.tone_freq_cmd(freq)
        if mode_ok and freq_ok:
            resp = PyRigCat.OK
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
        ok = False
        
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
        digits = [0, 0, 0, 0]
        div = 1000
        for i in range(len(digits)):
            d = int(ifreq / div)
            ifreq -= d * div
            digits[i] = d
            div /= 10

        # Construct the CAT command from the BCD digits.
        cmd = [0, 0, 0, 0, 0x0B]
        for i in range(0, len(digits), 2):
            d = (digits[i] * 16) + digits[i+1]
            cmd[i // 2] = d
        
        # Send the tone frequency command.
        send_buf = bytearray(cmd)
        self._serial_write(send_buf)
        rcv_data = self._serial_read(num_bytes=1)
        rcvd = len(rcv_data)
        if (rcvd == 1):
            if (rcv_data[0] == 0): ok = True
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
        ok = False
        cmd = [0, 0, 0, 0, 0x0A]
        if (mode == 'OFF'):
            cmd[0] = 0x8A     # Encoder/decoder off: no tone
        elif (mode == 'ENC'):
            cmd[0] = 0x4A     # Encoder on: tone on transmit
        elif (mode == 'DEC'):
            cmd[0] = 0x2A     # Decoder on: tone on transmit and receive
        else:
            return False      # Invalid argument
        
        send_buf = bytearray(cmd)
        self._serial_write(send_buf)
        rcv_data = self._serial_read(num_bytes=1)
        rcvd = len(rcv_data)
        if (rcvd == 1):
            if (rcv_data[0] == 0): ok = True
        return ok

    # ------------------------------------------------------------------------
    def get_rx_status(self):
        """
        Return the Rx status byte.
        Only appears to be valid if the FT-817 is receiving.
        """
        resp = PyRigCat.ERROR
        cmd = [0, 0, 0, 0, 0xE7]
        send_buf = bytearray(cmd)
        self._serial_write(send_buf)
        rcv_data = self._serial_read(num_bytes=1)
        rcvd = len(rcv_data)
        if (rcvd == 1):
            resp = ('%02X' % rcv_data[0])
        return resp
    
    # ------------------------------------------------------------------------
    def get_tx_status(self):
        """
        Return the Tx status byte.
        Only appears to be valid if the FT-817 is transmitting.
        """
        resp = PyRigCat.ERROR
        cmd = [0, 0, 0, 0, 0xF7]
        send_buf = bytearray(cmd)
        self._serial_write(send_buf)
        rcv_data = self._serial_read(num_bytes=1)
        rcvd = len(rcv_data)
        if (rcvd == 1):
            resp = ('%02X' % rcv_data[0])
        return resp
    
    # ------------------------------------------------------------------------
    def eeprom_read_cmd(self, addr):
        """
        UNDOCUMENTED command to read two bytes of the FT-817 internal EEPROM.
        See: http://www.ka7oei.com/ft817_meow.html
        Valid address range appears to be from 0 to 0x1925.
        
        Parameters
        ----------
        addr : int/str
            EEPROM address to read. Range is 0 to 6437 (decimal) or (0x1925 hex)
            Adddress is interpreted as decimal unless prefixed with '0x'
        
        Returns
        -------
        (resp, d1, d2) : (str, int, int)
            resp = Command response (OK or ERROR)
            d1 = Data value at EEPROM addr
            d2 = Data value at EEPROM addr + 1
        """
        resp = PyRigCat.ERROR
        d1 = 0
        d2 = 0
        addr_str = str(addr)
        
        # Check the address.
        addr_ok = False
        iaddr = 0
        try:
            base = 10
            if (addr_str.lower().startswith('0x')): base = 16
            iaddr = int(addr_str, base)
            if (iaddr >= 0) and (iaddr <= 0x1925):
                addr_ok = True
        except Exception:
            pass
        if not addr_ok: return (resp, d1, d2)
        
        msb = int(iaddr / 256)
        lsb = iaddr % 256
        cmd = [msb, lsb, 0, 0, 0xBB]
        send_buf = bytearray(cmd)
        self._serial_write(send_buf)
        rcv_data = self._serial_read(num_bytes=2)
        rcvd = len(rcv_data)
        if (rcvd == 2):
            resp = PyRigCat.OK
            d1 = int(rcv_data[0])
            d2 = int(rcv_data[1])
        return (resp, d1, d2)

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
        if (ptt_arg == ''):
            if self._ptt_is_on:
                resp = 'ON'
            else:
                resp = 'OFF'
        else:
            cmd = [0, 0, 0, 0, 0x88]             # Default is PTT off
            if (ptt_arg == 'ON'): cmd[4] = 0x08  # Turn PTT on
            send_buf = bytearray(cmd)
            self._serial_write(send_buf)
            rcv_data = self._serial_read(num_bytes=1)
            rcvd = len(rcv_data)
            if (rcvd == 1):
                self._ptt_is_on = ptt_arg
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
    print('PyRigCat_ft817 main program not implemented.')
