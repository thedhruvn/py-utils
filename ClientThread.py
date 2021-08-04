from threading import *
import serial
import queue
from StoppableLoopingThread import StoppableLoopingThread
from ColorLogBase import ColorLogBase

class TCPReceiverThread(StoppableLoopingThread, ColorLogBase):
    def __init__(self,host, port, inQueue, outQueue: queue.Queue(), *args, **kwargs):
        StoppableLoopingThread.__init__(self, *args, **kwargs)
        ColorLogBase.__init__(self)
        self.host = host
        self.port = port
        self.queue = inQueue
        self.out_queue = outQueue
        self.BUFFER_SIZE = 4096 

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            self.log.info("connected to server at" + str(s.getsockname()[0]) + "on port " + str(s.getsockname()[1]))

            while not self.stopped():
                # get next chunk of data from the server
                d = s.recv(BUFFER_SIZE).decode("utf-8").split('/')
                for data in d:
                    if len(data) > 0 and not data[0].isnumeric():
                        # for debugging purposes, we'll display what we received in the window
                        self.log.debug(f"Received: {data}")
                        self.queue.put(data)

                        # # then send back the response from processing the input
                        # response = str(self.parse_input(data) + '/').encode('utf-8')
                        # self.log.debug(response)
                        # s.sendall(response)
                self.queue.join()
                for i in range(0, len(d)):
                    item = self.out_queue.get(block=True)
                    self.log.debug(f"Output {item}")
                    s.sendall(str(item).encode('utf-8'))
                    self.out_queue.task_done()
            


class ClientThread(Thread):
    def __init__(self, bp, rc, vat, laser, host, port):
        Thread.__init__(self)
        self.buildplate = bp
        self.recoaterblade = rc
        self.vat = vat
        self.sensor = laser
        self.host = host
        self.port = port
        self.client = None

    def run(self):
        BUFFER_SIZE = 4096
        #global self.client
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((self.host, self.port))
            print("connected to server at" + str(self.client.getsockname()[0]) + "on port " + str(self.client.getsockname()[1]))

            while True:
                # get next chunk of data from the server
                d = self.client.recv(BUFFER_SIZE).decode("utf-8").split('/')
                for data in d:
                    if len(data) > 0 and not data[0].isnumeric():
                        # for debugging purposes, we'll display what we received in the window
                        print(f"Received: {data}")

                        # then send back the response from processing the input
                        response = str(self.parse_input(data) + '/').encode('utf-8')
                        print(response)
                        self.client.sendall(response)
            self.client.close()

    def parse_input(self, text):
        """
         All command components are separated by a ":"
         All commands are separated by a "/"

         I.e.: To move 1000 steps, "D:1000/"
                                    "{motor addr}:{cmd}:{opt args}/"


        """
        if len(text) != 0:
            parts = text.split(':')
            if len(parts) > 2:
                cmd = parts[1] + parts[2]
            else:
                cmd = parts[1]
            parts[0].strip()
            component = re.search(r"\d", parts[0]).group(0)
            component = component[0]

            if component:
                if int(component) == 1:
                    return self.buildplate.process_command(cmd)
                elif int(component) == 2:
                    return self.recoaterblade.process_command(cmd)
                elif int(component) == 3:
                    return self.vat.process_command(cmd)
                elif int(component) == 4:
                    return sensor.read_curr_value()
                else:
                    return
            else:
                return "Improper command received for component " + component


if __name__ == "__main__":
    host = '127.0.0.1'
    port = 8080
    if len(sys.argv) > 0:
        if len(sys.argv) == 2:
            host = sys.argv[0]
            port = int(sys.argv[1])
        else:
            port = int(sys.argv[0])

    ser = serial.Serial('/dev/ttyUSB0')
    rc = RecoaterMotor(port=ser)
    bp = BuildPlateMotor(port=ser)
    vat = VatMotor(port=ser)
    sensor = LaserSensor()

    controller = ClientThread(bp=bp, rc=rc, vat=vat, laser=sensor, host=host, port=port)
    controller.start()