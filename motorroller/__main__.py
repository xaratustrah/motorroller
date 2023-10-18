"""
Motorroller - Open hardware open software stepper motor controller

2023 xaratustra@github
"""

from time import sleep
import os

if os.name == 'posix' and os.uname().machine == 'armv7l':
    try:
        import RPi.GPIO as gpio
        import spidev
    except RuntimeError:
        print("""Error importing Raspberry Pi libraries!""")


# constants

MOTOR_SPEED = 500

# pin assignment

clw = 16
ccw = 18
brk0 = 40
brk2 = 35
brk1 = 37
brk3 = 33
motor_select = 36
driver_select = 38

# gpio Setup

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD) # Header pin number system

gpio.setup(clw, gpio.OUT)
gpio.setup(ccw, gpio.OUT)
gpio.setup(brk0, gpio.OUT)
gpio.setup(brk1, gpio.OUT)
gpio.setup(brk2, gpio.OUT)
gpio.setup(brk3, gpio.OUT)
gpio.setup(motor_select, gpio.OUT)
gpio.setup(driver_select, gpio.OUT)

# setup PWM
clw_pwm = gpio.PWM(clw, MOTOR_SPEED)
ccw_pwm = gpio.PWM(ccw, MOTOR_SPEED)
clw_pwm.ChangeDutyCycle(50)
ccw_pwm.ChangeDutyCycle(50)

# init SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 5000

def reinit_gpio():
    # Initial values
    gpio.output(clw, 0)
    gpio.output(ccw, 0)

    gpio.output(brk0, 0)
    gpio.output(brk1, 0)
    gpio.output(brk2, 0)
    gpio.output(brk3, 0)

    gpio.output(motor_select, 0)
    gpio.output(driver_select, 0)

def read_pot0():
    resp = spi.xfer([0x06, 0x00, 0x00])
    value = (resp[1] << 8) + resp[2]
    value = int(int(value) * 2 / 3)
    if value <= 0:
        value = 1
    return value

def read_pot1():
    resp = spi.xfer([0x06, 0x40, 0x00])
    value = (resp[1] << 8) + resp[2]
    value = int(int(value) * 2 / 3)
    if value <= 0:
        value = 1
    return value

def read_pot2():
    resp = spi.xfer([0x06, 0x80, 0x00])
    value = (resp[1] << 8) + resp[2]
    value = int(int(value) * 2 / 3)
    if value <= 0:
        value = 1
    return value

def read_pot3():
    resp = spi.xfer([0x06, 0xC0, 0x00])
    value = (resp[1] << 8) + resp[2]
    value = int(int(value) * 2 / 3)
    if value <= 0:
        value = 1
    return value

def move_mot0(duration, direction):
    # zero for clockwise
    gpio.output(driver_select, 0)
    gpio.output(motor_select, 0)
    gpio.output(brk0, 1)
    if not direction:
        ccw_pwm.start(50)
        sleep(duration)
        ccw_pwm.stop()
    else:
        clw_pwm.start(50)
        sleep(duration)
        clw_pwm.stop()
        
    gpio.output(brk0, 0)
    print('pot0 value: ', read_pot0())
    
def move_mot1(duration, direction):
    # zero for clockwise
    gpio.output(driver_select, 0)
    gpio.output(motor_select, 1)
    gpio.output(brk1, 1)
    if not direction:
        ccw_pwm.start(50)
        sleep(duration)
        ccw_pwm.stop()
    else:
        clw_pwm.start(50)
        sleep(duration)
        clw_pwm.stop()
        
    gpio.output(brk1, 0)
    print('pot1 value: ', read_pot1())

def move_mot2(duration, direction):
    # zero for clockwise
    gpio.output(driver_select, 1)
    gpio.output(motor_select, 0)
    gpio.output(brk2, 1)
    if not direction:
        ccw_pwm.start(50)
        sleep(duration)
        ccw_pwm.stop()
    else:
        clw_pwm.start(50)
        sleep(duration)
        clw_pwm.stop()
        
    gpio.output(brk2, 0)
    print('pot2 value: ', read_pot2())

def move_mot3(duration, direction):
    # zero for clockwise
    gpio.output(driver_select, 1)
    gpio.output(motor_select, 1)
    gpio.output(brk3, 1)
    if not direction:
        ccw_pwm.start(50)
        sleep(duration)
        ccw_pwm.stop()
    else:
        clw_pwm.start(50)
        sleep(duration)
        clw_pwm.stop()
        
    gpio.output(brk3, 0)
    print('pot3 value: ', read_pot3())

def main():
    
    reinit_gpio()
    
    move_mot0(2, 0)
    move_mot0(2, 1)

    move_mot1(2, 0)
    move_mot1(2, 1)

    move_mot2(2, 0)
    move_mot2(2, 1)

    move_mot3(2, 0)
    move_mot3(2, 1)

    reinit_gpio()
    spi.close()

# -----
if __name__ == '__main__':
    main()
