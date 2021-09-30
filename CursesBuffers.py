import logging, colorlog
import sys, curses
from ColorLogBase import ColorLogBase

class BaseBuffer:
    def __init__(self, maxBuf=20):
        self.__MAXBUF = maxBuf
        self.msgBuffer = []
    
    def __addToBuffer(self, value):
        self.msgBuffer = [value] + self.msgBuffer
        self.msgBuffer = self.msgBuffer[:self.__MAXBUF]


class CursesBufferHandler(logging.Handler, BaseBuffer):
    def __init__(self, curwin, maxbuf = 20, cursesLevel = logging.DEBUG):
        logging.Handler.__init__(self, level=cursesLevel)
        BaseBuffer.__init__(self,maxbuf)
        self.screen = curwin
        self.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)s:%(name)s:%(message)s'))
    
    def emit(self, msg):
        self.__addToBuffer(self.format(msg))
        try:
            idx = 0
            for msg in self.msgBuffer[:self.screen.getmaxyx()[0]-1]:
                msg = msg[:self.screen.getmaxyx()[1] - 2]  # truncate message to fit into the window, even if its a longer string.
                if msg == "":
                    msg = " "
                self.screen.addstr(idx,1,msg)
        except curses.error as e:
            sys.stdout.write("cursesBufferHandler cannot write to Screen")
        except Exception as e:
            sys.stdout.write(f"Other error writing Curses Log: {e}")


