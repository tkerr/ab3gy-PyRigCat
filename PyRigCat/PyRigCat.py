###############################################################################
# PyRigCat.py
# Author: Tom Kerr AB3GY
#
# A python Computer Aided Tranceiver (CAT) module for amateur radio use.
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
import math
import serial
import traceback


##############################################################################
# Enumeration classes.
##############################################################################

class Datasize(object):
    FIVE = serial.FIVEBITS
    SIX = serial.SIXBITS
    SEVEN = serial.SEVENBITS
    EIGHT = serial.EIGHTBITS

# ----------------------------------------------------------------------------
class Parity(object):
    NONE = serial.PARITY_NONE
    EVEN = serial.PARITY_EVEN
    ODD = serial.PARITY_ODD
    MARK = serial.PARITY_MARK
    SPACE = serial.PARITY_SPACE

# ----------------------------------------------------------------------------
class Stopbits(object):
    ONE = serial.STOPBITS_ONE
    ONE_POINT_FIVE = serial.STOPBITS_ONE_POINT_FIVE
    TWO = serial.STOPBITS_TWO

# ----------------------------------------------------------------------------
class Flow(object):
    # Values match serial class.
    NONE = 0
    XONXOFF = 1
    RTSCTS = 2
    DSRDTR = 3

# ----------------------------------------------------------------------------
class PttMethod(object):
    NONE = 'NONE'
    CAT = 'CAT'
    DTR = 'DTR'
    RTS = 'RTS'

# ----------------------------------------------------------------------------
class OperatingMode(object):
    UNKNOWN = 'UNKNOWN'
    LSB = 'LSB'
    USB = 'USB'
    CW = 'CW'
    CW_R = 'CW-R'
    AM = 'AM'
    AM_N = 'AM-N'
    FM = 'FM'
    FM_N = 'FM-N'
    FM_W = 'FM-W'
    C4FM = 'C4FM'
    RTTY = 'RTTY'
    RTTY_R = 'RTTY-R'
    DIGI = 'DIGI'
    PKT = 'PKT'
    DATA = 'DATA'
    DATA_USB = 'DATA-USB'
    DATA_LSB = 'DATA-LSB'
    DATA_FM = 'DATA-FM'
    MODE_LIST = [
        LSB,
        USB,
        CW,
        CW_R,
        AM,
        AM_N,
        FM,
        FM_N,
        FM_W,
        C4FM,
        RTTY,
        RTTY_R,
        DIGI,
        PKT,
        DATA,
        DATA_USB,
        DATA_LSB,
        DATA_FM]
    
    # ------------------------------------------------------------------------
    def is_valid(mode):
        """
        Return True if the specified mode is a valid OperatingMode attribute,
        or False otherwise.
        """
        return (mode.upper() in OperatingMode.MODE_LIST)

# ----------------------------------------------------------------------------
class RigName(object):
    NONE   = 'NONE'
    FT817  = 'FT-817'
    FT991  = 'FT-991'
    IC7000 = 'IC-7000'
    RIG_LIST = [
        NONE,
        FT817,
        FT991,
        IC7000]
        
    # ------------------------------------------------------------------------
    def is_valid(name):
        """
        Return True if the specified rig is a valid RigName attribute,
        or False otherwise.
        """
        return (name.upper() in RigName.RIG_LIST)


