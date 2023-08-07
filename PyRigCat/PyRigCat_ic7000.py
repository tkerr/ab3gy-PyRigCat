###############################################################################
# PyRigCat_ic7000.py
# Author: Tom Kerr AB3GY
#
# A python Computer Aided Tranceiver (CAT) module for amateur radio use.
# Implements CAT control for the Icom IC-7000 transceiver.
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
    PttMethod, OperatingMode, RigName
from PyRigCat.PyRigCat_icom import PyRigCat_icom, IcomAddr

##############################################################################
# PyRigCat_ic7000 class.
##############################################################################
class PyRigCat_ic7000(PyRigCat_icom):
    """
    CAT control class for the Icom IC-7000 transceiver.
    This is a subclass of the PyRigCat_icom base class.
    """
    
    # ------------------------------------------------------------------------
    def __init__(self):
        """
        Class constructor.
        """
        super().__init__()           # Call the base class constructor
        self.NAME = RigName.IC7000   # Set transceiver name
        self._echo = True            # Commands are echoed
        self._has_data_modes = False # No separate data modes
        self.addr = IcomAddr.IC7000  # IC-7000 hex address

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

        return resp


##############################################################################
# Functions.
############################################################################## 


##############################################################################
# Main program.
############################################################################## 
if __name__ == "__main__":
    print('PyRigCat_ic7000 main program not implemented.')
