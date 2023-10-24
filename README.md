# motorroller - Open hardware open software stepper motor controller

![Motoroller](https://raw.githubusercontent.com/xaratustrah/motorroller/master/rsrc/motorroller.png)

Motoroller is an easy to use open hardware open software stepper motor controller using Raspberry Pi. Depending on which driver you use, you can controll have 5 phase or 2 phase motors. In this current configuration, it can control up to 4 motors. Also supported are the readout of linear potentiometers.

#### Board and Schematics

![Motoroller](https://raw.githubusercontent.com/xaratustrah/motorroller/master/rsrc/box.jpg)

The schematics has been creating using [KiCAD](https://www.kicad.org/). The schematics file is included in the project. A PDF version of the schematics (connection plan) can be found here. Needed parts are listed also in an spread sheet document .


#### Installation
After cloning the code of the repository, go inside that directory and type:

```
pip install -r requirements.txt
pip3 install .
```

or uninstall

```
pip3 uninstall motorroller
```


#### Running `motorroller`




### Hardware description

Please note that the driver has direct opto coupler inputs, whereas the relay board has optocouplers that are already pulled up to 5V on one side.

#### Upgrade / future revisions

Here are some suggestions for an upgrade. In case a PCB is created for the project, it is recommended that the following be considered:

* Use SPI based IO-expander **MCP23S08** in order to read the status of the end switches. This one would share the same SCLK, MOSI and MISO lines with the MCP2308 but would need its own chip select signal. This would be then connected to **pin 26** of the Raspberry Pi header.

In order to have the analog signals of the potentiometers and the digitial signals of the end swtiches, one should use the 10-pin header, and connect via flat cable to 9-pin D-SUB connector to the front plate. **Please notice, that the 10-pin connector has a different counting direction whenever it is connected to flat-cable D-SUB connectors!**

* Change relay order

For the next revision, the relay order for the BRK signals could be made more symmetric:

| Relay board connector Pin # | Rev 0 | Rev 0 connection | Future connection |
|-----------------------------|-------|------------------|-------------------|
| 1                           | 5V    | 5V               | 5V                |
| 2                           | 5V    | 5V               | 5V                |
| 3                           | REL1  | motor_select     | motor_select      |
| 4                           | REL2  | motor_select     | motor_select      |
| 5                           | REL3  | motor_select     | motor_select      |
| 6                           | REL4  | motor_select     | motor_select      |
| 7                           | REL5  | motor_select     | motor_select      |
| 8                           | REL6  | brk0             | brk0              |
| 9                           | REL7  | driver_select    | brk1              |
| 10                          | REL8  | driver_select    | driver_select     |
| 11                          | REL9  | brk1             | driver_select     |
| 12                          | REL10 | brk2             | brk3              |
| 13                          | REL11 | brk3             | brk2              |
| 14                          | REL12 | motor_select     | motor_select      |
| 15                          | REL13 | motor_select     | motor_select      |
| 16                          | REL14 | motor_select     | motor_select      |
| 17                          | REL15 | motor_select     | motor_select      |
| 18                          | REL16 | motor_select     | motor_select      |
| 19                          | GND   | GND              | GND               |
| 20                          | GND   | GND              | GND               |


* Level shifters
  
This is a nice to have option, just add two level shofters for the CCW and CLW signals. In principle, a level shifter can also replace the darlington array IC ULN2003A , which is a bit of an overkill for the current purpose.


## Licensing

Please see the file [LICENSE.md](./LICENSE.md) for further information about how the content is licensed.

## Acknowledgements

Many thanks to Robert Boywitt, Roland Fischer and Sven Schuhmacher for helping with the connection plans and correct identification of the parts, and Davide Racano for providing help with the mechanical preparation of the enclosure.
