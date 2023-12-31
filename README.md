# motorroller - Open hardware open software stepper motor controller

<div style="margin-left:auto;margin-right:auto;text-align:center">
<img src="https://raw.githubusercontent.com/xaratustrah/motorroller/master/rsrc/motorroller.png" width="512">
</div>

Motoroller is an easy to use open hardware open software stepper motor controller using Raspberry Pi. Depending on which driver you use, you can controll have 5 phase or 2 phase stepper motors. In this current configuration, it can control up to 4 motors. Also supported are the readout of linear potentiometers.


## Installation
Please download the latest version of [Raspberry Pi OS Lite](https://www.raspberrypi.com/software/). Newest versions require setting up username / password already in the imager tool. You can also enable SSH from there. Then you can expand file system using the script `raspi-config`. Then you need a couple of things:

```
sudo apt udpate
sudo apt -y install git python3-pip
```

The clone the repository and go inside that directory and type (you may need to provide the command line arg `--break-system-packages` before the `-r` and before `.` below, depending on your system, and how you are using your Raspberry Pi. Please use with care!):

```
pip install -r requirements.txt
pip3 install .
```

For uninstalling you can type:

```
pip3 uninstall motorroller
```


## Usage

### Running modes

Motoroller can be run in three different modes. It accepts commands in interactive, command line and client / server mode. During movement, pressing ctrl-C will stop the movement and exit gracefully.

#### Interactive mode

this is the default mode. There will be an input prompt for entering commands. Just run:

```
motoroller
```

The readline history is activated for convenience. You can revisit your older commands by pressing arrow up.

#### Commands as arguments
Use one or several commands directly in the command prompt:

```
motoroller --command 0i1 0o1
```

Moves motor 0 in and out for 1 seconds.


#### Client / Server mode

This mode is not implemented yet.

### Command structure

Format is XYZ, where X is one of the following:

    0 --> Motor 0
    1 --> Motor 
    2 --> Motor 2
    3 --> Motor 3

    7 --> Both motors 0 and 1
    8 --> Both motors 2 and 3

    9 --> Read out potentiometers only, the other two positions will be ignored

    Y is the direction either I for in or O for out (case insensitive)

    Z is the duration in seconds (int or float

For example `0i1` means move motor 0 inside 1 second long, whereas `1o3.456` means move motor 1 outside 3.456 seconds long

### Other features
Following features work in combincatino with all obove mentioned operation modes:

#### Logger

A logger file name can be provided in order to put actions and readout information together with a time stamp in a log file. You activate the logger by using the `--log` swtich:

```
motorroller --log ./logfile
```

#### Motor speed

The switch `--speed` is for setting the rotation speed.

```
motorroller --speed 1000 --log ./logfile
```

#### Calibration file
Working with a calibration file insures a safer operation. In the calibration file, which is [TOML format]() limits can be set for every motor. You can provide the name of the calibration file as a command line argument:

```
motorroller --speed 1000 --log ./logfile --cal clibration.toml
```

This works for all modes of operation. Here is the structure of the calibration file:

```toml
# Value entry for every motor

[mot0]

# Absolute minimum and maximum in mm
limit_outside = 40
limit_inside = 60

# Provide two calibration points
# For calibration points, within each pair, please use either floats or ints, do not mix.
# First value is in mm, second the ADC / poti value
cal_points = [[49, 1864], [83, 1072]]
```

Please note that in the current hardware configuration, as motors move inside:

* values in mm increase
* ADC values decrease
* Motor rotation direction would correspond to CCW


## Hardware description

#### Board and Schematics

![Motoroller](https://raw.githubusercontent.com/xaratustrah/motorroller/master/rsrc/motorroller_case.png)

The schematics has been creating using [KiCAD](https://www.kicad.org/). The schematics file is included in the project. A PDF version of the schematics (connection plan) can be found [here](https://github.com/xaratustrah/motorroller/blob/main/rsrc/motorroller.kicad_sch.pdf). Needed parts are listed also in an spread sheet document [here](https://github.com/xaratustrah/motorroller/blob/main/rsrc/motorroller_part_list.ods).

#### Pin configurations

This is the connection table for the 9 pin D-SUB connector:

| Pin # | Signal                   |
|-------|--------------------------|
| 1     | End switch outside limit |
| 2     | N. C.                    |
| 3     | End switch GND           |
| 4     | End switch inside limit  |
| 5     | N. C.                    |
| 6     | Poti GND                 |
| 7     | Poti runner              |
| 8     | Poti PWR                 |
| 9     | N. C.                    |

This is the connection table for round motor connector:

| Pin | Signal    |
|-----|-----------|
| A   | Blue      |
| B   | Green     |
| C   | Red       |
| D   | Black     |
| E   | Orange    |
| F   | N. C.     |
| G   | N. C.     |
| H   | N. C.     |
| J   | N. C.     |
| K   | N. C.     |
| L   | Break PWR |
| M   | Break GND |


#### Upgrade / future revisions

Here are some suggestions for an upgrade. In case a PCB is created for the project, it is recommended that the following be considered:

* Use SPI based IO-expander **MCP23S08** in order to read the status of the end switches. This one would share the same SCLK, MOSI and MISO lines with the MCP2308 but would need its own chip select signal. This would be then connected to **pin 26** of the Raspberry Pi header.

In order to have the analog signals of the potentiometers and the digitial signals of the end swtiches, one should use the 10-pin header, and connect via flat cable to 9-pin D-SUB connector to the front plate. **Please notice, that the 10-pin connector has a different counting direction if connected to flat-cable D-SUB connectors!**

* Change relay order

For the next revision, the relay order for the BRK signals could be made more symmetric around the relay board connector:

| Pin # | Rev 0 | Rev 0 connection | Future connection |
|-------|-------|------------------|-------------------|
| 1     | 5V    | 5V               | 5V                |
| 2     | 5V    | 5V               | 5V                |
| 3     | REL1  | motor_select     | motor_select      |
| 4     | REL2  | motor_select     | motor_select      |
| 5     | REL3  | motor_select     | motor_select      |
| 6     | REL4  | motor_select     | motor_select      |
| 7     | REL5  | motor_select     | motor_select      |
| 8     | REL6  | brk0             | brk0              |
| 9     | REL7  | driver_select    | brk1              |
| 10    | REL8  | driver_select    | driver_select     |
| 11    | REL9  | brk1             | driver_select     |
| 12    | REL10 | brk2             | brk3              |
| 13    | REL11 | brk3             | brk2              |
| 14    | REL12 | motor_select     | motor_select      |
| 15    | REL13 | motor_select     | motor_select      |
| 16    | REL14 | motor_select     | motor_select      |
| 17    | REL15 | motor_select     | motor_select      |
| 18    | REL16 | motor_select     | motor_select      |
| 19    | GND   | GND              | GND               |
| 20    | GND   | GND              | GND               |

* Level shifters
  
This is a nice to have option, just add two level shofters for the CCW and CLW signals. In principle, a level shifter can also replace the darlington array IC ULN2003A , which is a bit of an overkill for the current purpose.

#### Additional hints

* Please note that the driver has direct opto coupler inputs, whereas the relay board has optocouplers that are already pulled up to 5V on one side.

* Also please note that for the crimp tool you need to set level 8 for 0.75mm<sup>2</sup> which are the motor cables, and level 5 for 0.14mm<sup>2</sup> cables, which are the end switch and potentiometer cables.

* On the motor side, the end swtiches are connected so that in the normal case they are connected to ground. If the end swtich is acticated, this connecttion is interrupted.
  


## Licensing

Please see the file [LICENSE.md](./LICENSE.md) for further information about how the content is licensed.

## Acknowledgements

Many thanks to Robert Boywitt, Roland Fischer and Sven Schuhmacher for helping with the connection plans and correct identification of the parts, and Davide Racano for providing help with the mechanical preparation of the enclosure.