##############################################################################
# Functions.
##############################################################################
    
    
##############################################################################
# PyRigCat class.
##############################################################################
class PyRigCat(object):
    """
    Base class used to send and receive transceiver commands over a serial port.
    CAT support for specific transceivers is provided by subclassing this class.
    """
    ERROR = 'ERROR'        # Standard command error response
    OK = 'OK'              # Standard command success response
    NOTFOUND = 'NOT FOUND' # Standard 'command not found' response
    
    # ------------------------------------------------------------------------
    def __init__(self):
        """
        Class constructor.
        """
        self.NAME = 'NONE'  # Rig name or other descriptive name for this CAT object
        self._port = serial.Serial(port=None)
        self._echo = False  # Set to True if rig echoes command
        self._ptt_method = PttMethod.NONE
        
        # Many transceivers don't have a way to determine if PTT is on (or if the 
        # rig is transmitting) during real-time operations.  This flag provides
        # a way for class methods to determine if PTT is on or off by remote control.
        # Every subclass should set/clear this flag as appropriate in their 
        # ptt_cat() method and any other method that affects PTT.
        self._ptt_is_on = False
        
        # Some newer transceivers have separate data modes and voice modes.
        # For example: DATA-LSB vs. LSB, DATA-USB vs. USB, DATA-FM vs. FM.
        # Older transceivers do not distinguish between data modes and voice modes.
        # This flag indicates whether or not the transceiver has separate data modes.
        self._has_data_modes = False
        
    # ------------------------------------------------------------------------
    def __del__(self):
        """
        Class destructor.
        """
        self.close()

    # ----------------------------------------------------------------------------    
    def _print_msg(self, msg):
        """
        Print a formatted message.  Used internally for error printing and
        debugging.

        Parameters
        ----------
        msg : str
            The message text to print.
        
        Returns
        -------
        None
        """
        cl = type(self).__name__                         # This class name
        fn = str(traceback.extract_stack(None, 2)[0][2]) # Calling function name
        print(cl + '.' + fn + ': ' + msg)

    # ----------------------------------------------------------------------------    
    def _serial_write(self, send_buf):
        """
        Send a series of bytes to the serial port.
        
        Parameters
        ----------
        send_buf : bytes-like
            A bytes-like object containing the bytes to send.
        
        Returns
        -------
        sent : int
            The number of bytes sent over the serial port.
        """
        sent = 0
        try:
            sent = self._port.write(send_buf)
        except Exception as err:
            self._print_msg(str(err))
        return sent
    
    # ----------------------------------------------------------------------------    
    def _serial_read(self, num_bytes=100000):
        """
        Receive a series of bytes from the serial port.
        
        Parameters
        ----------
        num_bytes : int
            The maximum number of bytes to receive.  
            Method will wait until the number of bytes are received or a timeout occurs.
        
        Returns
        -------
        read_buf : bytes
            The received bytes as a bytes object.
        """
        read_buf = bytearray()
        try:
            read_buf = self._port.read(size=num_bytes)
        except Exception as err:
            self._print_msg(str(err))
        return read_buf
    
    # ----------------------------------------------------------------------------    
    def _set_dtr(self, dtr=True):
        """
        Set/clear the DTR signal line.
        
        Parameters
        ----------
        dtr : bool
            True sets the DTR line, False clears it.
        
        Returns
        -------
        ok : bool
            True if command successful, False otherwise.
        """
        ok = False
        try:
            self._port.dtr = dtr
            ok = True
        except Exception as err:
            self._print_msg(str(err))
        return ok
    
    # ----------------------------------------------------------------------------    
    def _set_rts(self, rts=True):
        """
        Set/clear the RTS signal line.
        
        Parameters
        ----------
        rts : bool
            True sets the RTS line, False clears it.
        
        Returns
        -------
        ok : bool
            True if command successful, False otherwise.
        """
        ok = False
        try:
            self._port.rts = rts
            ok = True
        except Exception as err:
            self._print_msg(str(err))
        return ok
    
    # ------------------------------------------------------------------------
    def config_port(self, 
        port=None, 
        baudrate=9600, 
        datasize=Datasize.EIGHT, 
        parity=Parity.NONE, 
        stopbits=Stopbits.ONE, 
        flow=Flow.NONE,
        echo=None,
        read_timeout=1.1,
        write_timeout=1.0):
        
        """
        Configure and open the serial port.
        
        Parameters
        ----------
        port : str
            The serial port name to configure and open.
        baudrate : int
            The serial port baud rate.
        datasize : Datasize attribute
            The serial data size in bits as a Datasize() attribute.
        parity : Parity attribute
            The serial port parity as a Parity() attribute.
        stopbits : Stopbits attribute
            The serial stop bit size in bits as a Stopbits() attribute.
        flow : Flow attribute
            The flow control method as a Flow() attribute.
        echo : bool
            True if the serial port echoes the command, False otherwise.
            Ignored if None.
        read_timeout : float
            The read timeout value in seconds.
        write_timeout : float
            The write timeout value in seconds.
        
        Returns
        -------
        ok : bool
            True if configuration is successful, False otherwise.
        """
        ok = False
        if port is not None:
            try:
                if echo is not None: self._echo = echo
                self._port.port = port
                self._port.baudrate = baudrate
                self._port.bytesize = datasize
                self._port.parity = parity
                self._port.stopbits = stopbits
                self._port.timeout = read_timeout
                self._port.write_timeout = write_timeout
                
                # Set flow control.
                self._port.xonxoff = False
                self._port.rtscts = False
                self._port.dsrdtr = False
                if (flow == Flow.XONXOFF): self._port.xonxoff = True
                elif (flow == Flow.RTSCTS): self._port.rtscts = True
                elif (flow == Flow.DSRDTR): self._port.dsrdtr = True
                
                # Open the port.
                self._port.open()
                ok = True
                
            except ValueError as err:
                self._print_msg(str(err))
                
            except serial.SerialException as err:
                self._print_msg(str(err))
        return ok
    
    # ------------------------------------------------------------------------
    def close(self):
        """
        Close the serial port.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        None.
        """
        if self._port is not None:
            try:
                self._port.close()
            except Exception:
                pass

    # ------------------------------------------------------------------------
    def get_ptt_method(self):
        """
        Return the Push-To-Talk (PTT) method.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        _ptt_method : PttMethod attribute
            The Push-To-Talk (PTT) method as a PttMethod() attribute (CAT, RTS, DTR, NONE).
        """
        return self._ptt_method
    
    # ------------------------------------------------------------------------
    def set_ptt_method(self, method):
        """
        Set the Push-To-Talk (PTT) method.
        
        Parameters
        ----------
        method : PttMethod attribute
            The Push-To-Talk (PTT) method as a PttMethod() attribute (CAT, RTS, DTR, NONE).
        
        Returns
        -------
        ok : bool
            True if command successful, False otherwise.
        """
        ok = False
        if (method == PttMethod.CAT): 
            self._ptt_method = method
            ok = True
        elif (method == PttMethod.DTR): 
            self._ptt_method = method
            ok = True
        elif (method == PttMethod.RTS): 
            self._ptt_method = method
            ok = True
        elif (method == PttMethod.NONE): 
            self._ptt_method = method
            ok = True
        return ok

    # ------------------------------------------------------------------------
    def ptt_cmd(self, ptt_arg=''):
        """
        Get/set the Push-To-Talk (PTT) state.
        
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
        # NOTE: Subclasses SHOULD NOT override this method.  
        # They should override the ptt_cat() method to provide transceiver-specific CAT control.
        
        resp = PyRigCat.ERROR
        if (self._ptt_method == PttMethod.CAT):
            # Call the transceiver-specific CAT command.
            resp = self.ptt_cat(ptt_arg)

        elif (self._ptt_method == PttMethod.DTR):
            if (ptt_arg == ''): 
                if self._ptt_is_on: resp = 'ON'
                else: resp = 'OFF'
            elif (ptt_arg == 'ON'):
                ok = self._set_dtr(True)
                if ok:
                    self._ptt_is_on = True
                    resp = PyRigCat.OK
            elif (ptt_arg == 'OFF'):
                ok = self._set_dtr(False)
                if ok:
                    self._ptt_is_on = False
                    resp = PyRigCat.OK

        elif (self._ptt_method == PttMethod.RTS):
            if (ptt_arg == ''): 
                if self._ptt_is_on: resp = 'ON'
                else: resp = 'OFF'
            elif (ptt_arg == 'ON'):
                ok = self.self._set_rts(True)
                if ok:
                    self._ptt_is_on = True
                    resp = PyRigCat.OK
            elif (ptt_arg == 'OFF'):
                ok = self.self._set_rts(False)
                if ok:
                    self._ptt_is_on = False
                    resp = PyRigCat.OK
        return resp

    # ------------------------------------------------------------------------
    def int_to_bcd(self, val, max_val):
        """
        Convenience method to convert an integer to a list of BCD digits.
        
        Parameters
        ----------
        val : int
            The integer value to convert.
        max_val : int
            The maximum value that val can obtain. 
            Used to size the list of BCD digits.
        
        Returns
        -------
        bcd : list of ints
            A list of BCD integers in the range 0-9.
            Order is [MSB ... LSB]
        """
        val = int(abs(val)) # Convert to non-negative integer
        p = int(math.log10(abs(max_val)))
        digits = [0] * (p + 1) # List of zeros
        div = pow(10, p)
        for i in range(p + 1):
            d = int(val / div)
            val -= d * div
            digits[i] = d
            div /= 10
        return digits


    ##########################################################################
    # Rig control commands.
    # These need to be implemented by subclasses for each specific transceiver.
    ##########################################################################

    # ------------------------------------------------------------------------
    def ascii_cmd(self, cmd_str, arg_list=[]):
        """
        Parse an ASCII command into one or more CAT commands and send them
        to the transceiver.  Recive response(s) and convert to an ASCII 
        response to the user.
        
        Subclasses should first call their parent class method.  If it returns 
        PyRigCat.NOTFOUND, then they should try to parse a transceiver-specific 
        command.
        
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
        resp = PyRigCat.NOTFOUND
        cmd_str = cmd_str.upper()

        # NOTE: Subclasses must override the ptt_cat() method to implement  
        # their transceiver-specific PTT CAT control.
        if (cmd_str == 'PTT'):
            ptt_arg = ''
            if (len(arg_list) > 0):
                ptt_arg = arg_list[0].upper().strip()
            resp = self.ptt_cmd(ptt_arg)
        
        # Subclasses should NOT override this command.
        elif (cmd_str == 'PTT-METHOD'):
            if (len(arg_list) > 0):
                resp = self.set_ptt_method(arg_list[0])
            else:
                resp = self.get_ptt_method()
        
        elif (cmd_str == 'ASCII'):
            cmd_str = ''
            for arg in arg_list:
                cmd_str += '{} '.format(arg)
            resp = self.raw_ascii_str(cmd_str.strip())
        
        elif (cmd_str == 'HEX'):
            resp = self.raw_hex_list(arg_list)

        return resp

    # ------------------------------------------------------------------------
    def init_rig(self):
        """
        Attempt to place the transceiver in a known state.
        Assumes config_port() has been called successfully first.
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        None.
        """
        pass

    # ------------------------------------------------------------------------
    def ptt_cat(self, ptt_arg=''):
        """
        Perform transceiver-specific PTT CAT control.
        Should turn the PTT ON/OFF, or return the PTT state.
        Subclasses should also set the self._ptt_is_on flag appropriately.
        
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
            Subclasses may return additional responses.
        """
        resp = PyRigCat.ERROR # PTT control not implemented
        if (ptt_arg == ''):
            if self._ptt_is_on: resp = 'ON'
            else: resp = 'OFF'
        elif (ptt_arg == 'OFF'):
            # Subclasses execute CAT commands to turn PTT off
            self._ptt_is_on = False
            # resp = PyRigCat.OK
            pass
        elif (ptt_arg == 'ON'):
            # Subclasses execute CAT commands to turn PTT on
            self._ptt_is_on = True
            # resp = PyRigCat.OK
            pass
        return resp

    # ------------------------------------------------------------------------
    def raw_ascii_str(self, ascii_str, max_read=1000):
        """
        Send an ASCII string to the transceiver and return a response.
        Ths string is sent as-is with no parsing.
        
        Parameters
        ----------
        ascii_str : str
            The string to send to the transeiver.
        max_read : int
            The maximum number of bytes to read after sending the string.
            If zero (default), then no read operation is performed.
        
        Returns
        -------
        resp : str
            The transceiver response as an ASCII string.
        """
        resp = ''
        #print('ascii = "{}"'.format(ascii_str))
        send_buf = ascii_str.encode('ascii')
        sent = self._serial_write(send_buf)
        if (sent == len(send_buf)):
            if (max_read > 0):
                read_buf = self._serial_read(max_read)
                try:
                    resp = read_buf.decode('ascii')
                except Exception as err:
                    self._print_msg(str(err))
        else:
            self._print_msg('Serial write error: sent {}, expected {}'.format(sent, len(send_buf)))
        return resp
    
    # ------------------------------------------------------------------------
    def raw_hex_list(self, hex_str_list, max_read=1000):
        """
        Send a list of hex bytes to the transceiver and return a response.
        Ths string values are converted to binary and sent to the transcriver.
        e.g., 'AB' = 0xAB = 171
        
        Parameters
        ----------
        hex_str_list : [str, ...]
            A list of hex digits provided as strings, e.g., ['01', 'AB']
        max_read : int
            The maximum number of bytes to read after sending the string.
            If zero (default), then no read operation is performed.
        
        Returns
        -------
        resp : str
            The transceiver response as a list of bytes converted to ASCII strings.
        """
        resp = ''
        #print('hex = "{}"'.format(hex_str_list))
        
        # Build the array of hex bytes.
        hex_list = []
        for hex_str in hex_str_list:
            hex_list.append(int(hex_str, base=16))
        send_buf = bytearray(hex_list)
        send_len = len(send_buf)
        
        # Send the command.
        sent = self._serial_write(send_buf)
        if (sent == send_len):
            if (max_read > 0):
                resp = ''
                resp_buf = self._serial_read(max_read) # Get response
                resp_list = list(resp_buf)
                
                # Format the response as a list of hex byte strings.
                for r in resp_list:
                    resp += '{:02X} '.format(r)
        else:
            self._print_msg('Serial write error: sent {}, expected {}'.format(sent, len(send_buf)))
        return resp.strip()


    # ------------------------------------------------------------------------
    def setup_split(self, vfoa_hz, modea, split=False, vfob_hz=0, modeb_hz=OperatingMode.UNKNOWN):
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
            Subclasses may return additional responses.
        """
        resp = PyRigCat.ERROR # Base class method not implemented
        return resp


##############################################################################
# Main program.
############################################################################## 
if __name__ == "__main__":
    print('PyRigCat main program.')
    print(PyRigCat.OK)
    print(Datasize.EIGHT, Parity.NONE, Stopbits.ONE)
    print(Flow.XONXOFF)
    print(PttMethod.RTS)
    print(OperatingMode.RTTY)
    print(OperatingMode.MODE_LIST)
    
    my_cat = PyRigCat()
    cmd = 'FREQ'
    arg_list = ['7074000']
    resp = my_cat.ascii_cmd(cmd, arg_list)
    print('cmd = ' + cmd + ' arg = ' + arg_list[0] + ' resp = ' + resp)
    print('PTT method = ' + my_cat.ascii_cmd('PTT-METHOD'))

    
