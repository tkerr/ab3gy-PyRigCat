# AB3GY PyRigCat
A Python package for Computer Aided Transcriver (CAT) control for amateur radio use.

Developed for personal use by the author, but available to anyone under the license terms below.

The package consists of a `PyRigCat` base class that is subclassed for specific transceivers.

The basic idea is to provide a common set of ASCII commands that are parsed into transceiver-specific commands, for example:
  * FREQUENCY 14074000
  * POWER 100
  * PTT ON

Additional design details are provided in design.txt.

A list of ASCII commands is provided in ascii-cmds.txt.

### **_This is very much still a work in process._** ###

## Dependencies
Written for Python 3.x.

Requires serial port access, which may be OS-specific. Imports the `serial` package which is based on PySerial.

See https://pyserial.readthedocs.io/en/latest/pyserial.html 

This package has been tested on Windows 10 PCs. Other operating systems have not been tested.
 
## Author
Tom Kerr AB3GY
ab3gy@arrl.net

## License
Released under the 3-clause BSD license.
See license.txt for details.
