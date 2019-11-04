import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pypsdb",
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
              'psdb.targets',
              'psdb.targets.msp432',
              'psdb.targets.stm32h7',
              'psdb.targets.stm32g4',
              ],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
        "Operating System :: OS Independent",
    ],
    install_requires=['pyusb',
                      'pyelftools'],
    python_requires='>=2.7',
)
