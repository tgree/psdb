This package provides Python access to various ARM-compatible debug probes.

All tools support the --help option.  It is recommended to use python3.  You
may install the package locally using:

make install3

which will require super-user privileges.  Alternatively, you can run all
commands from the root of the repository.

If you are on a Linux machine, it is also recommended to install the udev
rules file that will allow non-sudo access to the debug probes (otherwise you
must run the psdb tools using sudo) to anybody that is a member of the 'usb'
group:

sudo addgroup usb
sudo adduser YOUR_USER_NAME usb
sudo cp -r etc/* /etc/

This command is not necessary on macOS since USB devices are accessible
without super-user privileges.  If your debug probe is connected when you
install the udev rules, you may need to hot-plug it in order for the new rules
to take effect.  Also, if you just added yourself to the usb group then you
will need to start a new shell session for that permission to take effect.

===============================================================================
python3 -m psdb.flash_tool <params>

The flash_tool script allows you to burn ELF images into flash, retrieve the
contents of flash and reset a target board.


===============================================================================
python3 -m psdb.gdb_tool

The gdb_tool script starts a simple gdb server that attaches to the target
device.  It can be connected to with a remote gdb client.


===============================================================================
python3 -m psdb.inspect_tool

The inspect_tool script starts an interactive curses-based tool that can be
used to view the current CPU registers, select target peripheral registers and
select regions of target RAM or flash.  The inspect_tool script requires the
tgcurses library to be installed (available on github/tgree).  Since tgcurses
only supports python3, inspect_tool can only run under python3.


===============================================================================
python3 -m psdb.fus_tool

The fus_tool script is for interacting with the ST Firmare Upgrade Services
(FUS) on the STM32WB55 wireless MCU.  The STM32WB55 co-processor has a secure
region of flash that includes the FUS binary itself and the wireless stack
currently installed on the MCU.  Different wireless stacks can be installed
and FUS itself can also be upgraded.  The binaries can be found in the
STM32CubeWB.git repository:

https://github.com/STMicroelectronics/STM32CubeWB

under the path:

Projects/STM32WB_Copro_Wireless_Binaries/STM32WB5x

Sample invocations:

python3 -m psdb.fus_tool --fw-upgrade Projects/STM32WB_Copro_Wireless_Binaries/STM32WB5x/stm32wb5x_BLE_Stack_full_fw.bin
python3 -m psdb.fus_tool --fw-delete
python3 -m psdb.fus_tool --bin-dir Projects/STM32WB_Copro_Wireless_Binaries/STM32WB5x --fus-upgrade

Or, a compound command to remove the old WS firmware, install new WS firmware
and then start the application back up:

python3 -m psdb.fus_tool \
    --fw-delete \
    --fw-upgrade Projects/STM32WB_Copro_Wireless_Binaries/STM32WB5x/stm32wb5x_BLE_Stack_full_fw.bin \
    --set-flash-boot

Note that an invocation with --set-flash-boot is required when you are done;
in order to properly communicate with FUS, we need to prevent any user
firmware from starting CPU2 or trying to use the IPC channels - we do that by
switching the system to boot from SRAM1 until we are done with it.


===============================================================================
We also attempt to document the STLINK protocol inside the stlink package.
You can view it most easily from within the python interpreter:

    >>> import psdb.probes.stlink
    >>> help(psdb.probes.stlink.cdb)
