This package provides Python access to various ARM-compatible debug probes.

All tools support the --help option.  It is recommended to use python3.


python3 -m psdb.flash_tool <params>

The flash_tool script allows you to burn ELF images into flash, retrieve the
contents of flash and reset a target board.


python3 -m psdb.gdb_tool

The gdb_tool script starts a simple gdb server that attaches to the target
device.  It can be connected to with a remote gdb client.


python3 -m psdb.inspect_tool

The inspect_tool script starts an interactive curses-based tool that can be
used to view the current CPU registers, select target peripheral registers and
select regions of target RAM or flash.  The inspect_tool script requires the
tgcurses library to be installed (available on github/tgree).  Since tgcurses
only supports python3, inspect_tool can only run under python3.
