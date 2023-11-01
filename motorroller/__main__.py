"""
Motorroller - Open hardware open software stepper motor controller

2023 xaratustrah@github
"""

from time import sleep
import readline
import argparse
import os, sys
from loguru import logger
import tomllib
from .version import __version__

if os.name == "posix" and os.uname().machine == "armv7l":
    try:
        import RPi.GPIO as gpio
        import spidev
    except RuntimeError:
        print("""Error importing Raspberry Pi libraries!""")
else:
    print("Are you running the code on a Raspberry Pi?")
    exit()

# Raspberry PI pin assignment

CLW = 16
CCW = 18

BRK0 = 40
BRK2 = 35
BRK1 = 37
BRK3 = 33

MOTOR_SELECT = 36
DRIVER_SELECT = 38


class Motorroller:
    def __init__(self, motor_speed, calibration_dic):
        self.motor_speed = motor_speed
        self.brk_list = [BRK0, BRK1, BRK2, BRK3]
        self.spi_init()
        self.gpio_setup()
        self.gpio_reset()
        self.calibration_dic = calibration_dic

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

    @staticmethod
    def get_mm_from_adcval(adc_val, p1, p2):
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        return (x2 - x1) / (y2 - y1) * (adc_val - y1) + x1

    @staticmethod
    def get_adcval_from_mm(mm, p1, p2):
        x1, y1 = p1[0], p1[1]
        x2, y2 = p2[0], p2[1]
        return (y2 - y1) / (x2 - x1) * (mm - x1) + y1

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
        sleep(0.2)
        num_avg = 20
        pot0, pot1, pot2, pot3 = 0, 0, 0, 0
        # do many measurements and average
        for i in range(num_avg):
            pot0 += self.read_poti(0)
            pot1 += self.read_poti(1)
            pot2 += self.read_poti(2)
            pot3 += self.read_poti(3)
        return [
            int(pot0 / num_avg),
            int(pot1 / num_avg),
            int(pot2 / num_avg),
            int(pot3 / num_avg),
        ]

    def move_motor(self, channel, direction, duration):
        # first read the potis
        pot0, pot1, pot2, pot3 = self.read_all_potis()

        if channel == 0:
            # first set the flags
            driver_select, motor_select = 0, 0

            # then check limits according to config file
            if self.calibration_dic:
                logger.info(
                    "Checking position values with the limits provided in the calibration file before moving."
                )
                limit_inside = self.calibration_dic["mot0"]["limit_inside"]
                limit_outside = self.calibration_dic["mot0"]["limit_outside"]
                p1 = self.calibration_dic["mot0"]["cal_points"][0]
                p2 = self.calibration_dic["mot0"]["cal_points"][1]
                logger.info(
                    f"Using calibration points: {p1, p2}, direction {direction}, inside limit {limit_inside} and outside limit {limit_outside}"
                )

                if (
                    pot0 <= self.get_adcval_from_mm(limit_inside, p1, p2)
                    and direction == "ccw"
                ):
                    logger.error(
                        "Motor mot0 limit_inside position reached. Cannot move any further in that direction."
                    )
                    return
                elif (
                    pot0 >= self.get_adcval_from_mm(limit_outside, p1, p2)
                    and direction == "clw"
                ):
                    logger.error(
                        "Motor mot0 limit_outside position reached. Cannot move any further in that direction."
                    )
                    return
                else:
                    logger.info(
                        "Motor mot0 still in the given range of calibration file. Moving..."
                    )

        if channel == 1:
            # first set the flags
            driver_select, motor_select = 0, 1

            # then check limits according to config file
            if self.calibration_dic:
                logger.info(
                    "Checking position values with the limits provided in the calibration file before moving."
                )
                limit_inside = self.calibration_dic["mot1"]["limit_inside"]
                limit_outside = self.calibration_dic["mot1"]["limit_outside"]
                p1 = self.calibration_dic["mot1"]["cal_points"][0]
                p2 = self.calibration_dic["mot1"]["cal_points"][1]
                logger.info(
                    f"Using calibration points: {p1, p2}, direction {direction}, inside limit {limit_inside} and outside limit {limit_outside}"
                )

                if (
                    pot1 <= self.get_adcval_from_mm(limit_inside, p1, p2)
                    and direction == "ccw"
                ):
                    logger.error(
                        "Motor mot1 limit_inside position reached. Cannot move any further in that direction."
                    )
                    return
                elif (
                    pot1 >= self.get_adcval_from_mm(limit_outside, p1, p2)
                    and direction == "clw"
                ):
                    logger.error(
                        "Motor mot1 limit_outside position reached. Cannot move any further in that direction."
                    )
                    return
                else:
                    logger.info(
                        "Motor mot1 still in the given range of calibration file. Moving..."
                    )

        if channel == 2:
            # first set the flags
            driver_select, motor_select = 1, 0

            # then check limits according to config file
            if self.calibration_dic:
                logger.info(
                    "Checking position values with the limits provided in the calibration file before moving."
                )
                limit_inside = self.calibration_dic["mot2"]["limit_inside"]
                limit_outside = self.calibration_dic["mot2"]["limit_outside"]
                p1 = self.calibration_dic["mot2"]["cal_points"][0]
                p2 = self.calibration_dic["mot2"]["cal_points"][1]
                logger.info(
                    f"Using calibration points: {p1, p2}, direction {direction}, inside limit {limit_inside} and outside limit {limit_outside}"
                )

                if (
                    pot2 <= self.get_adcval_from_mm(limit_inside, p1, p2)
                    and direction == "ccw"
                ):
                    logger.error(
                        "Motor mot2 limit_inside position reached. Cannot move any further in that direction."
                    )
                    return
                elif (
                    pot2 >= self.get_adcval_from_mm(limit_outside, p1, p2)
                    and direction == "clw"
                ):
                    logger.error(
                        "Motor mot2 limit_outside position reached. Cannot move any further in that direction."
                    )
                    return
                else:
                    logger.info(
                        "Motor mot2 still in the given range of calibration file. Moving..."
                    )

        if channel == 3:
            # first set the flags
            driver_select, motor_select = 1, 1

            # then check limits according to config file
            if self.calibration_dic:
                logger.info(
                    "Checking position values with the limits provided in the calibration file before moving."
                )
                limit_inside = self.calibration_dic["mot3"]["limit_inside"]
                limit_outside = self.calibration_dic["mot3"]["limit_outside"]
                p1 = self.calibration_dic["mot3"]["cal_points"][0]
                p2 = self.calibration_dic["mot3"]["cal_points"][1]
                logger.info(
                    f"Using calibration points: {p1, p2}, direction {direction}, inside limit {limit_inside} and outside limit {limit_outside}"
                )

                if (
                    pot3 <= self.get_adcval_from_mm(limit_inside, p1, p2)
                    and direction == "ccw"
                ):
                    logger.error(
                        "Motor mot3 limit_inside position reached. Cannot move any further in that direction."
                    )
                    return
                elif (
                    pot3 >= self.get_adcval_from_mm(limit_outside, p1, p2)
                    and direction == "clw"
                ):
                    logger.error(
                        "Motor mot3 limit_outside position reached. Cannot move any further in that direction."
                    )
                    return
                else:
                    logger.info(
                        "Motor mot3 still in the given range of calibration file. Moving..."
                    )

        # now you can start moving the motors
        gpio.output(DRIVER_SELECT, driver_select)
        gpio.output(MOTOR_SELECT, motor_select)
        gpio.output(self.brk_list[channel], 1)

        # setup PWM: this has to be done here it seems
        # that PWM forgets the settings after each stop
        self.ccw_pwm.ChangeFrequency(self.motor_speed)
        self.clw_pwm.ChangeFrequency(self.motor_speed)

        if direction == "ccw":
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
        valid_directions = {"i", "I", "o", "O"}

        try:
            assert len(cmd) >= 3

            first_char = int(cmd[0])
            second_char = cmd[1]

            assert first_char in valid_channels
            assert second_char in valid_directions

        except (AssertionError, ValueError):
            raise ValueError(
                """Command format incorrect. Please use the following format:

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
                """
            )

        channel = int(first_char)

        # assign CCW to the direction of in
        direction = "ccw" if second_char in {"i", "I"} else "clw"

        # Try to cast duration to both integer and float
        if len(cmd) == 3:
            s = cmd[2]
        else:
            s = cmd[2:]

        try:
            duration = int(s)  # Try to cast as an integer
        except ValueError:
            try:
                duration = float(s)  # Try to cast as a float
            except ValueError:
                raise ValueError("Could not cast the string to a number.")

        return channel, direction, duration

    def log_poti_values(self):
        pot_vals = self.read_all_potis()
        poti_string = (
            f"Poti values: {self.read_all_potis()}"
            if not self.calibration_dic
            else f"""Poti values: {pot_vals}, Positions in mm: {self.get_mm_from_adcval(pot_vals[0], self.calibration_dic["mot0"]["cal_points"][0], self.calibration_dic["mot0"]["cal_points"][1]):.2f}, {self.get_mm_from_adcval(pot_vals[1], self.calibration_dic["mot1"]["cal_points"][0], self.calibration_dic["mot1"]["cal_points"][1]):.2f}, {self.get_mm_from_adcval(pot_vals[2], self.calibration_dic["mot2"]["cal_points"][0], self.calibration_dic["mot2"]["cal_points"][1]):.2f}, {self.get_mm_from_adcval(pot_vals[3], self.calibration_dic["mot3"]["cal_points"][0], self.calibration_dic["mot3"]["cal_points"][1]):.2f}"""
        )
        logger.info(poti_string)

    def process_action(self, command_str):
        channel, direction, duration = self.process_command(command_str)
        if channel in {0, 1, 2, 3}:
            logger.info(
                f"Moving motor {channel}, direction {direction} for {duration} seconds."
            )
            self.move_motor(channel, direction, duration)
            self.log_poti_values()
        elif channel == 7:
            logger.info(
                f"Moving motors 0 and 1, direction {direction} for {duration} seconds."
            )
            self.move_motor(0, direction, duration)
            self.move_motor(1, direction, duration)
            self.log_poti_values()
        elif channel == 8:
            logger.info(
                f"Moving motors 2 and 3, direction {direction} for {duration} seconds."
            )
            self.move_motor(2, direction, duration)
            self.move_motor(3, direction, duration)
            self.log_poti_values()
        elif channel == 9:
            self.log_poti_values()


