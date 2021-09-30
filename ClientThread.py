from threading import *
import re
import queue, socket, time
from StoppableLoopingThread import StoppableLoopingThread
from ColorLogBase import ColorLogBase


class TCPServer(ColorLogBase):

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.outQueue = queue.Queue()
        self.ready_to_send = False
        self.BUFFER_SIZE = 4096
        self.serverThread = StoppableLoopingThread(target=self.__run_server)

    def __run_server(self, stop_event):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((self.host, self.port))
                s.listen(1)
                s.settimeout(2)
                while not stop_event.wait(timeout=0.5):
                    try:
                        conn, client_addr = s.accept()
                    except socket.timeout:
                        continue

                    except socket.error as e:
                        # Something else happened, handle error, exit, etc.
                        self.log.error(f"Error: Try again? {e}")
                        stop_event.set()
                    else:
                        self.log.info(f'Client connected: {client_addr}')
                        self.ready_to_send = True
                        while not stop_event.wait(timeout=0.05):
                            try:
                                item = self.outQueue.get(block=False)
                                self.log.debug(f"Sending: {item}")
                                conn.sendall(str(item).encode('utf-8'))
                                d = conn.recv(self.BUFFER_SIZE)
                                self.log.info(f"received: {d.decode('utf-8')}")
                            except queue.Empty:
                                pass

            except Exception as e:
                self.log.error(f"Aborting TCP Server: {e}")

    def run(self):
        try:
            self.serverThread.start()
            user_input = ''
            while user_input.lower() not in ['quit', 'q']:
                time.sleep(.1)
                user_input = input("Command: ")
                if not self.ready_to_send:
                    self.log.warning("No Client Connected!")
                    continue
                self.outQueue.put(user_input)
                self.log.info(f"added {user_input} to send queue")

        except KeyboardInterrupt:
            self.log.error("Exiting Program...")
        finally:
            self.serverThread.stop()
            self.serverThread.join()


class TCPReceiverThread(StoppableLoopingThread, ColorLogBase):

    def __init__(self, host, port, inQueue: queue.Queue, outQueue: queue.Queue, *args, **kwargs):
        StoppableLoopingThread.__init__(self, *args, **kwargs)
        ColorLogBase.__init__(self)
        self.host = host
        self.port = port
        self.queue = inQueue
        self.out_queue = outQueue
        self.BUFFER_SIZE = 4096 

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(2)
                s.connect((self.host, self.port))
                self.log.info("connected to server at" + str(s.getsockname()[0]) + "on port " + str(s.getsockname()[1]))
            except Exception as e:
                self.log.error(f"Something went wrong with the connection... {e}")
                self.stop()
                return

            msg_received = False
            while not self.stopped() and not msg_received:
                # get next chunk of data from the server
                try:
                    d = s.recv(self.BUFFER_SIZE)
                    msg = d.decode("utf-8").split('/')
                    if len(d) == 0:
                        self.log.info('orderly shutdown on server end')
                        msg_received = True
                    elif len(d) > 0:
                        self.log.info(f"Response: {msg}")
                        for data in msg:
                            if len(data) > 0:
                                # if len(data) > 0 and not data[0].isnumeric():
                                # for debugging purposes, we'll display what we received in the window
                                self.log.debug(f"Received: {data}")
                                self.queue.put(data)

                                # # then send back the response from processing the input
                                # response = str(self.parse_input(data) + '/').encode('utf-8')
                                # self.log.debug(response)
                                # s.sendall(response)
                        self.queue.join()
                        for i in range(0, len(msg)):
                            item = self.out_queue.get(block=True)
                            item = str(item) + "/"
                            self.log.debug(f"Output {item}")
                            s.sendall(str(item).encode('utf-8'))
                            self.out_queue.task_done()
                except socket.timeout as e:
                    err = e.args[0]
                    # this next if/else is a bit redundant, but illustrates how the
                    # timeout exception is setup
                    if err == 'timed out':
                        time.sleep(0.5)
                        #self.log.debug('recv timed out, retry later')
                        continue
                    else:
                        self.log.error(f"Error - timeout error occurred: Try again? {e}")
                        # sys.exit(1)
                        msg_received = False
                except socket.error as e:
                    # Something else happened, handle error, exit, etc.
                    self.log.error(f"Error: Try again? {e}")
                    msg_received = True


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
                    return self.sensor.read_curr_value()
                else:
                    return
            else:
                return "Improper command received for component " + component


