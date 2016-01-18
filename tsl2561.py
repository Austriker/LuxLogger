import time
import smbus


class TSL2561(object):
    VISIBLE                   = 2       # channel 0 - channel 1
    INFRARED                  = 1       # channel 1
    FULLSPECTRUM              = 0       # channel 0

    # 3 i2c address options!
    ADDR_LOW                  = 0x29
    ADDR_NORMAL               = 0x39
    ADDR_HIGH                 = 0x49

    # Lux calculations differ slightly for CS package
    PACKAGE_CS                = 0
    PACKAGE_T_FN_CL           = 1

    READBIT                   = 0x01
    COMMAND_BIT               = 0x80    # Must be 1
    CLEAR_BIT                 = 0x40    # Clears any pending interrupt (write 1 to clear)
    WORD_BIT                  = 0x20    # 1 = read/write word (rather than byte)
    BLOCK_BIT                 = 0x10    # 1 = using block read/write

    CONTROL_POWERON           = 0x03
    CONTROL_POWEROFF          = 0x00

    LUX_LUXSCALE              = 14      # Scale by 2^14
    LUX_RATIOSCALE            = 9       # Scale ratio by 2^9
    LUX_CHSCALE               = 10      # Scale channel values by 2^10
    LUX_CHSCALE_TINT0         = 0x7517  # 322/11 * 2^    LUX_CHSCALE
    LUX_CHSCALE_TINT1         = 0x0FE7  # 322/81 * 2^    LUX_CHSCALE

    LUX_K1T                   = 0x0040   # 0.125 * 2^RATIO_SCALE
    LUX_B1T                   = 0x01f2   # 0.0304 * 2^    LUX_SCALE
    LUX_M1T                   = 0x01be   # 0.0272 * 2^    LUX_SCALE
    LUX_K2T                   = 0x0080   # 0.250 * 2^RATIO_SCALE
    LUX_B2T                   = 0x0214   # 0.0325 * 2^    LUX_SCALE
    LUX_M2T                   = 0x02d1   # 0.0440 * 2^    LUX_SCALE
    LUX_K3T                   = 0x00c0   # 0.375 * 2^RATIO_SCALE
    LUX_B3T                   = 0x023f   # 0.0351 * 2^    LUX_SCALE
    LUX_M3T                   = 0x037b   # 0.0544 * 2^    LUX_SCALE
    LUX_K4T                   = 0x0100   # 0.50 * 2^RATIO_SCALE
    LUX_B4T                   = 0x0270   # 0.0381 * 2^    LUX_SCALE
    LUX_M4T                   = 0x03fe   # 0.0624 * 2^    LUX_SCALE
    LUX_K5T                   = 0x0138   # 0.61 * 2^RATIO_SCALE
    LUX_B5T                   = 0x016f   # 0.0224 * 2^    LUX_SCALE
    LUX_M5T                   = 0x01fc   # 0.0310 * 2^    LUX_SCALE
    LUX_K6T                   = 0x019a   # 0.80 * 2^RATIO_SCALE
    LUX_B6T                   = 0x00d2   # 0.0128 * 2^    LUX_SCALE
    LUX_M6T                   = 0x00fb   # 0.0153 * 2^    LUX_SCALE
    LUX_K7T                   = 0x029a   # 1.3 * 2^RATIO_SCALE
    LUX_B7T                   = 0x0018   # 0.00146 * 2^    LUX_SCALE
    LUX_M7T                   = 0x0012   # 0.00112 * 2^    LUX_SCALE
    LUX_K8T                   = 0x029a   # 1.3 * 2^RATIO_SCALE
    LUX_B8T                   = 0x0000   # 0.000 * 2^    LUX_SCALE
    LUX_M8T                   = 0x0000   # 0.000 * 2^    LUX_SCALE

    # CS package values
    LUX_K1C                   = 0x0043   # 0.130 * 2^RATIO_SCALE
    LUX_B1C                   = 0x0204   # 0.0315 * 2^    LUX_SCALE
    LUX_M1C                   = 0x01ad   # 0.0262 * 2^    LUX_SCALE
    LUX_K2C                   = 0x0085   # 0.260 * 2^RATIO_SCALE
    LUX_B2C                   = 0x0228   # 0.0337 * 2^    LUX_SCALE
    LUX_M2C                   = 0x02c1   # 0.0430 * 2^    LUX_SCALE
    LUX_K3C                   = 0x00c8   # 0.390 * 2^RATIO_SCALE
    LUX_B3C                   = 0x0253   # 0.0363 * 2^    LUX_SCALE
    LUX_M3C                   = 0x0363   # 0.0529 * 2^    LUX_SCALE
    LUX_K4C                   = 0x010a   # 0.520 * 2^RATIO_SCALE
    LUX_B4C                   = 0x0282   # 0.0392 * 2^    LUX_SCALE
    LUX_M4C                   = 0x03df   # 0.0605 * 2^    LUX_SCALE
    LUX_K5C                   = 0x014d   # 0.65 * 2^RATIO_SCALE
    LUX_B5C                   = 0x0177   # 0.0229 * 2^    LUX_SCALE
    LUX_M5C                   = 0x01dd   # 0.0291 * 2^    LUX_SCALE
    LUX_K6C                   = 0x019a   # 0.80 * 2^RATIO_SCALE
    LUX_B6C                   = 0x0101   # 0.0157 * 2^    LUX_SCALE
    LUX_M6C                   = 0x0127   # 0.0180 * 2^    LUX_SCALE
    LUX_K7C                   = 0x029a   # 1.3 * 2^RATIO_SCALE
    LUX_B7C                   = 0x0037   # 0.00338 * 2^    LUX_SCALE
    LUX_M7C                   = 0x002b   # 0.00260 * 2^    LUX_SCALE
    LUX_K8C                   = 0x029a   # 1.3 * 2^RATIO_SCALE
    LUX_B8C                   = 0x0000   # 0.000 * 2^    LUX_SCALE
    LUX_M8C                   = 0x0000   # 0.000 * 2^    LUX_SCALE

    REGISTER_CONTROL          = 0x00
    REGISTER_TIMING           = 0x01
    REGISTER_THRESHHOLDL_LOW  = 0x02
    REGISTER_THRESHHOLDL_HIGH = 0x03
    REGISTER_THRESHHOLDH_LOW  = 0x04
    REGISTER_THRESHHOLDH_HIGH = 0x05
    REGISTER_INTERRUPT        = 0x06
    REGISTER_CRC              = 0x08
    REGISTER_ID               = 0x0A
    REGISTER_CHAN0_LOW        = 0x0C
    REGISTER_CHAN0_HIGH       = 0x0D
    REGISTER_CHAN1_LOW        = 0x0E
    REGISTER_CHAN1_HIGH       = 0x0F

    INTEGRATIONTIME_13MS      = 0x00    # 13.7ms
    INTEGRATIONTIME_101MS     = 0x01    # 101ms
    INTEGRATIONTIME_402MS     = 0x02    # 402ms

    GAIN_0X                   = 0x00    # No gain
    GAIN_16X                  = 0x10    # 16x gain

    address = ADDR_NORMAL
    _package = PACKAGE_T_FN_CL
    _timing = INTEGRATIONTIME_13MS
    _gain = GAIN_0X

    def __init__(self, bus=0):
        self._address = 0x39
        self._i2cbus = smbus.SMBus(1)

    def findSensor(self):

        result = self._i2cbus.read_i2c_block_data(
            self._address,
            self.REGISTER_ID,
            1
        )[0]

        if result == 0x0A:
            print("TSL2561 sensor found.")
            return True
        else:
            raise ValueError("TSL2561 sensor not found")

    def setGain(self, gain=None):

        if gain is not None:
            self._gain = gain

        self._i2cbus.write_byte_data(
            self._address,
            self.COMMAND_BIT | self.REGISTER_TIMING,
            self._gain | self._timing
        )

    def setTiming(self, timing=None):

        if timing is not None:
            self._timing = timing

        self._i2cbus.write_byte_data(
            self._address,
            self.COMMAND_BIT | self.REGISTER_TIMING,
            self._gain | self._timing
        )

    def _enable(self):

        self._i2cbus.write_byte_data(
            self._address,
            self.COMMAND_BIT | self.REGISTER_CONTROL,
            self.CONTROL_POWERON
        )

    def _wait(self):
        if self._timing == self.INTEGRATIONTIME_13MS:
            time.sleep(0.14)
        elif self._timing == self.INTEGRATIONTIME_101MS:
            time.sleep(0.102)
        elif self._timing == self.INTEGRATIONTIME_402MS:
            time.sleep(0.403)
        else:
            raise ValueError("Timing error")

    def _disable(self):

        self._i2cbus.write_byte_data(
            self._address,
            self.COMMAND_BIT | self.REGISTER_CONTROL,
            self.CONTROL_POWEROFF
        )

    def getFullLuminosity(self):

        self._enable()
        self._wait()

        result = self._i2cbus.read_i2c_block_data(
            self._address,
            self.COMMAND_BIT | self.WORD_BIT | self.REGISTER_CHAN1_LOW,
            2
        )

        full = result[1] << 8 | result[0]

        result = self._i2cbus.read_i2c_block_data(
            self._address,
            self.COMMAND_BIT | self.WORD_BIT | self.REGISTER_CHAN0_LOW,
            2
        )

        full = full << 8
        full += result[1] << 8 | result[0]

        self._disable()

        return full

    def getLuminosity(self, channel):
        x = self.getFullLuminosity()

        if channel == self.FULLSPECTRUM:
            # Reads two byte value from channel 0 (visible + infrared)
            result = x & 0xFFFF
            return result

        if channel == self.INFRARED:
            # Reads two byte value from channel 1 (infrared)
            result = x >> 16
            return result

        if channel == self.VISIBLE:
            # Reads all and subtracts out just the visible!
            result = (x & 0xFFFF) - (x >> 16)
            return result

        return 0

    def calculateLux(self, ch0, ch1):
        # default is no scaling ... integration time = 402ms
        chScale = (1 << self.LUX_CHSCALE)

        if self._timing == self.INTEGRATIONTIME_13MS:
            chScale = self.LUX_CHSCALE_TINT0
        if self._timing == self.INTEGRATIONTIME_101MS:
            chScale = self.LUX_CHSCALE_TINT1

        # Scale for gain (1x or 16x)
        chScale = chScale * self._gain

        # scale the channel values
        channel0 = (ch0 * chScale) >> self.LUX_CHSCALE
        channel1 = (ch1 * chScale) >> self.LUX_CHSCALE

        # find the ratio of the channel values (Channel1/Channel0)
        ratio = 0
        if channel0 != 0:
            ratio = (channel1 << (self.LUX_RATIOSCALE + 1)) // channel0

        # round the ratio value
        ratio = (ratio + 1) >> 1

        if self._package == self.PACKAGE_T_FN_CL:
            if (ratio >= 0) and (ratio <= self.LUX_K1T):
                b = self.LUX_B1T
                m = self.LUX_M1T
            elif ratio <= self.LUX_K2T:
                b = self.LUX_B2T
                m = self.LUX_M2T
            elif ratio <= self.LUX_K3T:
                b = self.LUX_B3T
                m = self.LUX_M3T
            elif ratio <= self.LUX_K4T:
                b = self.LUX_B4T
                m = self.LUX_M4T
            elif ratio <= self.LUX_K5T:
                b = self.LUX_B5T
                m = self.LUX_M5T
            elif ratio <= self.LUX_K6T:
                b = self.LUX_B6T
                m = self.LUX_M6T
            elif ratio <= self.LUX_K7T:
                b = self.LUX_B7T
                m = self.LUX_M7T
            elif ratio <= self.LUX_K8T:
                b = self.LUX_B8T
                m = self.LUX_M8T
        else:
            # PACKAGE_CS otherwise
            if (ratio >= 0) and (ratio <= self.LUX_K1C):
                b = self.LUX_B1C
                m = self.LUX_M1C
            elif ratio <= self.LUX_K2C:
                b = self.LUX_B2C
                m = self.LUX_M2C
            elif ratio <= self.LUX_K3C:
                b = self.LUX_B3C
                m = self.LUX_M3C
            elif ratio <= self.LUX_K4C:
                b = self.LUX_B4C
                m = self.LUX_M4C
            elif ratio <= self.LUX_K5C:
                b = self.LUX_B5C
                m = self.LUX_M5C
            elif ratio <= self.LUX_K6C:
                b = self.LUX_B6C
                m = self.LUX_M6C
            elif ratio <= self.LUX_K7C:
                b = self.LUX_B7C
                m = self.LUX_M7C
            elif ratio <= self.LUX_K8C:
                b = self.LUX_B8C
                m = self.LUX_M8C

        temp = ((channel0 * b) - (channel1 * m))
        # do not allow negative lux value
        if temp < 0:
            temp = 0
        # round lsb (2^(LUX_SCALE-1))
        temp += (1 << (self.LUX_LUXSCALE-1))

        # strip off fractional portion
        lux = temp >> self.LUX_LUXSCALE

        # Signal I2C had no errors
        return lux
