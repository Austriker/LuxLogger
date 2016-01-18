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

        while True:
            print(sensor.getLuminosityDict())
            time.sleep(1)


if __name__ == "__main__":
    main()