# -------


def start_interactive_mode(motorroller):
    while True:
        try:
            command_str = input("Enter command or ctrl-C or ctrl-D to abort-->")
            motorroller.process_action(command_str)

        except (EOFError, KeyboardInterrupt):
            logger.success("\nUser input cancelled. Aborting...")
            break

        except ValueError as e:
            print(e)


def start_single_mode(motorroller, command_str_list):
    try:
        for command in command_str_list:
            motorroller.process_action(command)

    except (EOFError, KeyboardInterrupt):
        logger.success("\nUser input cancelled. Aborting...")

    except ValueError as e:
        print(e)



def start_server_mode():
    logger.error("Client / Server mode not implemented yet.")


# -------


def main():
    parser = argparse.ArgumentParser(prog="motorroller")
    parser.add_argument(
        "-c",
        "--command",
        nargs="+",
        type=str,
        help="Enter command as an argument.",
        default=None,
    )
    parser.add_argument(
        "--server",
        action=argparse.BooleanOptionalAction,
        help="Start in client / server mode.",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=__version__, help="Print version."
    )
    parser.add_argument(
        "-s",
        "--speed",
        nargs="?",
        type=int,
        const=200,
        default=200,
        help="Motor speed.",
    )
    parser.add_argument(
        "-l", "--log", nargs=1, type=str, help="Path and name of the log file."
    )

    parser.add_argument(
        "--cal",
        nargs=1,
        type=str,
        default=None,
        help="Path and name of the calibration file.",
    )

    logger.remove(0)
    logger.add(sys.stdout, level="INFO")
    # logger.patch(lambda record: record.update(name=record["file"].name))

    args = parser.parse_args()
    speed = args.speed
    if speed > 1200:
        logger.info(f"Given speed {speed} is not so secure. Limitting to 1200.")
        speed = 1200

    # read config file
    cal_dic = None
    if args.cal:
        logger.info("Calibration file has been provided.")
        try:
            # Load calibration file
            with open(args.cal[0], "rb") as f:
                cal_dic = tomllib.load(f)
            # check structure of calibration file
            for key in ['mot0', 'mot1', 'mot2', 'mot3']:
                assert key in cal_dic.keys()
                for keykey in ['limit_outside', 'limit_inside', 'cal_points']:
                    assert keykey in cal_dic[key].keys()
        except:
            logger.error('Calibration file does not have required format.')
            exit()
        logger.success("Calibration file is good.")
    else:
        logger.warning(
            "No calibration file provided, so limits are unknown. Proceed with caution!"
        )

    # ready to go
    motorroller = Motorroller(speed, cal_dic)

    if args.log:
        outfilename = args.log[0]
        # all levels
        logger.add(f"{outfilename}.log")

    if args.command:
        logger.info("Running individual commands.")
        start_single_mode(motorroller, args.command)

    elif args.server:
        logger.info("Starting client / server mode.")
        start_server_mode(motorroller)

    else:
        logger.info("Starting interactive mode.")
        start_interactive_mode(motorroller)

    # gracefully close down
    motorroller.closedown()
    exit()


# -----
if __name__ == "__main__":
    main()
