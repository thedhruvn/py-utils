from threading import *
import serial

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
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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