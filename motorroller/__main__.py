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

CLW = 16
CCW = 18
BRK0 = 40
BRK2 = 35
BRK1 = 37
BRK3 = 33

brk_list = [BRK0, BRK1, BRK2, BRK3]

MOTOR_SELECT = 36
DRIVER_SELECT = 38

# gpio Setup

gpio.setwarnings(False)
gpio.setmode(gpio.BOARD) # Header pin number system

gpio.setup(CLW, gpio.OUT)
gpio.setup(CCW, gpio.OUT)
gpio.setup(BRK0, gpio.OUT)
gpio.setup(BRK1, gpio.OUT)
gpio.setup(BRK2, gpio.OUT)
gpio.setup(BRK3, gpio.OUT)
gpio.setup(MOTOR_SELECT, gpio.OUT)
gpio.setup(DRIVER_SELECT, gpio.OUT)

# setup PWM
clw_pwm = gpio.PWM(CLW, MOTOR_SPEED)
ccw_pwm = gpio.PWM(CCW, MOTOR_SPEED)
clw_pwm.ChangeDutyCycle(50)
ccw_pwm.ChangeDutyCycle(50)

# init SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 5000

def reinit_gpio():
    # Initial values
    gpio.output(CLW, 0)
    gpio.output(CCW, 0)

    gpio.output(BRK0, 0)
    gpio.output(BRK1, 0)
    gpio.output(BRK2, 0)
    gpio.output(BRK3, 0)

    gpio.output(MOTOR_SELECT, 0)
    gpio.output(DRIVER_SELECT, 0)

def read_poti(channel):
    if channel not in {0, 1, 2, 3}:
        raise ValueError('Channel should be 0-3')
    msg = 0x00 if channel == 0 else 0x40 if channel == 1 else 0x80 if channel == 2 else 0xC0
    
    resp = spi.xfer([0x06, msg, 0x00])
    value = (resp[1] << 8) + resp[2]
    value = int(int(value) * 2 / 3)
    if value <= 0:
        value = 1
    return value

def move_motor(channel, direction, duration):

    motor_select, driver_select = (0, 0) if channel == 0 else (0, 1) if channel == 1 else (1, 0) if channel == 2 else (1, 1) if channel == 3 else (None, None)
    
    gpio.output(DRIVER_SELECT, driver_select)
    gpio.output(MOTOR_SELECT, motor_select)
    gpio.output(channel, 1)

    # zero for clockwise
    if not direction:
        ccw_pwm.start(50)
        sleep(duration)
        ccw_pwm.stop()
    else:
        clw_pwm.start(50)
        sleep(duration)
        clw_pwm.stop()
    
    # break off
    gpio.output(channel, 0)
    
    
def process_command(cmd):
    try:
        first_char = int(cmd[0])
    except ValueError:
        raise ValueError('Command format incorrect. Format is XDY, where X is channel numnber 0, 1, 2 and 3, D is either I for in or O for out and Y is the duration in seconds (int or float)\n')
        
    second_char = cmd[1]

    valid_channels = {0, 1, 2, 3}
    valid_directions = {'i', 'I', 'o', 'O'}

    if first_char not in valid_channels or second_char not in valid_directions:
        raise ValueError('Command format incorrect. Format is XDY, where X is channel numnber 0, 1, 2 and 3, D is either I for in or O for out and Y is the duration in seconds (int or float)\n')

    channel = int(first_char)
    
    direction = 'CLW' if second_char in {'i', 'I'} else 'CCW'

    # Try to cast duration to both integer and float
    if len(cmd) == 3:
        s = cmd[2]
    else:
        s = cmd[2:-1]

    try:
        duration =  int(s)  # Try to cast as an integer
    except ValueError:
        try:
            duration = float(s)  # Try to cast as a float
        except ValueError:
            raise ValueError("Could not cast the string to a number.")

    return channel, direction, duration


#-------

def main():
    print('Motor controller')
    reinit_gpio()
    while True:
        try:
            cmmd = input ('Enter command or ctrl-C to abort-->')
            print(process_command(cmmd))
        except(EOFError, KeyboardInterrupt):
            spi.close()
            reinit_gpio()    
            print('\nUser input cancelled. Aborting...')            
            exit()
        except(ValueError) as e:
            print(e)

# -----
if __name__ == '__main__':
    main()
