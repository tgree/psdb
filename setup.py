import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="psdb",
    version="0.9.0",
    author="Phase Advanced Sensor Sytems",
    author_email="tgreeniaus@phasesensors.com",
    description="Package for interfacing with ARM-compatible debug probes",
    long_description=long_description,
    long_description_content_type="text/plain",
    packages=['psdb',
              'psdb.block',
              'psdb.component',
              'psdb.cpus',
              'psdb.elf',
              'psdb.probes',
              'psdb.probes.stlink',
              'psdb.probes.xds110',
              'psdb.targets',
              'psdb.targets.msp432',
              'psdb.targets.stm32',
              'psdb.targets.stm32h7',
              'psdb.targets.stm32g0',
              'psdb.targets.stm32g4',
              'psdb.targets.stm32wb55',
              'psdb.targets.stm32wb55.ipc',
              'psdb.util',
              ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Operating System :: OS Independent",
    ],
    install_requires=['pyusb',
                      'pyelftools',
                      'tgcurses'],
    python_requires='>=3.0',
)
