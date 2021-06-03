DEIMOS QuickLook Script Usage
=============================

Documents how to use this script to launch the DEIMOS quicklook script
from PypeIt, along with additional command line arguments that can be
used to customize the process.

Default Usage
-------------

The program can be launched with 

``start_deimos_ql -m -w -d [DIRECTORY]``

where ``[DIRECTORY]`` is the filepath (absolute or relative) to the
directory that should be monitored. This will almost always be an RTI
``lev0`` directory. The directory should be empty to begin with. This
program does *not* mutate files in the input directory.

Extra Options
-------------

**Extra Calibration Frames**
    If more than the minimum number of calibrations appear in the directory,
    the script will re-process all of the calibrations with the new file added.
    This should be avoided where possible by adjusting the minimum number of
    frames of each calibration type to match the number the observer plans on
    capture. If you don't care about using all calibrations that appear, 
    enabling ``--no-clobber`` will tell the script to ignore extra calibrations.

