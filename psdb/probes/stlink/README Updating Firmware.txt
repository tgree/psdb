In order to upgrade your firmware, the easiest way is to use the STSW-LINK007
app from ST's website:

https://www.st.com/en/development-tools/stsw-link007.html#get-software

Trying to run this on macOS is painful because none of the Java files or
dynamic libraries used are signed (thanks, ST).  You can still force it to
open using the macOS "Settings > Privacy & Security" tab if you scroll down to
the bottom.  In a separate Terminal window, cd to the STSW-LINK007 folder and
just try to launch the .jar file:

java -jar STLinkUpgrade.jar

You will get an error message from Apple about the .jar being untrusted; you
can now click "Open Anyways" in the Privacy & Security panel.  You will need
to do this process a few times because there are a few other dynamic libraries
that have the same issue.  Eventually you will have whitelisted everything you
need and the upgrader will open.  You will then have the option of upgrading
the probe firmware (this works for Nucleo boards or for a standalone debug
probe) and also to change its type so that it doesn't show up as a mass
storage device all the time (and thus won't give the stupid warnings about
unplugging a drive before ejecting it).
