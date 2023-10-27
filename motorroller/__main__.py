'''
Motorroller - Open hardware open software stepper motor controller

2023 xaratustra@github
'''

from time import sleep
import readline
import argparse
import os, sys
from loguru import logger
from .version import __version__

if os.name == 'posix' and os.uname().machine == 'armv7l':
    try:
        import RPi.GPIO as gpio
        import spidev
    except RuntimeError:
        print('''Error importing Raspberry Pi libraries!''')
else:
    print('Are you running the code on a Raspberry Pi?')
    exit()

# pin assignment

CLW = 16
CCW = 18

BRK0 = 40
BRK2 = 35
BRK1 = 37
BRK3 = 33

MOTOR_SELECT = 36
DRIVER_SELECT = 38


class Motorroller:
    def __init__(self, motor_speed):
        self.motor_speed = motor_speed
        self.brk_list = [BRK0, BRK1, BRK2, BRK3]
        self.spi_init()
        self.gpio_setup()
        self.gpio_reset()

    def gpio_setup(self):
        # gpio Setup
        gpio.setwarnings(False)
        gpio.setmode(gpio.BOARD)  # Header pin number system

        gpio.setup(CLW, gpio.OUT)
        gpio.setup(CCW, gpio.OUT)
        gpio.setup(BRK0, gpio.OUT)
        gpio.setup(BRK1, gpio.OUT)
        gpio.setup(BRK2, gpio.OUT)
        gpio.setup(BRK3, gpio.OUT)
        gpio.setup(MOTOR_SELECT, gpio.OUT)
        gpio.setup(DRIVER_SELECT, gpio.OUT)

        # setup PWM
        self.clw_pwm = gpio.PWM(CLW, self.motor_speed)
        self.ccw_pwm = gpio.PWM(CCW, self.motor_speed)
        self.clw_pwm.ChangeDutyCycle(50)
        self.ccw_pwm.ChangeDutyCycle(50)

    def spi_init(self):
        # init SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 5000
        return self.spi

    def gpio_reset(self):
        # Initial values
        gpio.output(CLW, gpio.LOW)
        gpio.output(CCW, gpio.LOW)

        gpio.output(MOTOR_SELECT, gpio.LOW)
        gpio.output(DRIVER_SELECT, gpio.LOW)

        for channel in {0, 1, 2, 3}:
            gpio.output(self.brk_list[channel], gpio.LOW)

    def read_poti(self, channel):
        msg = (
            0x00
            if channel == 0
            else 0x40
            if channel == 1
            else 0x80
            if channel == 2
            else 0xC0
        )

        resp = self.spi.xfer([0x06, msg, 0x00])
        value = (resp[1] << 8) + resp[2]
        value = int(value)

        # clip value
        if value <= 0:
            value = 0
        elif value > 4095:
            value = 4095

        return value

    def read_all_potis(self):
        return [
            self.read_poti(0),
            self.read_poti(1),
            self.read_poti(2),
            self.read_poti(3),
        ]

    def move_motor(self, channel, direction, duration):
        driver_select, motor_select = (
            (0, 0)
            if channel == 0
            else (0, 1)
            if channel == 1
            else (1, 0)
            if channel == 2
            else (1, 1)
            if channel == 3
            else (None, None)
        )
        gpio.output(DRIVER_SELECT, driver_select)
        gpio.output(MOTOR_SELECT, motor_select)
        gpio.output(self.brk_list[channel], 1)

        # setup PWM: this has to be done here it seems
        # that PWM forgets the settings after each stop
        self.ccw_pwm.ChangeFrequency(self.motor_speed)
        self.clw_pwm.ChangeFrequency(self.motor_speed)

        if direction == 'ccw':
            self.ccw_pwm.start(50)
            sleep(duration)
            self.ccw_pwm.stop()
        else:
            self.clw_pwm.start(50)
            sleep(duration)
            self.clw_pwm.stop()

        # break off
        gpio.output(self.brk_list[channel], 0)

    def closedown(self):
        self.spi.close()
        self.gpio_reset()

    def process_command(self, cmd):
        valid_channels = {0, 1, 2, 3, 7, 8, 9}
        valid_directions = {'i', 'I', 'o', 'O'}

        try:
            assert len(cmd) >= 3
            
            first_char = int(cmd[0])
            second_char = cmd[1]

            assert first_char in valid_channels
            assert second_char in valid_directions
            
        except (AssertionError, ValueError):
            raise ValueError(
                '''Command format incorrect. Please use the following format:

                    Format is XYZ, where X is one of the following:

                    0 --> Motor 0
                    1 --> Motor 
                    2 --> Motor 2
                    3 --> Motor 3

                    7 --> Both motors 0 and 1
                    8 --> Both motors 2 and 3

                    9 --> Read out potentiometers only, the other two positions will be ignored

                    Y is the direction either I for in or O for out (case insensitive)

                    Z is the duration in seconds (int or float)\n
                '''
            )

        channel = int(first_char)

        # assign CCW to the direction of in
        direction = 'ccw' if second_char in {'i', 'I'} else 'clw'

        # Try to cast duration to both integer and float
        if len(cmd) == 3:
            s = cmd[2]
        else:
            s = cmd[2:-1]

        try:
            duration = int(s)  # Try to cast as an integer
        except ValueError:
            try:
                duration = float(s)  # Try to cast as a float
            except ValueError:
                raise ValueError('Could not cast the string to a number.')

        return channel, direction, duration


    def process_action(self, command_str):
        channel, direction, duration = self.process_command(command_str)
        if channel in {0, 1, 2, 3}:
            logger.info(
                f'Moving motor {channel}, direction {direction} for {duration} seconds.'
            )
            self.move_motor(channel, direction, duration)
            logger.info(f'Poti values: {self.read_all_potis()}')
        elif channel == 7:
            logger.info(
                f'Moving motors 0 and 1, direction {direction} for {duration} seconds.'
            )
            self.move_motor(0, direction, duration)
            self.move_motor(1, direction, duration)
            logger.info(f'Poti values: {self.read_all_potis()}')
        elif channel == 8:
            logger.info(
                f'Moving motors 2 and 3, direction {direction} for {duration} seconds.'
            )
            self.move_motor(2, direction, duration)
            self.move_motor(3, direction, duration)
            logger.info(f'Poti values: {self.read_all_potis()}')
        elif channel == 9:
            logger.info(f'Poti values: {self.read_all_potis()}')
                        

