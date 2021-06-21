import logging, colorlog

### Logging Configuration ###
globalLogHandler = colorlog.StreamHandler()
globalLogHandler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)s:%(name)s:%(message)s'))
globalOutFileHandler = logging.FileHandler('spam.log')
globalOutFileHandler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))

class ColorLogBase:
    def __init__(self, outHandler: logging.Handler = None, outFileHandler: logging.Handler = None, outLevel = logging.WARNING):
        self.log = colorlog.getLogger(self.__class__.__name__)
        self.log.addHandler(outHandler if outHandler else globalLogHandler)
        self.log.addHandler(outFileHandler if outFileHandler else globalOutFileHandler)
        self.log.setLevel(outLevel)
    
    def updateStreamHandler(self, newHandler: logging.Handler = None):
        if newHandler:
            self.log.handlers = [h for h in self.log.handlers if not isinstance(h, logging.StreamHandler)]
            self.log.addHandler(newHandler)
    
    def updateLevel(self, newLevel: int = logging.DEBUG):
        self.log.setLevel(newLevel)
