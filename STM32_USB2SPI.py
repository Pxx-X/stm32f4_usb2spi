import os
import time
from ctypes import *
import binascii
import re
import serial
from serial.tools.list_ports import comports

from queue import Queue
import threading

SPI_SPEED_d2 = 0x01     #2分频42MHz
SPI_SPEED_d4 = 0x02     #4分频21MHz
SPI_SPEED_d8 = 0x03     #8分频10.5MHz
SPI_SPEED_d16 = 0x04    #16分频
SPI_SPEED_d32 = 0x05    #32分频
SPI_SPEED_d64 = 0x06    #64分频
SPI_SPEED_d128 = 0x07   #128分频
SPI_SPEED_d256 = 0x08   #256分频

SPI_MODE_0  = 0x00  #闲时低电平，上升沿触发 #适用amc7836
SPI_MODE_1  = 0x01  #闲时低电平，下降沿触发
SPI_MODE_2  = 0x02  #闲时高电平，上升沿触发
SPI_MODE_3  = 0x03  #闲时高电平，下降沿触发

CS_OPEN = 0x01
CS_CLOSE = 0x00

class STM32_USB2SPI():
    ser = serial.Serial()
    buffer_queue = Queue()
    receive_thread = threading.Thread()

    #初始化,打印所有可用端口，参数1为端口号
    def __init__(self):
        com = ''
        ports_list = list(serial.tools.list_ports.comports())
        if len(ports_list) <= 0:
            print("There are not serial device")
        else:
            print("Available serial device list：")
            for comport in ports_list:
                print(list(comport)[0], list(comport)[1])
                if list(comport)[1].count('STMicroelectronics'):
                    com = list(comport)[0]
                    print("you choose", com)

        self.ser = serial.Serial(com, 115200, timeout=0.5)
        if self.ser.isOpen():
            print("open success")
        else:
            print("open failed")

        self.receive_thread = threading.Thread(target=self.receive_thread)
        self.receive_thread.start()  # 启动接收线程
        time.sleep(1)

    #设置SCLK频率
    def setSpeed(self,speedflag):
        stream = bytearray()
        self.ser.write(bytes([0xfe, speedflag, 0x0d, 0x0a]))
        time.sleep(0.5)
        while not self.buffer_queue.empty():
            data = self.buffer_queue.get()
            if len(data) != 0:
                stream.append(data[0])
        if (stream[0] == 0x01):
            print("setSpeed Succeed")
        else:
            print("setSpeed Error")

    #设置SPI模式,四种模式：
    #模式0：闲时低电平，上升沿触发（适用amc7836） #模式1：闲时低电平，下降沿触发
    # 模式2：闲时高电平，上升沿触发   #模式3：闲时高电平，下降沿触发
    def setMode(self,modeflag):
        stream = bytearray()
        self.ser.write(bytes([0xfd, modeflag, 0x0d, 0x0a]))
        time.sleep(0.5)
        while not self.buffer_queue.empty():
            data = self.buffer_queue.get()
            if len(data) != 0:
                stream.append(data[0])
        if (stream[0] == 0x01):
            print("setMode Succeed")
        else:
            print("setMode Error")

    #设置CS_N端口:三个参数置1为开启，置0为关闭；参数1对应P13(SPI1_NSS,PA4)，参数2对应P8(ADC_IN0,PA0),参数3对应P9(ADC_IN1,PA1)
    def setCS_N(self, cs0, cs1, cs2):
        csflag = 0x00
        if(cs0):
            csflag = csflag + 1
        if (cs1):
            csflag = csflag + 2
        if (cs2):
            csflag = csflag + 4

        self.ser.write(bytes([0xfc, csflag, 0x0d, 0x0a]))

        stream = bytearray()
        time.sleep(0.5)
        while not self.buffer_queue.empty():
            data = self.buffer_queue.get()
            if len(data) != 0:
                stream.append(data[0])
        if (stream[0] == 0x01):
            print("setCS Succeed")
        else:
            print("setCS Error")

    #写寄存器，addr为1byte的地址，data为1byte的数据
    def write(self,addr,data):
        self.ser.write(bytes([0x00, addr, data, 0x0d, 0x0a]))

    #读寄存器，addr为1byte的地址
    def read(self,addr):
        stream = bytearray()
        self.ser.write(bytes([0x01, addr, 0x00, 0x0d, 0x0a]))
        time.sleep(0.01)
        while not self.buffer_queue.empty():
            data = self.buffer_queue.get()
            if len(data) != 0:
                stream.append(data[0])
        return stream.decode('utf-8')

    #关闭串口
    def close(self):
        self.ser.close()

    #用于接受数据的线程
    def receive_thread(self):
        while True:
            data = self.ser.read(1)  # 读取一行数据
            self.buffer_queue.put(data)  # 将数据放入缓冲队列


