# AS726X (AS7262 and AS7263) MicroPython driver v0.7 (26/01/2018)
# By Roberto Colistete Jr. (Roberto.Colistete@Gmail.com)

from micropython import const
from time import sleep_ms
from ustruct import unpack

# I2C address for AS7262 and AS7263
AS726X_I2C_ADDR = const(0x49)

# I2C physical registers
AS726X_SLAVE_STATUS_REG = const(0x00)
AS726X_SLAVE_WRITE_REG = const(0x01)
AS726X_SLAVE_READ_REG = const(0x02)

# I2C virtual registers
AS726X_HW_VERSION = const(0x01)
AS726X_CONTROL_SETUP = const(0x04)
AS726X_INT_T = const(0x05)
AS726X_DEVICE_TEMP = const(0x06)
AS726X_LED_CONTROL = const(0x07)

# Values for Status register
_AS726X_SLAVE_TX_VALID = const(0x02)
_AS726X_SLAVE_RX_VALID = const(0x01)
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

# AS7262 virtual registers
_AS7262_V = const(0x08)
_AS7262_B = const(0x0A)
_AS7262_G = const(0x0C)
_AS7262_Y = const(0x0E)
_AS7262_O = const(0x10)
_AS7262_R = const(0x12)
_AS7262_V_CAL = const(0x14)
_AS7262_B_CAL = const(0x18)
_AS7262_G_CAL = const(0x1C)
_AS7262_Y_CAL = const(0x20)
_AS7262_O_CAL = const(0x24)
_AS7262_R_CAL = const(0x28)

# AS7263 virtual registers
_AS7263_R = const(0x08)
_AS7263_S = const(0x0A)
_AS7263_T = const(0x0C)
_AS7263_U = const(0x0E)
_AS7263_V = const(0x10)
_AS7263_W = const(0x12)
_AS7263_R_CAL = const(0x14)
_AS7263_S_CAL = const(0x18)
_AS7263_T_CAL = const(0x1C)
_AS7263_U_CAL = const(0x20)
_AS7263_V_CAL = const(0x24)
_AS7263_W_CAL = const(0x28)

_POLLING_DELAY = const(5)

def getSensorType(i2c):
    return _virtualReadRegister(i2c, AS726X_HW_VERSION)

# Temperature in C (Celsius scale)
def getTemperature(i2c):
    return _virtualReadRegister(i2c, AS726X_DEVICE_TEMP)

def enableIndicatorLED(i2c):
    _virtualWriteRegister(i2c, AS726X_LED_CONTROL, (_virtualReadRegister(i2c, AS726X_LED_CONTROL) & 0b11111110) | (1 << 0))

def disableIndicatorLED(i2c):
    _virtualWriteRegister(i2c, AS726X_LED_CONTROL, (_virtualReadRegister(i2c, AS726X_LED_CONTROL) & 0b11111110) | (0 << 0))

def setIndicatorLEDCurrent(i2c, current):
    _virtualWriteRegister(i2c, AS726X_LED_CONTROL, (_virtualReadRegister(i2c, AS726X_LED_CONTROL) & 0b11111001) | (current << 1))

def enableBulbLED(i2c):
    _virtualWriteRegister(i2c, AS726X_LED_CONTROL, (_virtualReadRegister(i2c, AS726X_LED_CONTROL) & 0b11110111) | (1 << 3))

def disableBulbLED(i2c):
    _virtualWriteRegister(i2c, AS726X_LED_CONTROL, (_virtualReadRegister(i2c, AS726X_LED_CONTROL) & 0b11110111) | (0 << 3))

def setBulbLEDCurrent(i2c, current):
    _virtualWriteRegister(i2c, AS726X_LED_CONTROL, (_virtualReadRegister(i2c, AS726X_LED_CONTROL) & 0b11001111) | (current << 4))

def setGain(i2c, gain):
    if (gain > AS726X_GAIN_64X):
        gain = AS726X_GAIN_1X
    _virtualWriteRegister(i2c, AS726X_CONTROL_SETUP, (_virtualReadRegister(i2c, AS726X_CONTROL_SETUP) & 0b11001111) | (gain << 4))

def setMeasurementMode(i2c, mode):
    if (mode > AS726X_ONE_SHOT_READING_ALL_CHANNELS):
        mode = AS726X_ONE_SHOT_READING_ALL_CHANNELS
    _virtualWriteRegister(i2c, AS726X_CONTROL_SETUP, (_virtualReadRegister(i2c, AS726X_CONTROL_SETUP) & 0b11110011) | (mode << 2))

def setIntegrationTime(i2c, integrationValue):
    _virtualWriteRegister(i2c, AS726X_INT_T, integrationValue)

def dataAvailable(i2c):
    return (_virtualReadRegister(i2c, AS726X_CONTROL_SETUP) & 0b00000010) == 0b00000010

def clearDataAvailable(i2c):
    _virtualWriteRegister(i2c, AS726X_CONTROL_SETUP, _virtualReadRegister(i2c, AS726X_CONTROL_SETUP) & 0b11111101)

def takeOneShotASynchMeasurement(i2c):
    clearDataAvailable(i2c)
    setMeasurementMode(i2c, AS726X_ONE_SHOT_READING_ALL_CHANNELS)

def takeOneShotSynchMeasurement(i2c):
    clearDataAvailable(i2c)
    pausems = _virtualReadRegister(i2c,AS726X_INT_T)*6
    setMeasurementMode(i2c, AS726X_ONE_SHOT_READING_ALL_CHANNELS)
    sleep_ms(pausems)

