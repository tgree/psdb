psdb
====
This package provides Python access to various ARM-compatible debug probes.

All tools support the ``--help`` option.  It is required to use python3.  The
easiest way to install psdb is using pip::

    pip3 install psdb

Note that you may wish to use sudo to install psdb for all users on your
system::

    sudo pip3 install psdb

You may also install the package from the source using::

    make install

which will require super-user privileges.  Alternatively, you can run all
commands from the root of the repository without installing anything.

If you are on a Linux machine, it is also recommended to install the udev
rules file that will allow non-sudo access to the debug probes (otherwise you
must run the psdb tools using sudo) to anybody that is a member of the 'usb'
group::

    sudo addgroup usb
    sudo adduser YOUR_USER_NAME usb
    sudo cp -r etc/* /etc/

This command is not necessary on macOS since USB devices are accessible
without super-user privileges.  If your debug probe is connected when you
install the udev rules, you may need to hot-plug it in order for the new rules
to take effect.  Also, if you just added yourself to the usb group then you
will need to start a new shell session for that permission to take effect.


psdb_flash_tool
===============
The flash_tool script allows you to burn ELF images into flash, retrieve the
contents of flash and reset a target board.  On STM32, it is highly
recommended to use the ``--connect-under-reset`` option.  This will reset the
target MCU and halt in the reset handler before any code has a chance to
execute and potentially interfere with the flashing operation.  This is
especially important on the STM32WB series where the flash is shared by the
wireless coprocessor.  Non-STM32 MCUs may not support connecting to the target
while it is under reset (for instance, the MSP432 does not support this).

To dump the full flash contents to a file, generating a raw binary image
(useful for making a backup of the original flash contents on a board)::

    psdb_flash_tool --connect-under-reset --read path/to/file.bin

To write a raw binary image into flash::

    psdb_flash_tool --connect-under-reset --write--raw-binary path/to/file.bin

Flashing of ELF and Intel HEX files is also supported.  In these cases, all
address ranges that overlap with the flash will be burnt in, and other address
ranges will be ignored.  Note that the target sectors (and only the target
sectors) are fully erased first, so any sectors that are under-specified in
the ELF or HEX files will contain 0xFF in the unused regions.  To flash an ELF
or HEX file::

    psdb_flash_tool --connect-under-reset --flash path/to/image.elf
    psdb_flash_tool --connect-under-reset --flash path/to/image.hex

Finally, erasing the flash is also supported.  All writeable sectors will be
erased to the value 0xFF::

    psdb_flash_tool --connect-under-reset --erase

The flash_tool script can also be used to view and modify the STM32 option
bytes stored in the MCU's flash.  The ``--get-options`` flag allows one to dump
the contents of all option bytes::

    psdb_flash_tool --connect-under-reset --get-options

While the ``--option`` argument (which takes two parameters - a
case-insensitive option name and an option value) can be specified multiple
times to change options::

    psdb_flash_tool --connect-under-reset --option nboot1 0 --option nboot0 1


psdb_core_tool
==============
The core_tool script can be used to capture the contents of flash and SRAM in
the form of an ELF core file.  This core file, in conjunction with the
original ELF executable, can be opened under gdb for offline diagnosis.
Unfortunately, the standard ``arm-none-eabi-gdb`` tool cannot open core files;
however, ``gdb-multiarch`` is able to open these without any trouble.  On Linux,
this is as simple as installing ``gdb-multiarch`` with your package manager.
On other systems, installing in a Docker container may be a viable alternative.

The ``--peripheral-capture`` option allows the capture of all registers from
devices listed in the target's dev array.

The captured core file is independent of the build system used to generate the
executable or the actual code installed on the microcontroller.  To debug the
core file::

    gdb-multiarch path/to/executable.elf
    target core path/to/core.elf


psdb_gdb_tool
=============
The gdb_tool script starts a simple gdb server that attaches to the target
device.  It can be connected to with a remote gdb client.


psdb_inspect_tool
=================
The inspect_tool script starts an interactive curses-based tool that can be
used to view the current CPU registers, select target peripheral registers and
select regions of target RAM or flash.  The inspect_tool script requires the
tgcurses library to be installed (available on github/tgree).  pip will
install tgcurses automatically.


psdb_fus_tool
=============
The fus_tool script is for interacting with the ST Firmare Upgrade Services
(FUS) on the STM32WB55 wireless MCU.  The STM32WB55 co-processor has a secure
region of flash that includes the FUS binary itself and the wireless stack
currently installed on the MCU.  Different wireless stacks can be installed
and FUS itself can also be upgraded.  The binaries can be found in ST's
`STM32CubeWB.git`_ repository under the path::

    Projects/STM32WB_Copro_Wireless_Binaries/STM32WB5x

Sample invocations for manipulating wireless firmware::

    psdb_fus_tool --fw-upgrade Projects/STM32WB_Copro_Wireless_Binaries/STM32WB5x/stm32wb5x_BLE_Stack_full_fw.bin
    psdb_fus_tool --fw-delete

Or, a compound command to remove the old WS firmware, install new WS firmware
and then start the application back up::

    psdb_fus_tool \
        --fw-delete \
        --fw-upgrade Projects/STM32WB_Copro_Wireless_Binaries/STM32WB5x/stm32wb5x_BLE_Stack_full_fw.bin \
        --set-flash-boot

Note that an invocation with ``--set-flash-boot`` is required when you are done;
in order to properly communicate with FUS, we need to prevent any user
firmware from starting CPU2 or trying to use the IPC channels - we do that by
switching the system to boot from SRAM1 until we are done with it.

When using this to upgrade FUS itself, you use the ``--fus-upgrade`` option
along with the ``--bin-dir`` option.  The code will find the next valid FUS
binary in the upgrade path for your target.  For instance, a brand new Nucleo
STM32WB55 board has an ancient 0.5.3 version of FUS.  This cannot be directly
upgraded to the latest 1.1.0 version of FUS but must instead stop at 1.0.2
first.  You can then reinvoke fus_tool again if you wish to then upgrade from
1.0.2 to 1.1.0.  Note that it is not possible to downgrade FUS, so this
behavior allows you to stop at any desired version.  When upgrading FUS, it is
required to first delete the current wireless stack with the ``--fw-delete``
option.

Sample invocation for updating FUS::

    psdb_fus_tool --bin-dir Projects/STM32WB_Copro_Wireless_Binaries/STM32WB5x --fus-upgrade

Note that when upgrading FUS, the target board will reboot at least 4 times.

It is recommended to upgrade to FUS 1.1.0.


STLINK Protocol
===============
We also attempt to document the STLINK protocol inside the stlink package.
You can view it most easily from within the python interpreter::

    >>> import psdb.probes.stlink
    >>> help(psdb.probes.stlink.cdb)


.. _STM32CubeWB.git: https://github.com/STMicroelectronics/STM32CubeWB
