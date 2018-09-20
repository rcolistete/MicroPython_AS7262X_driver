"""
AS726X (AS7262 and AS7263) MicroPython driver, low memory version, specific for BBC Micro:bit :
https://github.com/rcolistete/MicroPython_AS726x
Version: 0.7.0 (16/06/2018)
"""

from microbit import sleep
from ustruct import unpack


class AS726X:
    
    def __init__(self, i2c, address=0x49):
        self.i2c = i2c
        self.addr = address

    def getSensorType(self):
        return self.readVReg(0x01)

    def getTemperature(self):
        return self.readVReg(0x06)

    def enableIndicatorLED(self, value=True):
        self.writeVReg(7, (self.readVReg(7) & 0b11111110) | (value & 0x01))

    def setIndicatorLEDCurrent(self, current):
        self.writeVReg(7, (self.readVReg(7) & 0b11111001) | ((current & 0x03) << 1))

    def enableBulbLED(self, value=True):
        self.writeVReg(7, (self.readVReg(7) & 0b11110111) | ((value & 0x01) << 3))

    def setBulbLEDCurrent(self, current):
        self.writeVReg(7, (self.readVReg(7) & 0b11001111) | ((current & 0x03) << 4))

    def setGain(self, gain):
        self.writeVReg(4, (self.readVReg(4) & 0b11001111) | ((gain & 0x03) << 4))

    def setMeasurementMode(self, mode):
        self.writeVReg(4, (self.readVReg(4) & 0b11110011) | ((mode & 0x03) << 2))

    def setIntegrationTime(self, integrationValue):
        self.writeVReg(5, integrationValue)

    def dataAvailable(self):
        return (self.readVReg(4) & 0b00000010) == 0b00000010

    def clearDataAvailable(self):
        self.writeVReg(4, self.readVReg(0x04) & 0b11111101)

    def takeOneShotASynchMeasurement(self):
        self.clearDataAvailable()
        self.setMeasurementMode(3)

    def takeOneShotSynchMeasurement(self):
        self.clearDataAvailable()
        pausems = self.readVReg(5)*6
        self.setMeasurementMode(3)
        sleep(pausems)

    def _getCalibratedValue(self, calAddr):
        return unpack(">f", bytearray([self.readVReg(calAddr + 0), self.readVReg(calAddr + 1), self.readVReg(calAddr + 2), self.readVReg(calAddr + 3)]))[0]

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

    def _set_reg(self, reg, data):
        self.i2c.write(self.addr, bytearray([reg, data]))    

    def _get_8bits_reg(self, reg):
        self.i2c.write(self.addr, bytearray([reg]))
        v =	self.i2c.read(self.addr, 1)
        return v[0]
	
    def readVReg(self, vAddr): 
        status = self._get_8bits_reg(0x00)
        if (status & 0x01) != 0:
            status = self._get_8bits_reg(0x00)
        while (self._get_8bits_reg(0x00) & 0x02) != 0:
            sleep(5)
        self._set_reg(0x01, vAddr)
        while (self._get_8bits_reg(0x00) & 0x01) == 0:
            sleep(5)
        return self._get_8bits_reg(0x02)

    def writeVReg(self, vAddr, data): 
        while (self._get_8bits_reg(0x00) & 0x02) != 0:
            sleep(5)
        self._set_reg(0x01, vAddr | 0x80)
        while (self._get_8bits_reg(0x00) & 0x02) != 0:
            sleep(5)
        self._set_reg(0x01, data)