def _getChannel(i2c, channelRegister):
    return (_virtualReadRegister(i2c, channelRegister) << 8) | _virtualReadRegister(i2c, channelRegister + 1)

def getViolet(i2c):
    return _getChannel(i2c, _AS7262_V)

def getBlue(i2c):
    return _getChannel(i2c, _AS7262_B)

def getGreen(i2c):
    return _getChannel(i2c, _AS7262_G)

def getYellow(i2c):
    return _getChannel(i2c, _AS7262_Y)

def getOrange(i2c):
    return _getChannel(i2c, _AS7262_O)

def getRed(i2c):
    return _getChannel(i2c, _AS7262_R)

def getR(i2c):
    return _getChannel(i2c, _AS7263_R)

def getS(i2c):
    return _getChannel(i2c, _AS7263_S)

def getT(i2c):
    return _getChannel(i2c, _AS7263_T)

def getU(i2c):
    return _getChannel(i2c, _AS7263_U)

def getV(i2c):
    return _getChannel(i2c, _AS7263_V)

def getW(i2c):
    return _getChannel(i2c, _AS7263_W)

def _getCalibratedValue(i2c, calAddress):
    b0 = _virtualReadRegister(i2c, calAddress + 0)
    b1 = _virtualReadRegister(i2c, calAddress + 1)
    b2 = _virtualReadRegister(i2c, calAddress + 2)
    b3 = _virtualReadRegister(i2c, calAddress + 3)
    return unpack(">f", bytearray([b0, b1, b2, b3]))[0]

def getCalibratedViolet(i2c):
    return _getCalibratedValue(i2c, _AS7262_V_CAL)

def getCalibratedBlue(i2c):
    return _getCalibratedValue(i2c, _AS7262_B_CAL)

def getCalibratedGreen(i2c):
    return _getCalibratedValue(i2c, _AS7262_G_CAL)

def getCalibratedYellow(i2c):
    return _getCalibratedValue(i2c, _AS7262_Y_CAL)

def getCalibratedOrange(i2c):
    return _getCalibratedValue(i2c, _AS7262_O_CAL)

def getCalibratedRed(i2c):
    return _getCalibratedValue(i2c, _AS7262_R_CAL)

def getCalibratedVBGYOR(i2c):
    return getCalibratedViolet(i2c), getCalibratedBlue(i2c), getCalibratedGreen(i2c), getCalibratedYellow(i2c), getCalibratedOrange(i2c), getCalibratedRed(i2c)

def getCalibratedR(i2c):
    return _getCalibratedValue(i2c, _AS7263_R_CAL)

def getCalibratedS(i2c):
    return _getCalibratedValue(i2c, _AS7263_S_CAL)

def getCalibratedT(i2c):
    return _getCalibratedValue(i2c, _AS7263_T_CAL)

def getCalibratedU(i2c):
    return _getCalibratedValue(i2c, _AS7263_U_CAL)

def getCalibratedV(i2c):
    return _getCalibratedValue(i2c, _AS7263_V_CAL)

def getCalibratedW(i2c):
    return _getCalibratedValue(i2c, _AS7263_W_CAL)

def getCalibratedRSTUVW(i2c):
    return getCalibratedR(i2c), getCalibratedS(i2c), getCalibratedT(i2c), getCalibratedU(i2c), getCalibratedV(i2c), getCalibratedW(i2c)

def _virtualReadRegister(i2c, virtualAddr): 
    status = i2c.mem_read(1, AS726X_I2C_ADDR, AS726X_SLAVE_STATUS_REG)
    if (status[0] & _AS726X_SLAVE_RX_VALID) != 0:
        status = i2c.mem_read(1, AS726X_I2C_ADDR, AS726X_SLAVE_READ_REG)
    while (i2c.mem_read(1, AS726X_I2C_ADDR, AS726X_SLAVE_STATUS_REG)[0] & _AS726X_SLAVE_TX_VALID) != 0:
        sleep_ms(_POLLING_DELAY)
    i2c.mem_write(virtualAddr, AS726X_I2C_ADDR, AS726X_SLAVE_WRITE_REG)
    while (i2c.mem_read(1, AS726X_I2C_ADDR, AS726X_SLAVE_STATUS_REG)[0] & _AS726X_SLAVE_RX_VALID) == 0:
        sleep_ms(_POLLING_DELAY)
    return i2c.mem_read(1, AS726X_I2C_ADDR, AS726X_SLAVE_READ_REG)[0]

def _virtualWriteRegister(i2c, virtualAddr, dataToWrite): 
    while (i2c.mem_read(1, AS726X_I2C_ADDR, AS726X_SLAVE_STATUS_REG)[0] & _AS726X_SLAVE_TX_VALID) != 0:
        sleep_ms(_POLLING_DELAY)
    i2c.mem_write(virtualAddr | 0x80, AS726X_I2C_ADDR, AS726X_SLAVE_WRITE_REG)
    while (i2c.mem_read(1, AS726X_I2C_ADDR, AS726X_SLAVE_STATUS_REG)[0] & _AS726X_SLAVE_TX_VALID) != 0:
        sleep_ms(_POLLING_DELAY)
    i2c.mem_write(dataToWrite, AS726X_I2C_ADDR, AS726X_SLAVE_WRITE_REG)
