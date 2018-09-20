"""
AS726X (AS7262 and AS7263) MicroPython driver, low memory version, specific for BBC Micro:bit :
https://github.com/rcolistete/MicroPython_AS726x
Version: 0.7.0 (16/06/2018)
"""

from micropython import const
from microbit import sleep
from ustruct import unpack


# Values for HW_Version virtual register
SENSORTYPE_AS7262 = const(0x3E)
SENSORTYPE_AS7263 = const(0x3F)
# Values for Control Setup virtual register
## Gain
AS726X_GAIN_1X = const(0) # Default
AS726X_GAIN_3d7X = const(1)
AS726X_GAIN_16X = const(2)
AS726X_GAIN_64X = const(3)
## Measurement Mode (Bank Mode) settings for spectral conversion
AS726X_CONTINUOUS_READING_BANK1_CHANNELS = const(0b00)
AS726X_CONTINUOUS_READING_BANK2_CHANNELS = const(0b01)
AS726X_CONTINUOUS_READING_ALL_CHANNELS = const(0b10) # Default
AS726X_ONE_SHOT_READING_ALL_CHANNELS = const(0b11)
# Values for LED Control virtual register
AS726X_INDICATOR_LED_CURRENT_1mA = const(0b00) # Default
AS726X_INDICATOR_LED_CURRENT_2mA = const(0b01)
AS726X_INDICATOR_LED_CURRENT_4mA = const(0b10)
AS726X_INDICATOR_LED_CURRENT_8mA = const(0b11)
AS726X_BULB_LED_CURRENT_12d5mA = const(0b00) # Default
AS726X_BULB_LED_CURRENT_25mA = const(0b01)
AS726X_BULB_LED_CURRENT_50mA = const(0b10)
AS726X_BULB_LED_CURRENT_100mA = const(0b11)


class AS726X:
    
    def __init__(self, i2c, address=0x49):
        self.i2c = i2c
        self.address = address

    def getSensorType(self):
        return self.virtualReadRegister(0x01)

    # Temperature in C (Celsius scale)
    def getTemperature(self):
        return self.virtualReadRegister(0x06)

    def enableIndicatorLED(self, value=True):
        self.virtualWriteRegister(0x07, (self.virtualReadRegister(0x07) & 0b11111110) | (value & 0x01))

    def setIndicatorLEDCurrent(self, current):
        self.virtualWriteRegister(0x07, (self.virtualReadRegister(0x07) & 0b11111001) | ((current & 0x03) << 1))

    def enableBulbLED(self, value=True):
        self.virtualWriteRegister(0x07, (self.virtualReadRegister(0x07) & 0b11110111) | ((value & 0x01) << 3))

    def setBulbLEDCurrent(self, current):
        self.virtualWriteRegister(0x07, (self.virtualReadRegister(0x07) & 0b11001111) | ((current & 0x03) << 4))

    def setGain(self, gain):
        if (gain > 3):
            gain = 0
        self.virtualWriteRegister(0x04, (self.virtualReadRegister(0x04) & 0b11001111) | (gain << 4))

    def setMeasurementMode(self, mode):
        if (mode > 3):
            mode = 3
        self.virtualWriteRegister(0x04, (self.virtualReadRegister(0x04) & 0b11110011) | (mode << 2))

    def setIntegrationTime(self, integrationValue):
        self.virtualWriteRegister(0x05, integrationValue)

    def dataAvailable(self):
        return (self.virtualReadRegister(0x04) & 0b00000010) == 0b00000010

    def clearDataAvailable(self):
        self.virtualWriteRegister(0x04, self.virtualReadRegister(0x04) & 0b11111101)

    def takeOneShotASynchMeasurement(self):
        self.clearDataAvailable()
        self.setMeasurementMode(3)

    def takeOneShotSynchMeasurement(self):
        self.clearDataAvailable()
        pausems = self.virtualReadRegister(0x05)*6
        self.setMeasurementMode(3)
        sleep(pausems)

    def _getCalibratedValue(self, calAddress):
        b0 = self.virtualReadRegister(calAddress + 0)
        b1 = self.virtualReadRegister(calAddress + 1)
        b2 = self.virtualReadRegister(calAddress + 2)
        b3 = self.virtualReadRegister(calAddress + 3)
        return unpack(">f", bytearray([b0, b1, b2, b3]))[0]

    def getCalibratedChannel1(self):
        return self._getCalibratedValue(0x14)

    def getCalibratedChannel2(self):
        return self._getCalibratedValue(0x18)

    def getCalibratedChannel3(self):
        return self._getCalibratedValue(0x1C)

    def getCalibratedChannel4(self):
        return self._getCalibratedValue(0x20)

    def getCalibratedChannel5(self):
        return self._getCalibratedValue(0x24)

    def getCalibratedChannel6(self):
        return self._getCalibratedValue(0x28)

    def getCalibrated6Channels(self):
        return self._getCalibratedValue(0x14), self._getCalibratedValue(0x18), self._getCalibratedValue(0x1C), \
               self._getCalibratedValue(0x20), self._getCalibratedValue(0x24), self._getCalibratedValue(0x28)

    def _set_reg(self, register, data):
        self.i2c.write(self.address, bytearray([register, data]))    

    def _get_8bits_reg(self, register):
        self.i2c.write(self.address, bytearray([register]))
        v =	self.i2c.read(self.address, 1)
        return v[0]
	
    def virtualReadRegister(self, virtualAddr): 
        status = self._get_8bits_reg(0x00)
        if (status & 0x01) != 0:
            readdata = self._get_8bits_reg(0x00)
        while (self._get_8bits_reg(0x00) & 0x02) != 0:
            sleep(5)
        self._set_reg(0x01, virtualAddr)
        while (self._get_8bits_reg(0x00) & 0x01) == 0:
            sleep(5)
        readdata = self._get_8bits_reg(0x02)
        return readdata

    def virtualWriteRegister(self, virtualAddr, dataToWrite): 
        while (self._get_8bits_reg(0x00) & 0x02) != 0:
            sleep(5)
        self._set_reg(0x01, virtualAddr | 0x80)
        while (self._get_8bits_reg(0x00) & 0x02) != 0:
            sleep(5)
        self._set_reg(0x01, dataToWrite) 
