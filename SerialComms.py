import sys, re, serial, time
from util.ColorLogBase import ColorLogBase
from util.CursesBuffers import BaseBuffer

class SerialBuffer(ColorLogBase, BaseBuffer):
    def __init__(self, maxBuf=20, port='/dev/ttyUSB0'):
        BaseBuffer.__init__(self, maxBuf=maxBuf)
        ColorLogBase.__init__(self)
        self.serial = SerialComm(port)

    def handleMessage(self, msg):
        self.__addToBuffer("OUT: " + msg.decode('utf-8'))
        # self.msgBuffer[self.getIdx] = msg
        # self.msgIdx = self.msgIdx + 1
        # self.serial.write(msg)
        output = self.serial.readWrite(msg)
        output = re.sub(r'^[\r\n]+|\.|[\r\n]+$', '', output)
        # output = re.sub(r'[^ \w\.]','',output)
        self.__addToBuffer("IN: " + output)


class StdBuffer(SerialBuffer):
    def __init__(self):
        super().__init__(port=None)

    def write(self, text):
        self.__addToBuffer(text)

    def get_text(self, beg=0, end=1):
        return '\n'.join(self.msgBuffer[beg:end])

import sys
import glob


def sys_serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class SerialComm(ColorLogBase):
    def __init__(self, port='/dev/ttyUSB0', baud=38400):
        super().__init__()
        self.port = port
        self.baud = baud #9600
        self.timeout = 0.5
        self.serialPort = serial.Serial()
        # self.serialPort = serial.Serial(self.port, 9600, timeout=1)

    def readWrite(self, msg: bytes, ending="\r", encoding='utf-8', chars=None):
        try:
            if isinstance(msg, str):
                msg = bytes(f"{msg}", encoding=encoding)
            finString = "ERR"
            with serial.Serial(self.port, self.baud, timeout=self.timeout) as ser:
                outmsg = msg + bytes(f"{ending}", encoding=encoding)
                self.log.debug(f"Sending: {outmsg}")
                ser.write(outmsg)
                time.sleep(0.1)
                readString = b''
                if chars:
                    readString = ser.read(chars)
                else:
                    readString = ser.readline()
                if len(readString) < 1:
                    readString = ser.read(64)
                finString = readString.decode(encoding=encoding)
                # finString = re.sub(r'\W+','',finString)
                # finString = re.sub(r'[^ \w\.]','',finString)
                self.log.debug(f"read: {finString}")

            return finString
        except ValueError as e:
            self.log.error(f"Error with SerialComm readWrite: {e}")
            return "Error - See Logs"
        except serial.SerialException as e:
            self.log.error(f"Error with SerialComm readWrite: {e}")
            return "Error - See Logs"
        except Exception as e:
            self.log.error(f"Error with SerialComm readWrite: {e}")
            return "Error - See Logs"
