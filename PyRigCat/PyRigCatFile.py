###############################################################################
# PyRigCatFile.py
# Author: Tom Kerr AB3GY
#
# PyRigCatFile class.
# Used to parse and iterate through a file of Computer Aided Transceiver (CAT)
# commands.
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
import codecs
import sys
import traceback


##############################################################################
# PyRigCatFile class.
##############################################################################
class PyRigCatFile(object):
    """
    PyRigCatFile class.
    
    Parse and iterate through a file of Computer Aided Transceiver (CAT) 
    commands.
    
    Class must be instantiated with the name of the CAT command file to parse.
    """
    
    # ------------------------------------------------------------------------
    def __init__(self, filename):
        """
        Class constructor.
        
        Parameters
        ----------
        filename : str
            The name of the CAT command file to parse.
        
        Returns
        -------
        None
        """
        self.filename = filename
        self.fileobj = None

        
    # ------------------------------------------------------------------------
    def __del__(self):
        """
        Class destructor.
        """
        self.close()
    
    # ------------------------------------------------------------------------
    def __iter__(self):
        """
        Initializes the iterator.
        """
        (status, errmsg) = self.open()
        if not status: self._print_msg(errmsg)
        return self
    
    # ------------------------------------------------------------------------
    def __next__(self):
        """
        Returns the next command in the file.
        Raises the StopIteration exception when complete.
        """
        command = ''
        status = False
        errmsg = ''
        (command, status, errmsg) = self.next_command()
        if status:
            return command
        else:
            self.close()
            raise StopIteration
    
    # ----------------------------------------------------------------------------    
    def _print_msg(self, msg):
        """
        Print a formatted message.  Used internally for error and verbose printing.

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

    # ------------------------------------------------------------------------
    def open(self):
        """
        Opens the CAT command file for reading.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        (status, errmsg) : tuple
            status : bool
                True if the file opened successfully, False otherwise.
                  errmsg : str
                The file open error message if an error occurred.
        """
        status = False
        errmsg = ''
        if self.fileobj is not None:
            self.close()
        try:
            self.fileobj = codecs.open(self.filename, mode='r', encoding='utf-8', errors='ignore')
            status = True
        except Exception as err:
            self.fileobj = None
            errmsg = str(err)
            #self._print_msg(errmsg)
        return (status, errmsg)

    # ------------------------------------------------------------------------
    def all_commands(self):
        """
        The iterator function to use in a for() loop.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        command : str
            The next command string in the file.
        
        Example usage:
            myCat = PyRigCatFile(filename)
            for command in myAdifIter.all_commands():
                print(command)
                do_stuff()
        """
        return iter(self)

    # ------------------------------------------------------------------------
    def next_command(self):
        """
        Method to get the next CAT command from the file.
        Removes comments and whitespace from the command string.
    
        Parameters
        ----------
        None
        
        Returns
        -------
        (command, success, errmsg) : tuple
            command : str
                The CAT command as a string.
            success : bool
                True if the command was retrieved successfully, False otherwise.
                Returns False on end of file.                
            errmsg : str
                The error message if an error occurred.
                Returns 'EOF' on end of file.
        """
        command = ''
        success = True
        errmsg = ''
        blank = True
        if self.fileobj is not None:
            while blank and success:
                try:
                    command = self.fileobj.readline()
                    if (len(command) > 0):
                
                        # Strip comments.
                        idx = command.find('#')
                        if (idx >= 0): command = command[:idx]
                    
                        # Strip whitespace.
                        command = command.strip()
                        
                        # Check if blank.
                        if (len(command) > 0):
                            blank = False
                        success = True
                    else:
                       errmsg = 'EOF'
                       success = False
                except Exception as err:
                     errmsg = str(err)
                     success = False
        else:
            errmsg = 'EOF'
            success = False
        return (command, success, errmsg)
        
    # ------------------------------------------------------------------------
    def close(self):
        """
        Closes the ADIF file.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        """
        if self.fileobj is not None:
            try:
                fileobj.close()
            except Exception as err:
                pass
            self.fileobj = None


##############################################################################
# Main program.
############################################################################## 
if __name__ == "__main__":

    print('PyRigCatFile application example.')
    
    # Get filename from command line.
    if (len(sys.argv) < 2):
        print('No CAT command file specified.')
        sys.exit(1)
        
    filename = sys.argv[1]
    myCatFile = PyRigCatFile(filename)
    
    print('Pass 1 - Manual iteration.')
    
    # Manually open the CAT command file.
    (status, errmsg) = myCatFile.open()
    if not status:
        print('Error opening ' + filename + ': ' + errmsg)
    
    # Get each command individually.
    status = True
    errmsg = ''
    command = ''
    while status:
        (command, status, errmsg) = myCatFile.next_command()
        if status: print('"' + command + '"')
        else: print('(' + errmsg + ')')
    
    # Close the CAT command file.
    myCatFile.close()
        
    print('Pass 2 - Using an iterator.')
    for command in myCatFile.all_commands():
        print('"' + command + '"')
    
    sys.exit(0)
