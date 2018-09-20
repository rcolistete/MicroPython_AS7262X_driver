# MicroPython_AS7262X_driver
MicroPython driver for AS7262/AS7263 nano spectrometer sensor

There are specific versions for :
* Pyboard and BBC Micro:bit;
* low memory usage, using less RAM memory.

### Examples using Micro:bit lowmem version, rename the driver to 'as726x.py' and copy it to flash memory.
##### One shot mode (only one measure for each command) :
```python
from microbit import i2c
import as726x
sensor = as726x.AS726X(i2c)
sensor.takeOneShotSynchMeasurement()
```
#### Continuous mode :
```python
from microbit import i2c
import as726x
sensor = as726x.AS726X(i2c)
sensor.getCalibrated6Channels()
sensor.setMeasurementMode(2)
while True:                               
    if sensor.dataAvailable():            
        print(sensor.getCalibrated6Channels())
```
