#!/usr/bin/env python3

import time
import logging
import os
import datetime
from tsl2561 import TSL2561

logger = logging.getLogger(__name__)
output_dir = os.path.dirname(os.path.realpath(__file__))
filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + "_gps.log"

logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

handler = logging.FileHandler(os.path.join(output_dir, filename), "w", encoding=None)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def main():
    sensor = TSL2561()
    if sensor.findSensor():
        sensor.setGain(sensor.GAIN_16X)
        sensor.setTiming(sensor.INTEGRATIONTIME_13MS)

        x = sensor.getFullLuminosity()
        print("Full luminosity value: %d" % x)
        print("Full luminosity value: %#08x" % x)

        full = sensor.getLuminosity(sensor.FULLSPECTRUM)
        visible = sensor.getLuminosity(sensor.VISIBLE)
        infrared = sensor.getLuminosity(sensor.INFRARED)

        print("IR: %x" % infrared)
        print("Full: %x" % full)
        print("Visible: %#x" % visible)
        print("Visible, calculated: %#x" % (full - infrared))
        print("Lux: %d" % tsl.calculateLux(full, infrared))


if __name__ == "__main__":
    main()
