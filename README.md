# motorroller - Open hardware open software stepper motor controller

![RDTS](https://raw.githubusercontent.com/xaratustrah/motorroller/master/rsrc/motorroller.png)

Motoroller is an easy to use open hardware open software stepper motor controller using Raspberry Pi. Depending on which driver you use, you can controll have 5 phase or 2 phase motors. In this current configuration, it can control up to 4 motors. Also supported are the readout of linear potentiometers.

#### Board and Schematics

![RDTS](https://raw.githubusercontent.com/xaratustrah/motorroller/master/rsrc/box.png)

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



## Licensing

Please see the file [LICENSE.md](./LICENSE.md) for further information about how the content is licensed.

## Acknowledgements

Many thanks to Robert Boywitt, Roland Fischer and Sven Schuhmacher for helping with the connection plans and correct identification of the parts, and Davide Racano for providing help with the mechanical preparation of the enclosure.