# -------


def start_interactive_mode(motorroller):
    while True:
        try:
            command_str = input('Enter command or ctrl-C to abort-->')
            motorroller.process_action(command_str)

        except (EOFError, KeyboardInterrupt):
            logger.info('\nUser input cancelled. Aborting...')
            break

        except ValueError as e:
            print(e)


def start_single_mode(motorroller, command_str_list):
    for command in command_str_list:
        motorroller.process_action(command)


def start_server_mode():
    logger.info('Client / Server mode not implemented yet.')


# -------


def main():
    parser = argparse.ArgumentParser(prog='motorroller')
    parser.add_argument(
        '-c',
        '--command',
        nargs='+',
        type=str,
        help='Enter command as an argument.',
        default=None,
    )
    parser.add_argument(
        '--server',
        action=argparse.BooleanOptionalAction,
        help='Start in client / server mode.',
    )
    parser.add_argument(
        '-v', '--version', action='version', version=__version__, help='Print version.'
    )
    parser.add_argument(
        '-s',
        '--speed',
        nargs='?',
        type=int,
        const=200,
        default=200,
        help='Motor speed.',
    )
    parser.add_argument('-l', '--log', nargs=1, type=str,
                        help='Path and name of the log file.')
    

    args = parser.parse_args()
    motorroller = Motorroller(args.speed)
    
    logger.remove(0)
    logger.add(sys.stdout, level='INFO')
    #logger.patch(lambda record: record.update(name=record["file"].name))
    
    if args.log:
        outfilename = args.log[0]
        # all levels
        logger.add(f'{outfilename}.log')

    if args.command:
        logger.info('Running individual commands.')
        start_single_mode(motorroller, args.command)

    elif args.server:
        logger.info('Starting client / server mode.')
        start_server_mode(motorroller)

    else:
        logger.info('Starting interactive mode.')
        start_interactive_mode(motorroller)

    motorroller.closedown()
    exit()


# -----
if __name__ == '__main__':
    main()
