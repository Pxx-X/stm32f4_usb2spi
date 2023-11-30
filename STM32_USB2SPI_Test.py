import time
from STM32_USB2SPI import *

usb2spi = STM32_USB2SPI()

usb2spi.setSpeed(SPI_SPEED_d4)
usb2spi.setMode(SPI_MODE_0)
usb2spi.setCS_N(CS_OPEN, CS_OPEN, CS_OPEN)

print(usb2spi.read(0x05))
print(usb2spi.read(0x04))
print(usb2spi.read(0x06))

for i in range(0,256):
    usb2spi.write(0x15, i)
    print(usb2spi.read(0x15))


#usb2spi.close()